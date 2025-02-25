
from pydantic import BaseModel, Field
from typing import Optional

class StudentBase(BaseModel):
    last_name: str = Field(..., min_length=1, max_length=255)
    first_name: str = Field(..., min_length=1, max_length=255)
    faculty: str = Field(..., min_length=1, max_length=255)
    course: str = Field(..., min_length=1, max_length=255)
    grade: float = Field(..., ge=0.0, le=100.0)

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    last_name: Optional[str] = Field(None, min_length=1, max_length=255)
    first_name: Optional[str] = Field(None, min_length=1, max_length=255)
    faculty: Optional[str] = Field(None, min_length=1, max_length=255)
    course: Optional[str] = Field(None, min_length=1, max_length=255)
    grade: Optional[float] = Field(None, ge=0.0, le=100.0)

class StudentResponse(StudentBase):
    id: int
    class Config:
        from_attributes = True 
