import os
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from dotenv import load_dotenv

load_dotenv()

class CustomCORSMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, allowed_origins=None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["*"]

    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin", "")
        
        if request.method == "OPTIONS":
            response = Response(status_code=200)
            self._set_cors_headers(response, origin)
            return response
        
        response = await call_next(request)
        
        self._set_cors_headers(response, origin)
        
        return response
    
    def _set_cors_headers(self, response: Response, origin: str):
        if origin in self.allowed_origins or "*" in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
        else:
            response.headers["Access-Control-Allow-Origin"] = self.allowed_origins[0]
        
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, X-API-Key"
        response.headers["Access-Control-Max-Age"] = "600"  # 10 minutes

def add_cors_middleware(app: FastAPI) -> None:
    """
    Add CORS middleware to the FastAPI application.
    
    Args:
        app: The FastAPI application instance
    """
    origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
    
    if "localhost" not in origins_str:
        origins_str += ",http://localhost:5173"
    
    origins = [origin.strip() for origin in origins_str.split(",")]
    origins = [origin[:-1] if origin.endswith("/") else origin for origin in origins]
    
    if not origins:
        origins = ["*"]
    
    print(f"Cors setup with origins: {origins}")
    
    app.add_middleware(CustomCORSMiddleware, allowed_origins=origins) 