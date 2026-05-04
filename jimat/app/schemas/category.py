"""
Pydantic schemas for Category validation and serialization.

Why multiple schemas for one entity:
- CategoryCreate: Only has 'name' and 'color' (what user sends in POST request)
- CategoryUpdate: All fields optional (for PUT requests)
- CategoryResponse: Has all fields including 'id' and 'created_at' (what API returns)
- This enforces validation and prevents unintended data exposure
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CategoryCreate(BaseModel):
    """Schema for creating a new category (POST request body)"""
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(default="#6366F1", min_length=7, max_length=7)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Food",
                "color": "#FF5733"
            }
        }


class CategoryUpdate(BaseModel):
    """Schema for updating a category (PUT request body) - all fields optional"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")  # Hex color validation
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Food Updated",
                "color": "#FF0000"
            }
        }


class CategoryResponse(BaseModel):
    """Schema for returning category (GET response)"""
    id: int
    name: str
    color: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Allow reading from SQLAlchemy model (ORM mode)
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Food",
                "color": "#FF5733",
                "created_at": "2025-05-01T10:00:00",
                "updated_at": "2025-05-01T10:00:00"
            }
        }
