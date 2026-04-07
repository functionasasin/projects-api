from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from motor.motor_asyncio import AsyncIOMotorClient

from src.config import get_settings
from src.core import (
    EmptyContentException,
    InvalidIDException,
    ProjectAccessDeniedException,
    ResourceNotFoundException,
    empty_content_exception_handler,
    general_exception_handler,
    http_exception_handler,
    invalid_id_exception_handler,
    project_access_denied_exception_handler,
    resource_not_found_exception_handler,
    validation_exception_handler,
)
from src.middleware import add_cors_middleware
from src.routes import projects_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.db_name]
    app.state.db_client = client
    app.state.db = db

    print(f"Connected to MongoDB database: {settings.db_name}")
    yield

    print("Shutting down MongoDB connection...")
    client.close()


app = FastAPI(
    title="Project Generator API",
    description="API for generating portfolio project ideas",
    version="1.0.0",
    lifespan=lifespan,
)

add_cors_middleware(app)

# General exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, general_exception_handler)

# Custom exception handlers
app.add_exception_handler(ResourceNotFoundException, resource_not_found_exception_handler)
app.add_exception_handler(EmptyContentException, empty_content_exception_handler)
app.add_exception_handler(InvalidIDException, invalid_id_exception_handler)
app.add_exception_handler(ProjectAccessDeniedException, project_access_denied_exception_handler)

app.include_router(projects_router)


@app.get(
    "/health",
    tags=["health"],
    summary="Health check endpoint",
    description="Used for monitoring the application health status",
)
async def health_check():
    return {"status": "ok"}


@app.get("/")
def read_root():
    return {
        "app": "Project Generator API",
        "version": "1.0.0",
        "documentation": "/docs",
    }
