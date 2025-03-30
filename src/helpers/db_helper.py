from bson import ObjectId
from typing import Dict
from datetime import datetime

def project_helper(project) -> dict:
    """
    Helper function to convert MongoDB project document to a response dictionary
    """
    if not project:
        return None
        
    return {
        "_id": str(project["_id"]),
        "title": project["title"],
        "description": project["description"],
        "project_type": project["project_type"],
        "difficulty": project["difficulty"],
        "tech_stack": project.get("tech_stack", []),
        "features": project.get("features", []),
        "new_features": project.get("new_features", []),
        "justification": project.get("justification", {}),
        "created_at": project.get("created_at").isoformat() if project.get("created_at") else None,
        "updated_at": project.get("updated_at").isoformat() if project.get("updated_at") else None
    } 