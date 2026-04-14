from datetime import datetime, timezone
from typing import Any, Dict

from google import genai
from google.genai import types
from motor.motor_asyncio import AsyncIOMotorCollection

from src.helpers import project_helper
from src.models.ai_response_model import EnhancedProjectResponse
from src.models.project_model import DifficultyLevel

SYSTEM_INSTRUCTION = (
    "You are a highly skilled web developer specializing in frontend, backend, and full-stack "
    "applications. Your task is to enhance web development projects by refining their features "
    "and technology stack while maintaining the core idea. Enhancements should be realistic, "
    "scalable, and follow industry best practices. Strictly follow all rules regarding tech "
    "stack composition based on project type."
)


async def enhance_project_with_ai(
    projects_collection: AsyncIOMotorCollection,
    gemini_client: genai.Client,
    project_data: Dict[str, Any],
    target_difficulty: DifficultyLevel,
) -> Dict[str, Any]:
    # Check if an enhanced version already exists in the database
    enhanced_project = await projects_collection.find_one(
        {
            "title": project_data["title"],
            "project_type": project_data["project_type"],
            "difficulty": target_difficulty.value,
            "tech_stack": {"$elemMatch": {"$in": project_data["tech_stack"]}},
        }
    )

    if enhanced_project:
        return project_helper(enhanced_project)

    prompt = create_enhancement_prompt(project_data, target_difficulty)

    response = await gemini_client.aio.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=EnhancedProjectResponse,
        ),
    )

    if response.parsed is None:
        raise ValueError("Gemini returned no parsed content")

    enhanced_data: EnhancedProjectResponse = response.parsed

    new_project = {
        "title": project_data["title"],
        "description": enhanced_data.description,
        "project_type": project_data["project_type"],
        "difficulty": target_difficulty.value,
        "tech_stack": enhanced_data.tech_stack,
        "new_features": enhanced_data.new_features,
        "justification": {
            "tech_stack": enhanced_data.justification.tech_stack,
            "features": enhanced_data.justification.features,
        },
        "original_project_id": project_data.get("_id"),
        "created_at": (now := datetime.now(timezone.utc)),
        "updated_at": now,
    }

    result = await projects_collection.insert_one(new_project)
    saved_project = await projects_collection.find_one({"_id": result.inserted_id})

    return project_helper(saved_project)


def create_enhancement_prompt(
    project_data: Dict[str, Any], target_difficulty: DifficultyLevel
) -> str:
    current_difficulty = project_data["difficulty"]
    project_type = project_data["project_type"]

    prompt = f"""# Task
Enhance a {current_difficulty} level {project_type} project to {target_difficulty.value} difficulty.

# Project
- Title: {project_data["title"]}
- Description: {project_data["description"]}
- Type: {project_type.upper()}
- Current tech stack: {", ".join(project_data["tech_stack"])}

# Tech Stack Rules

## Allowed by project type
- Frontend: only frontend frameworks (React, Vue, Angular, Next.js, Nuxt.js, Svelte) and CSS frameworks (Tailwind CSS, Bootstrap, Material UI). No backend frameworks or databases.
- Backend: only backend frameworks (Express, Django, FastAPI, Flask, Laravel), languages, and databases. No frontend frameworks.
- Fullstack: a coherent combination of frontend and backend technologies. No incompatible mixes.

## Never include in tech_stack (put these in features instead)
- Task queues or job processors (Celery, Bull, RabbitMQ)
- Web servers (Nginx, Apache)
- Caching systems (Redis, Memcached)
- Message brokers (Kafka)
- Authentication systems (JWT, OAuth2, Auth0, Passport)
- Container technologies (Docker, Kubernetes)
- CI/CD tools (Jenkins, GitHub Actions)
- Monitoring tools (Prometheus, Grafana)
- API specifications (GraphQL, RESTful)
- Specific libraries (Axios, Redux, Lodash)
- Cloud services (AWS, Azure, GCP)

## Coherence
- Choose one backend language ecosystem (e.g., Node.js/Express OR Python/Django — not both).
- No redundant frameworks (e.g., if Next.js is included, do not also include React).
- Include 3–5 technologies total for intermediate; at most 5 for advanced.
"""

    prompt += "\n# Feature Guidance\n"

    if target_difficulty == DifficultyLevel.INTERMEDIATE:
        prompt += """
## Intermediate enhancements
- Introduce 2–3 additional features that improve user experience (e.g., better UI state management, animations, real-time updates).
- Include authentication and authorization (JWT, OAuth) as a feature, not as tech stack.
- Suggest database integration if missing.
- Add features like caching or pagination for better performance.
"""
    elif target_difficulty == DifficultyLevel.ADVANCED:
        if (
            current_difficulty == DifficultyLevel.INTERMEDIATE
            and "new_features" in project_data
        ):
            existing_features = project_data.get("new_features", [])
            existing_features_text = ", ".join(
                [f'"{f}"' for f in existing_features]
            )
            prompt += f"""
## Advanced enhancements
- Do NOT repeat these existing intermediate features: {existing_features_text}
- Build upon or extend these features instead of duplicating them.
- Introduce 3–4 new high-complexity features not present at the intermediate level.
- Focus on enterprise-grade capabilities: multi-user roles, dynamic permissions, background jobs, AI-powered recommendations.
- Include advanced authentication mechanisms and RBAC as features, not tech stack.
- Add features related to scalability, performance monitoring, or advanced security.
"""
        else:
            prompt += """
## Advanced enhancements
- Introduce 4–5 high-complexity features (e.g., multi-user roles, dynamic permissions, background jobs, AI-powered recommendations).
- Include advanced authentication and RBAC as features, not tech stack.
- Add features related to state management, microservices, or WebSockets for scalability.
- Include security features (rate limiting, encryption, OAuth2 flows).
"""

    prompt += f"""
# Output Requirements
- Improve upon existing features; do not replace them.
- Apply performance, accessibility (a11y), and security best practices.
- This is a {project_type.upper()} project — tech stack must strictly match the allowed types above.
"""

    return prompt
