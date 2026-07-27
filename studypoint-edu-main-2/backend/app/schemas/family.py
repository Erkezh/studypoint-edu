from pydantic import BaseModel, Field

class FamilyAddChildRequest(BaseModel):
    name: str = Field(..., min_length=2)
    grade_level: int = Field(..., ge=1, le=12)

class FamilyAddChildResponse(BaseModel):
    id: str
    name: str
    username: str
    grade_level: int
