from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from src.config import MONGODB_URL, DB_NAME
from src.routes import projects_router
from src.middleware import add_cors_middleware
from src.core import (
    ResourceNotFoundException,
    EmptyContentException,
    InvalidIDException,
    ProjectAccessDeniedException,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    resource_not_found_exception_handler,
    empty_content_exception_handler,
    invalid_id_exception_handler,
    project_access_denied_exception_handler
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    app.state.db_client = client
    app.state.db = db
    
    print(f"Connected to MongoDB database: {DB_NAME}")
    yield
    
    print("Shutting down MongoDB connection...")
    client.close()

app = FastAPI(
    title="Project Generator API",
    description="API for generating portfolio project ideas",
    version="1.0.0",
    lifespan=lifespan
)

add_cors_middleware(app)

# General exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Custom exception handlers
app.add_exception_handler(ResourceNotFoundException, resource_not_found_exception_handler)
app.add_exception_handler(EmptyContentException, empty_content_exception_handler)
app.add_exception_handler(InvalidIDException, invalid_id_exception_handler)
app.add_exception_handler(ProjectAccessDeniedException, project_access_denied_exception_handler)

app.include_router(projects_router)

@app.get("/")
def read_root():
    return {
        "app": "Project Generator API",
        "version": "1.0.0",
        "documentation": "/docs"
    }