"""
OpenAI services for enhancing projects to different difficulty levels.
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from openai import OpenAI
from src.models.project_model import DifficultyLevel
from src.core import ResourceNotFoundException
from src.helpers import project_helper
from src.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

async def enhance_project_with_ai(
    projects_collection: AsyncIOMotorCollection,
    project_data: Dict[str, Any],
    target_difficulty: DifficultyLevel
) -> Dict[str, Any]:
    """
    Enhance a project to a higher difficulty level using OpenAI.
    
    Args:
        projects_collection: MongoDB collection for projects
        project_data: The original project data to enhance
        target_difficulty: The target difficulty level to enhance to
        
    Returns:
        The enhanced project data
    """
    # Check if an enhanced version already exists in the database
    # Include project_type and tech_stack to ensure uniqueness
    enhanced_project = await projects_collection.find_one({
        "title": project_data["title"],
        "project_type": project_data["project_type"],
        "difficulty": target_difficulty.value,
        "tech_stack": {"$elemMatch": {"$in": project_data["tech_stack"]}}  # At least one matching tech
    })
    
    if enhanced_project:
        return project_helper(enhanced_project)
    
    prompt = create_enhancement_prompt(project_data, target_difficulty)
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a highly skilled web developer with expertise in frontend, backend, and full-stack web applications. Your task is to enhance web development projects by refining their features and technology stack while maintaining the core idea. The enhancements should be realistic, scalable, and follow industry best practices for modern web applications. Respond strictly in the requested JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"}
        )
        
        enhanced_data = json.loads(completion.choices[0].message.content)
        
        # Validate and prepare the enhanced project for saving
        enhanced_project = {
            "title": project_data["title"],  # Keep the same title
            "description": enhanced_data["description"],
            "project_type": project_data["project_type"],  # Keep the same project type
            "difficulty": target_difficulty.value,
            "tech_stack": enhanced_data["tech_stack"],
            "new_features": enhanced_data["new_features"],
            "justification": enhanced_data["justification"],
            "original_project_id": project_data.get("_id"),  # Reference to the original project
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Save the enhanced project to the database
        result = await projects_collection.insert_one(enhanced_project)
        
        # Retrieve the saved project
        saved_project = await projects_collection.find_one({"_id": result.inserted_id})
        
        return project_helper(saved_project)
        
    except Exception as e:
        print(f"Error enhancing project with AI: {str(e)}")
        raise ResourceNotFoundException(
            resource_name="Enhanced Project",
            message="Unable to generate an enhanced version of this project"
        )

def create_enhancement_prompt(project_data: Dict[str, Any], target_difficulty: DifficultyLevel) -> str:
    """
    Creates a prompt for enhancing a project to a higher difficulty level.
    
    Args:
        project_data: The original project data
        target_difficulty: The target difficulty level
        
    Returns:
        A string prompt for the OpenAI API
    """
    current_difficulty = project_data["difficulty"]
    project_type = project_data["project_type"]
    
    prompt = f"""
I have a {current_difficulty} level web development project that I want to enhance to {target_difficulty.value} difficulty level.

Original Project Details:

Title: {project_data["title"]}

Description: {project_data["description"]}

Project Type: {project_type} (Frontend, Backend, or Full-Stack)

Tech Stack: {', '.join(project_data["tech_stack"])}

Enhancement Instructions:

Feature Expansion:
- Improve upon existing features instead of replacing them.
- Introduce additional web-focused features that complement the existing ones.

Tech Stack Evolution:
- CRITICAL: Ensure the tech stack is appropriate for the project type:
  * For FRONTEND projects: Only include frontend frameworks (React, Vue, Angular, etc.), CSS frameworks, and related technologies.
  * For BACKEND projects: Only include backend frameworks (Express, Django, Flask, etc.), databases, and server technologies. DO NOT include frontend frameworks like React.
  * For FULLSTACK projects: Include an appropriate mix of frontend and backend technologies.

- Provide a diverse and varied tech stack that suits the project requirements.
- Be creative and consider many different tech stack combinations (don't default to the same few technologies).
- Consider popular stacks appropriate for the project type, such as:
  * For frontend: React/Next.js, Vue/Nuxt.js, Angular, Svelte/SvelteKit
  * For backend: Express/Node.js, Django/Python, Ruby on Rails, FastAPI, Spring Boot
  * For fullstack: MEAN (MongoDB, Express, Angular, Node.js), MERN (MongoDB, Express, React, Node.js), PERN (PostgreSQL, Express, React, Node.js), FARM (FastAPI, React, MongoDB), LAMP (Linux, Apache, MySQL, PHP)

- IMPORTANT: Only include frameworks, programming languages, and databases in the tech stack. DO NOT include individual libraries or packages (like Axios, NumPy, or SQLite).
- IMPORTANT: Avoid redundancy in the tech stack. For example, if you include Next.js, do not also include React since Next.js is built on React. Similarly, if you include Django, don't also list Python separately.
- For example, good tech stack items are: React OR Next.js (not both), Node.js, PostgreSQL, Django (implies Python), MongoDB, Vue.js, Ruby on Rails, FastAPI, etc.
- When replacing a technology with a more advanced alternative (like React → Next.js), remove the original technology from the list.
- Explain why the new technologies improve performance, scalability, or security.

Web Development Best Practices:
- Ensure performance optimization techniques are applied.
- Suggest improvements for accessibility (a11y) and responsive design.
- Follow security best practices (e.g., CSRF protection, OAuth, etc.).

Difficulty-Specific Guidelines:
    """
    
    if target_difficulty == DifficultyLevel.INTERMEDIATE:
        prompt += """
For Intermediate Level Enhancements:
- Introduce 2-3 additional features to improve user experience (e.g., better UI state management, animations, real-time updates).
- Implement authentication and authorization using JWT or OAuth.
- Suggest database integration (MongoDB, PostgreSQL, etc.) if missing.
- Optimize API performance with caching (Redis) or pagination.
        """
    elif target_difficulty == DifficultyLevel.ADVANCED:
        prompt += """
For Advanced Level Enhancements:
- Introduce 4-5 high-complexity features (e.g., multi-user roles, dynamic permissions, background jobs, AI-powered recommendations).
- Implement full authentication and role-based access control (RBAC).
- Use advanced state management (Redux Toolkit, Zustand, TanStack Query).
- Suggest microservices, GraphQL, or WebSockets for scalability.
- Improve security (e.g., rate limiting, encryption, OAuth2 flows).
- Include DevOps considerations like CI/CD pipelines, containerization (Docker), and cloud deployment strategies.
        """
    
    prompt += """
Please return your response as a JSON object with the following structure:
{
    "description": "Enhanced project description with advanced features.",
    "tech_stack": ["Tech1", "Tech2", "Tech3"],
    "new_features": ["Feature1", "Feature2", "Feature3"],
    "justification": {
        "tech_stack": "Explain why these technologies were added.",
        "features": "Explain how these new features enhance the web project."
    }
}
    """
    
    return prompt
