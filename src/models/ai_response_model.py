from typing import List

from pydantic import BaseModel


class EnhancementJustification(BaseModel):
    tech_stack: str
    features: str


class EnhancedProjectResponse(BaseModel):
    description: str
    tech_stack: List[str]
    new_features: List[str]
    justification: EnhancementJustification
