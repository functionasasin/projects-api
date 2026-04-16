from fastapi import APIRouter, Body, Depends, Query
from fastapi_limiter.depends import RateLimiter
from pyrate_limiter import Duration, Limiter, Rate

from src.core import HTTPStatusCodes, InvalidIDException, get_api_key
from src.dependencies import GeminiClient, ProjectsCollection
from src.helpers import create_error_response, create_success_response
from src.models import DifficultyLevel, Project, ProjectBase, ProjectType, SuccessResponse
from src.services import create_new_project, delete_project, enhance_project, generate_random_project

router = APIRouter(prefix="/projects", tags=["projects"])

_generate_limiter = RateLimiter(limiter=Limiter(Rate(10, Duration.MINUTE)))
_enhance_limiter = RateLimiter(limiter=Limiter(Rate(5, Duration.MINUTE)))


@router.get(
    "/generate",
    dependencies=[Depends(_generate_limiter)],
    response_model=SuccessResponse,
    response_description="Generate a project idea based on filters",
    responses={
        200: {
            "description": "Project successfully generated",
            "content": {
                "application/json": {
                    "example": {
                        "status": "Success",
                        "message": "Project generated successfully",
                        "data": {
                            "_id": "5f9d88b7b54764e8a5a77f3c",
                            "title": "Portfolio Website",
                            "description": "A responsive portfolio website using React and Tailwind CSS with dark mode support",
                            "project_type": "frontend",
                            "difficulty": "beginner",
                            "tech_stack": ["React", "Tailwind CSS", "Vite"],
                            "created_at": "2023-03-15T12:30:45.123Z",
                            "updated_at": "2023-03-15T12:30:45.123Z",
                        },
                    }
                }
            },
        }
    },
)
async def generate_project_route(
    projects_collection: ProjectsCollection,
    project_type: ProjectType = Query(..., description="Project type (frontend, backend, fullstack)"),
    exclude_titles: str = Query(None, description="Comma-separated list of project titles to exclude"),
):
    excluded_titles = []
    if exclude_titles:
        excluded_titles = [title.strip() for title in exclude_titles.split(",") if title.strip()]

    project = await generate_random_project(
        projects_collection=projects_collection,
        project_type=project_type,
        difficulty=DifficultyLevel.BEGINNER,
        excluded_titles=excluded_titles,
    )

    return create_success_response(
        data=project,
        message="Project generated successfully",
    )


@router.get(
    "/enhance",
    dependencies=[Depends(_enhance_limiter)],
    response_model=SuccessResponse,
    response_description="Enhance a project to a higher difficulty level",
    responses={
        200: {
            "description": "Project successfully enhanced",
            "content": {
                "application/json": {
                    "example": {
                        "status": "Success",
                        "message": "Project enhanced successfully",
                        "data": {
                            "_id": "5f9d88b7b54764e8a5a77f3d",
                            "title": "Portfolio Website",
                            "description": "A responsive portfolio website using React, Redux and Tailwind CSS with dark mode support and authentication",
                            "project_type": "frontend",
                            "difficulty": "intermediate",
                            "tech_stack": ["React", "Redux", "Tailwind CSS", "Vite", "Firebase Auth"],
                            "new_features": [
                                "User authentication and authorization",
                                "Real-time collaboration",
                                "Category and reminder support",
                            ],
                            "justification": {
                                "tech_stack": "Redux provides better state management for complex UIs, while Firebase Auth enables secure user authentication.",
                                "features": "Authentication enables personalized experiences, while real-time collaboration allows multiple users to work together.",
                            },
                            "created_at": "2023-03-15T12:30:45.123Z",
                            "updated_at": "2023-03-15T12:30:45.123Z",
                        },
                    }
                }
            },
        },
        400: {
            "description": "Invalid enhancement request",
            "content": {
                "application/json": {
                    "example": {
                        "status": "Error",
                        "message": "Cannot skip difficulty levels. Must enhance to intermediate before advanced.",
                        "error_code": "INVALID_ENHANCEMENT_REQUEST",
                        "details": None,
                    }
                }
            },
        },
        404: {
            "description": "Enhanced version not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "Error",
                        "message": "No enhanced version available for this project",
                        "error_code": "RESOURCE_NOT_FOUND",
                        "details": None,
                    }
                }
            },
        },
    },
)
async def enhance_project_route(
    projects_collection: ProjectsCollection,
    gemini_client: GeminiClient,
    title: str = Query(..., description="Title of the project to enhance"),
    current_difficulty: DifficultyLevel = Query(..., description="Current difficulty level of the project"),
    target_difficulty: DifficultyLevel = Query(
        ...,
        description="Target difficulty level (intermediate, advanced)",
        include_in_schema=True,
    ),
):
    if current_difficulty == DifficultyLevel.BEGINNER and target_difficulty == DifficultyLevel.ADVANCED:
        return create_error_response(
            error_code="INVALID_ENHANCEMENT_REQUEST",
            message="Cannot skip difficulty levels. Must enhance to intermediate before advanced.",
            status_code=400,
        )

    enhanced_project = await enhance_project(
        projects_collection=projects_collection,
        gemini_client=gemini_client,
        title=title,
        target_difficulty=target_difficulty,
        current_difficulty=current_difficulty,
    )

    return create_success_response(
        data=enhanced_project,
        message="Project enhanced successfully",
    )


@router.post(
    "/create",
    response_model=SuccessResponse,
    response_description="Add a new project",
    responses={
        201: {
            "description": "Project successfully created",
            "content": {
                "application/json": {
                    "example": {
                        "status": "Success",
                        "message": "Project created successfully",
                        "data": {
                            "_id": "5f9d88b7b54764e8a5a77f3c",
                            "title": "Portfolio Website",
                            "description": "A responsive portfolio website using React and Tailwind CSS with dark mode support",
                            "project_type": "frontend",
                            "difficulty": "beginner",
                            "tech_stack": ["React", "Tailwind CSS", "Vite"],
                            "features": ["Responsive design", "Dark mode", "Contact form", "Project showcase"],
                            "created_at": "2023-03-15T12:30:45.123Z",
                            "updated_at": "2023-03-15T12:30:45.123Z",
                        },
                    }
                }
            },
        },
        401: {
            "description": "API Key header not found",
            "content": {
                "application/json": {
                    "example": {"detail": "API Key header not found"}
                }
            },
        },
        403: {
            "description": "Invalid API Key",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid API Key"}
                }
            },
        },
    },
)
async def create_project_route(
    projects_collection: ProjectsCollection,
    project_data: ProjectBase = Body(
        ...,
        examples=[
            {
                "title": "Portfolio Website",
                "description": "A responsive portfolio website using React and Tailwind CSS with dark mode support",
                "project_type": "frontend",
                "difficulty": "beginner",
                "tech_stack": ["React", "Tailwind CSS", "Vite"],
                "features": ["Responsive design", "Dark mode", "Contact form", "Project showcase"],
            }
        ],
    ),
    api_key: str = Depends(get_api_key),
):
    project = Project(
        title=project_data.title,
        description=project_data.description,
        project_type=project_data.project_type,
        difficulty=project_data.difficulty,
        tech_stack=project_data.tech_stack,
        features=project_data.features,
    )

    project_dict = project.model_dump(exclude={"id"})

    new_project = await create_new_project(
        projects_collection=projects_collection,
        project_data=project_dict,
    )

    return create_success_response(
        data=new_project,
        message="Project created successfully",
        status_code=HTTPStatusCodes.CREATED.value,
    )


@router.delete(
    "/delete/{id}",
    response_model=SuccessResponse,
    response_description="Delete a project",
    responses={
        200: {
            "description": "Project successfully deleted",
            "content": {
                "application/json": {
                    "example": {
                        "status": "Success",
                        "message": "Project deleted successfully",
                        "data": {"id": "5f9d88b7b54764e8a5a77f3c"},
                    }
                }
            },
        },
        401: {
            "description": "API Key header not found",
            "content": {
                "application/json": {
                    "example": {"detail": "API Key header not found"}
                }
            },
        },
        403: {
            "description": "Invalid API Key",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid API Key"}
                }
            },
        },
    },
)
async def delete_project_route(
    projects_collection: ProjectsCollection,
    id: str,
    api_key: str = Depends(get_api_key),
):
    try:
        result = await delete_project(
            projects_collection=projects_collection,
            project_id=id,
        )

        return create_success_response(
            message="Project deleted successfully",
            data=result,
        )
    except Exception as e:
        if "Invalid ObjectId" in str(e):
            raise InvalidIDException()
        raise
