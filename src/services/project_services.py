import random
from typing import Any, Dict, List, Optional

from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from openai import AsyncOpenAI

from src.core import ResourceNotFoundException
from src.helpers import project_helper
from src.models.project_model import DifficultyLevel, ProjectType
from src.services.openai_services import enhance_project_with_ai


async def generate_random_project(
    projects_collection: AsyncIOMotorCollection,
    project_type: ProjectType,
    difficulty: DifficultyLevel,
    excluded_titles: Optional[List[str]] = None,
) -> Dict[str, Any]:
    query: Dict[str, Any] = {
        "project_type": project_type.value,
        "difficulty": difficulty.value,
    }

    if excluded_titles:
        query["title"] = {"$nin": excluded_titles}

    count = await projects_collection.count_documents(query)

    if count == 0:
        if excluded_titles:
            fallback_query = {
                "project_type": project_type.value,
                "difficulty": difficulty.value,
            }
            fallback_count = await projects_collection.count_documents(fallback_query)

            if fallback_count > 0:
                random_index = random.randint(0, fallback_count - 1)
                cursor = projects_collection.find(fallback_query).skip(random_index).limit(1)
                project = await cursor.next()
                return project_helper(project)

        raise ResourceNotFoundException(
            resource_name="Projects",
            message="No projects found matching the selected criteria",
        )

    random_index = random.randint(0, count - 1)
    cursor = projects_collection.find(query).skip(random_index).limit(1)

    project = await cursor.next()
    return project_helper(project)


async def find_project_by_title_and_difficulty(
    projects_collection: AsyncIOMotorCollection,
    title: str,
    difficulty: DifficultyLevel,
) -> Optional[Dict[str, Any]]:
    query = {
        "title": title,
        "difficulty": difficulty.value,
    }

    project = await projects_collection.find_one(query)

    if project:
        return project_helper(project)
    return None


async def enhance_project(
    projects_collection: AsyncIOMotorCollection,
    openai_client: AsyncOpenAI,
    title: str,
    target_difficulty: DifficultyLevel,
    current_difficulty: Optional[DifficultyLevel] = None,
) -> Dict[str, Any]:
    enhanced_project = await find_project_by_title_and_difficulty(
        projects_collection=projects_collection,
        title=title,
        difficulty=target_difficulty,
    )

    if enhanced_project:
        return enhanced_project

    if current_difficulty is None:
        if target_difficulty == DifficultyLevel.INTERMEDIATE:
            current_difficulty = DifficultyLevel.BEGINNER
        elif target_difficulty == DifficultyLevel.ADVANCED:
            current_difficulty = DifficultyLevel.INTERMEDIATE
        else:
            raise ValueError(f"Cannot determine source difficulty for target '{target_difficulty.value}'")

    current_project = await find_project_by_title_and_difficulty(
        projects_collection=projects_collection,
        title=title,
        difficulty=current_difficulty,
    )

    if not current_project:
        raise ResourceNotFoundException(
            resource_name="Project",
            message=f"Original project with title '{title}' and difficulty '{current_difficulty.value}' not found",
        )

    return await enhance_project_with_ai(
        projects_collection=projects_collection,
        openai_client=openai_client,
        project_data=current_project,
        target_difficulty=target_difficulty,
    )


async def create_new_project(
    projects_collection: AsyncIOMotorCollection,
    project_data: Dict[str, Any],
) -> Dict[str, Any]:
    result = await projects_collection.insert_one(project_data)
    new_project = await projects_collection.find_one({"_id": result.inserted_id})
    return project_helper(new_project)


async def delete_project(
    projects_collection: AsyncIOMotorCollection,
    project_id: str,
) -> Dict[str, Any]:
    project = await projects_collection.find_one({"_id": ObjectId(project_id)})
    if project is None:
        raise ResourceNotFoundException(
            resource_name="Project",
            message=f"Project with ID {project_id} not found",
        )

    await projects_collection.delete_one({"_id": ObjectId(project_id)})
    return {"id": project_id}
