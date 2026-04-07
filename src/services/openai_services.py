import json
from datetime import datetime, timezone
from typing import Any, Dict

from motor.motor_asyncio import AsyncIOMotorCollection
from openai import AsyncOpenAI

from src.helpers import project_helper
from src.models.project_model import DifficultyLevel


async def enhance_project_with_ai(
    projects_collection: AsyncIOMotorCollection,
    openai_client: AsyncOpenAI,
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

    completion = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a highly skilled web developer specializing in frontend, "
                    "backend, and full-stack applications. Your task is to enhance web "
                    "development projects by refining their features and technology stack "
                    "while maintaining the core idea. The enhancements should be realistic, "
                    "scalable, and follow industry best practices. You MUST strictly follow "
                    "all instructions regarding tech stack composition based on project type. "
                    "NEVER include backend technologies in frontend projects, and NEVER "
                    "include frontend technologies in backend projects. Respond strictly in "
                    "the requested JSON format."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )

    content = completion.choices[0].message.content
    if not content:
        raise ValueError("OpenAI returned an empty response")

    enhanced_data = json.loads(content)

    enhanced_project = {
        "title": project_data["title"],
        "description": enhanced_data["description"],
        "project_type": project_data["project_type"],
        "difficulty": target_difficulty.value,
        "tech_stack": enhanced_data["tech_stack"],
        "new_features": enhanced_data["new_features"],
        "justification": enhanced_data["justification"],
        "original_project_id": project_data.get("_id"),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    result = await projects_collection.insert_one(enhanced_project)
    saved_project = await projects_collection.find_one({"_id": result.inserted_id})

    return project_helper(saved_project)


def create_enhancement_prompt(
    project_data: Dict[str, Any], target_difficulty: DifficultyLevel
) -> str:
    current_difficulty = project_data["difficulty"]
    project_type = project_data["project_type"]

    prompt = f"""
\U0001f6a8 **IMPORTANT: THIS IS A {project_type.upper()} PROJECT - FOLLOW TYPE-SPECIFIC RULES FOR TECH STACK!** \U0001f6a8

I have a {current_difficulty} level web development project that I want to enhance to {target_difficulty.value} difficulty level.

Original Project Details:

Title: {project_data["title"]}

Description: {project_data["description"]}

Project Type: {project_type.upper()} (Frontend, Backend, or Full-Stack)

Tech Stack: {', '.join(project_data["tech_stack"])}

\U0001f680 Enhancement Instructions:

Feature Expansion:
- Improve upon existing features instead of replacing them.
- Introduce additional web-focused features that complement the existing ones.
- Ensure new features are appropriate for the target difficulty level and don't repeat features from lower difficulty levels.

\U0001f534 TECH STACK RULES BASED ON PROJECT TYPE:

- **If this is a FRONTEND project:**
  \u274c DO NOT include ANY backend frameworks (Express, Django, Node.js, FastAPI, Flask, etc.)
  \u274c DO NOT include ANY server technologies or databases
  \u2705 ONLY use frontend frameworks (React, Vue, Angular, Next.js, etc.) and CSS frameworks

- **If this is a BACKEND project:**
  \u274c DO NOT include ANY frontend frameworks (React, Vue, Angular, Next.js, etc.)
  \u2705 ONLY use backend frameworks, languages, and databases

- **If this is a FULLSTACK project:**
  \u2705 Include a coherent combination of frontend and backend technologies
  \u274c DO NOT mix incompatible tech stacks

CRITICAL: The tech stack should STRICTLY INCLUDE ONLY the following types of technologies:
  1. Frontend frameworks (React, Vue, Angular, Next.js, Nuxt.js, Svelte) - ONLY FOR FRONTEND OR FULLSTACK
  2. CSS frameworks (Tailwind CSS, Bootstrap, Material UI) - ONLY FOR FRONTEND OR FULLSTACK
  3. Backend frameworks (Express, Django, FastAPI, Flask, Laravel) - ONLY FOR BACKEND OR FULLSTACK
  4. Programming languages (only if not implied by frameworks)
  5. Databases (MongoDB, PostgreSQL, MySQL, SQLite) - ONLY FOR BACKEND OR FULLSTACK

CRITICAL: The tech stack should NEVER INCLUDE the following (these belong in features instead):
  * Task queues or job processors (Celery, Bull, RabbitMQ)
  * Web servers (Nginx, Apache)
  * Caching systems (Redis, Memcached)
  * Message brokers (Kafka, RabbitMQ)
  * Authentication systems (JWT, OAuth2, Auth0, Passport)
  * Container technologies (Docker, Kubernetes)
  * CI/CD tools (Jenkins, GitHub Actions)
  * Monitoring tools (Prometheus, Grafana)
  * API specifications (GraphQL, RESTful)
  * Specific libraries (Axios, Redux, Lodash)
  * Cloud services (AWS, Azure, GCP)

CRUCIAL: Maintain tech stack coherence and compatibility
  * Choose ONE backend language ecosystem (e.g., Node.js/Express OR Python/Django OR Java/Spring Boot)
  * Do NOT mix incompatible backend frameworks
  * Choose technologies that work well together in real-world scenarios
  * For databases, only include 1-2 that are actually needed

Keep the tech stack focused on 3-5 core technologies for intermediate projects and at most 5 for advanced projects.
Avoid redundancy in the tech stack. For example, if you include Next.js, do not also include React.

Web Development Best Practices:
- Ensure performance optimization techniques are applied.
- Suggest improvements for accessibility (a11y) and responsive design.
- Follow security best practices.

Difficulty-Specific Guidelines:
    """

    if target_difficulty == DifficultyLevel.INTERMEDIATE:
        prompt += """
For Intermediate Level Enhancements:
- Introduce 2-3 additional features to improve user experience (e.g., better UI state management, animations, real-time updates).
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
                [f'"{feature}"' for feature in existing_features]
            )
            prompt += f"""
For Advanced Level Enhancements:
- IMPORTANT: Do NOT repeat these existing intermediate features: {existing_features_text}
- Build upon or extend these features instead of duplicating them.
- Introduce 3-4 new high-complexity features not present at the intermediate level.
- Focus on enterprise-grade capabilities like multi-user roles, dynamic permissions, background jobs, AI-powered recommendations.
- Include advanced authentication mechanisms and role-based access control (RBAC) as features, not tech stack.
- Add features related to scalability, performance monitoring, or advanced security.
- Consider features like microservices architecture, real-time communication, or distributed systems.
            """
        else:
            prompt += """
For Advanced Level Enhancements:
- Introduce 4-5 high-complexity features (e.g., multi-user roles, dynamic permissions, background jobs, AI-powered recommendations).
- Include advanced authentication and role-based access control (RBAC) as features, not tech stack.
- Add features related to state management, microservices, GraphQL, or WebSockets for scalability.
- Include security features (e.g., rate limiting, encryption, OAuth2 flows).
- Consider DevOps-related features like CI/CD pipelines, containerization, and cloud deployment strategies.
            """

    prompt += f"""
\U0001f534 FINAL CRITICAL REMINDER: This is a {project_type.upper()} project. Your tech stack MUST be appropriate for this project type.

- For FRONTEND projects: ONLY include frontend technologies (React, Next.js, Vue, etc.)
- For BACKEND projects: ONLY include backend technologies (Express, Django, etc.)
- For FULLSTACK projects: Include compatible frontend AND backend technologies
"""

    prompt += """
CRITICAL REMINDERS:
1. Authentication systems (JWT, OAuth2, etc.) should be listed as features, not tech stack.
2. Keep tech stack strictly limited to core frameworks, languages, and databases.
3. Don't repeat features across difficulty levels - build upon them instead.
4. Maintain tech stack coherence - don't mix incompatible backend frameworks.
5. Choose technologies that make sense together in real-world projects.
6. The following should NEVER be in the tech stack: Task queues (Celery), Web servers (Nginx), Caching systems (Redis), etc.

TECH STACK FORMAT EXAMPLES:
For a frontend project:
["React", "Tailwind CSS"]

For a backend project:
["FastAPI", "PostgreSQL"] OR ["Node.js", "Express", "MongoDB"]

For a fullstack project:
["React", "Node.js", "Express", "MongoDB"] OR ["Next.js", "PostgreSQL"]

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
