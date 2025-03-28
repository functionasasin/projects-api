from fastapi import Security, HTTPException, status, Depends
from fastapi.security.api_key import APIKeyHeader
from src.config import API_KEY
from typing import Optional

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: Optional[str] = Security(api_key_header)):
    """
    Dependency that checks if the API key is valid.
    This is used to protect admin-only endpoints.
    """
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key header not found"
        )
        
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
        
    return api_key 