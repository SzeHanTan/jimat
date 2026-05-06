"""Pydantic schemas for document processing"""

from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict, Any
from datetime import datetime


class DocumentAnalyzeRequest(BaseModel):
    """Request body for document analysis endpoint"""
    
    content_type: Literal["image", "text"] = Field(
        ...,
        description="Type of content: 'image' (base64) or 'text' (plain text)"
    )
    content: str = Field(
        ...,
        description="Base64-encoded image or plain text string"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata (e.g., user_id, source)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "content_type": "image",
                "content": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                "metadata": {"user_id": "user-123"}
            }
        }


class DocumentAnalyzeResponse(BaseModel):
    """Response body for document analysis endpoint"""
    
    success: bool = Field(
        ...,
        description="Whether analysis was successful"
    )
    raw_text: str = Field(
        ...,
        description="Raw extracted text from document"
    )
    normalized_text: str = Field(
        ...,
        description="Cleaned and normalized text"
    )
    document_type: Literal["receipt", "invoice", "manual_entry"] = Field(
        ...,
        description="Detected document type"
    )
    ocr_confidence: float = Field(
        ...,
        description="OCR confidence score (0-1)"
    )
    extracted_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extracted metadata (amount, date, etc.)"
    )
    processing_time_ms: int = Field(
        ...,
        description="Time taken to process document"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Processing timestamp"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "raw_text": "Starbucks Receipt Total: $12.50 Date: 05/05/2024",
                "normalized_text": "Starbucks Receipt Total: $12.50 Date: 05/05/2024",
                "document_type": "receipt",
                "ocr_confidence": 0.92,
                "extracted_metadata": {
                    "amount": 12.50,
                    "date": "05/05/2024",
                    "store_name": "Starbucks"
                },
                "processing_time_ms": 245,
                "timestamp": "2024-05-05T12:30:45Z"
            }
        }


class TextNormalizeRequest(BaseModel):
    """Request to normalize text"""
    
    text: str = Field(
        ...,
        description="Text to normalize"
    )


class TextNormalizeResponse(BaseModel):
    """Response from text normalization"""
    
    original_text: str
    normalized_text: str
    lines_deduplicated: int
    processing_time_ms: int
