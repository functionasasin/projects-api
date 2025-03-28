from bson.objectid import ObjectId
import random
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorCollection
from src.models.project_model import ProjectType, DifficultyLevel
from src.core import ResourceNotFoundException
from src.helpers import project_helper
from src.services.openai_services import enhance_project_with_ai

async def generate_random_project(
    projects_collection: AsyncIOMotorCollection,
    project_type: ProjectType,
    difficulty: DifficultyLevel
) -> Dict[str, Any]:
    """
    Generate a random project based on project type and difficulty level.
    
    Args:
        projects_collection: MongoDB collection for projects
        project_type: Type of project (frontend, backend, fullstack)
        difficulty: Difficulty level (beginner, intermediate, advanced)
    
    Returns:
        A randomly selected project matching the criteria
        
    Raises:
        ResourceNotFoundException: If no projects match the criteria
    """
    query = {
        "project_type": project_type.value,
        "difficulty": difficulty.value
    }
    
    # Count matching projects
    count = await projects_collection.count_documents(query)
    
    if count == 0:
        raise ResourceNotFoundException(
            resource_name="Projects",
            message="No projects found matching the selected criteria"
        )
    
    # Select a random project from the matching ones
    random_index = random.randint(0, count - 1)
    cursor = projects_collection.find(query).skip(random_index).limit(1)
    
    project = await cursor.next()
    return project_helper(project)

async def find_project_by_title_and_difficulty(
    projects_collection: AsyncIOMotorCollection,
    title: str,
    difficulty: DifficultyLevel
) -> Optional[Dict[str, Any]]:
    """
    Find a project by title and difficulty level.
    
    Args:
        projects_collection: MongoDB collection for projects
        title: Title of the project to find
        difficulty: Difficulty level to search for
        
    Returns:
        The project if found, None otherwise
    """
    query = {
        "title": title,
        "difficulty": difficulty.value
    }
    
    project = await projects_collection.find_one(query)
    
    if project:
        return project_helper(project)
    return None

async def enhance_project(
    projects_collection: AsyncIOMotorCollection,
    title: str,
    target_difficulty: DifficultyLevel,
    current_difficulty: DifficultyLevel = None
) -> Dict[str, Any]:
    """
    Enhance a project to a higher difficulty level.
    First tries to find a pre-existing enhanced version in the database.
    If not found, uses AI to generate an enhanced version.
    
    Args:
        projects_collection: MongoDB collection for projects
        title: Title of the project to enhance
        target_difficulty: Target difficulty level to enhance to
        current_difficulty: Current difficulty level of the project (optional)
        
    Returns:
        The enhanced project
        
    Raises:
        ResourceNotFoundException: If enhancement fails
    """
    # First try to find an existing enhanced version
    enhanced_project = await find_project_by_title_and_difficulty(
        projects_collection=projects_collection,
        title=title,
        difficulty=target_difficulty
    )
    
    # If enhanced version exists, return it
    if enhanced_project:
        return enhanced_project
    
    # Otherwise, use AI to generate an enhanced version
    # First, get the current project
    if current_difficulty is None:
        # If not specified, default to finding the project with immediately lower difficulty
        if target_difficulty == DifficultyLevel.INTERMEDIATE:
            current_difficulty = DifficultyLevel.BEGINNER
        elif target_difficulty == DifficultyLevel.ADVANCED:
            current_difficulty = DifficultyLevel.INTERMEDIATE
    
    current_project = await find_project_by_title_and_difficulty(
        projects_collection=projects_collection,
        title=title,
        difficulty=current_difficulty
    )
    
    if not current_project:
        raise ResourceNotFoundException(
            resource_name="Project",
            message=f"Original project with title '{title}' and difficulty '{current_difficulty.value}' not found"
        )
    
    # Use AI to enhance the project
    return await enhance_project_with_ai(
        projects_collection=projects_collection,
        project_data=current_project,
        target_difficulty=target_difficulty
    )

async def create_new_project(
    projects_collection: AsyncIOMotorCollection,
    project_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a new project in the database.
    
    Args:
        projects_collection: MongoDB collection for projects
        project_data: Project data to insert
        
    Returns:
        The newly created project
    """
    result = await projects_collection.insert_one(project_data)
    new_project = await projects_collection.find_one({"_id": result.inserted_id})
    return project_helper(new_project)

async def delete_project(
    projects_collection: AsyncIOMotorCollection,
    project_id: str
) -> Dict[str, Any]:
    """
    Delete a project from the database.
    
    Args:
        projects_collection: MongoDB collection for projects
        project_id: ID of the project to delete
        
    Returns:
        The deleted project ID
        
    Raises:
        ResourceNotFoundException: If the project is not found
    """
    # Check if project exists
    project = await projects_collection.find_one({"_id": ObjectId(project_id)})
    if project is None:
        raise ResourceNotFoundException(
            resource_name="Project", 
            message=f"Project with ID {project_id} not found"
        )
        
    # Delete project
    await projects_collection.delete_one({"_id": ObjectId(project_id)})
    return {"id": project_id}

async def project_exists(
    projects_collection: AsyncIOMotorCollection,
    title: str
) -> bool:
    """
    Check if a project with the given title already exists.
    
    Args:
        projects_collection: MongoDB collection for projects
        title: Project title to check
        
    Returns:
        True if a project with the title exists, False otherwise
    """
    existing_project = await projects_collection.find_one({"title": title})
    return existing_project is not None
