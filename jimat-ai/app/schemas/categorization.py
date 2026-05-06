"""Schemas for categorization API"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class CategorizationRequest(BaseModel):
    """Request model for expense categorization"""
    description: str = Field(..., min_length=1, description="Expense description")
    amount: Optional[float] = Field(None, ge=0, description="Expense amount")
    date: Optional[str] = Field(None, description="Transaction date")
    user_id: Optional[str] = Field(None, description="User ID for personalization")
    
    class Config:
        json_schema_extra = {
            "example": {
                "description": "Starbucks coffee and pastry",
                "amount": 12.50,
                "date": "2024-05-05",
                "user_id": "user-123"
            }
        }


class CategorizationResponse(BaseModel):
    """Response model for categorization"""
    success: bool = Field(True, description="Whether categorization was successful")
    category: str = Field(..., description="Primary category")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    explanation: str = Field(..., description="Why this category was chosen")
    alternatives: List[str] = Field(default_factory=list, description="Alternative categories")
    metadata: Dict = Field(default_factory=dict, description="Additional metadata")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    timestamp: str = Field(..., description="ISO timestamp")


class CategorizationHealthResponse(BaseModel):
    """Health check response for categorizer"""
    status: str = Field(..., description="Health status")
    categorizer: str = Field(..., description="Categorizer type")
    available: bool = Field(..., description="Whether categorizer is operational")
    supported_categories: List[str] = Field(..., description="List of supported categories")
    fallback_method: str = Field(default="keyword", description="Fallback categorization method")
