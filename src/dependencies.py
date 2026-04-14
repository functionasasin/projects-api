from typing import Annotated

from fastapi import Depends, Request
from google import genai
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from src.config import Settings, get_settings


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


def get_projects_collection(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> AsyncIOMotorCollection:
    return db.projects


def get_gemini_client(
    settings: Settings = Depends(get_settings),
) -> genai.Client:
    return genai.Client(api_key=settings.gemini_api_key)


# Reusable type aliases for route signatures
ProjectsCollection = Annotated[AsyncIOMotorCollection, Depends(get_projects_collection)]
GeminiClient = Annotated[genai.Client, Depends(get_gemini_client)]
