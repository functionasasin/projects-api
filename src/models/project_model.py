from enum import Enum
from typing import List, Optional, Annotated, Dict
from pydantic import BaseModel, Field, BeforeValidator
from datetime import datetime, timezone
from bson import ObjectId

def validate_object_id(v):
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str) and ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")

PyObjectId = Annotated[ObjectId, BeforeValidator(validate_object_id)]

class ProjectType(str, Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    FULLSTACK = "fullstack"

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ProjectBase(BaseModel):
    title: str = Field(
        ..., 
        max_length=100, 
        description="The title of the project"
    )
    description: str = Field(
        ..., 
        max_length=1000, 
        description="Detailed description of the project"
    )
    project_type: ProjectType = Field(
        ...,
        description="The type of project (frontend, backend, fullstack)"
    )
    difficulty: DifficultyLevel = Field(
        ...,
        description="The difficulty level of the project"
    )
    tech_stack: List[str] = Field(
        ...,
        description="Technologies used in the project"
    )

class Project(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=ObjectId, alias="_id")
    title: str = Field(max_length=100)
    description: str = Field(max_length=1000)
    project_type: ProjectType
    difficulty: DifficultyLevel
    tech_stack: List[str]
    new_features: Optional[List[str]] = None
    justification: Optional[Dict[str, str]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = {
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "populate_by_name": True
    } 