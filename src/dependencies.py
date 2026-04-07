from typing import Annotated

from fastapi import Depends, Request
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from openai import AsyncOpenAI

from src.config import Settings, get_settings


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


def get_projects_collection(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> AsyncIOMotorCollection:
    return db.projects


def get_openai_client(
    settings: Settings = Depends(get_settings),
) -> AsyncOpenAI:
    return AsyncOpenAI(api_key=settings.openai_api_key)


# Reusable type aliases for route signatures
ProjectsCollection = Annotated[AsyncIOMotorCollection, Depends(get_projects_collection)]
OpenAIClient = Annotated[AsyncOpenAI, Depends(get_openai_client)]
