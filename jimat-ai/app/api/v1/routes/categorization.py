"""Expense categorization API routes"""

import logging
import time
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from app.categorizers import get_categorizer
from app.schemas.categorization import (
    CategorizationRequest,
    CategorizationResponse,
    CategorizationHealthResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/categorization",
    tags=["categorization"],
    responses={
        400: {"description": "Invalid request"},
        500: {"description": "Server error"}
    }
)


@router.post(
    "/categorize",
    response_model=CategorizationResponse,
    summary="Categorize an expense",
    description="Categorize an expense into a category using LLM with keyword fallback"
)
def categorize_expense(request: CategorizationRequest) -> CategorizationResponse:
    """
    Categorize an expense based on its description and optional metadata.
    
    - **description**: Expense description (required)
    - **amount**: Expense amount (optional)
    - **date**: Transaction date (optional)
    - **user_id**: User ID for personalization (optional)
    
    Returns category with confidence score and alternatives.
    """
    start_time = time.time()
    
    try:
        logger.info(f"Categorizing expense: '{request.description}'")
        
        # Get categorizer
        categorizer = get_categorizer()
        
        # Perform categorization
        result = categorizer.categorize(
            description=request.description,
            amount=request.amount,
            date=request.date,
            user_id=request.user_id
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        logger.info(
            f"Expense categorized as '{result.category}' "
            f"(confidence: {result.confidence:.2f}, time: {processing_time}ms)"
        )
        
        return CategorizationResponse(
            success=True,
            category=result.category,
            confidence=result.confidence,
            explanation=result.explanation,
            alternatives=result.alternatives,
            metadata=result.metadata,
            processing_time_ms=processing_time,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Categorization error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Categorization failed: {str(e)}"
        )


@router.get(
    "/health",
    response_model=CategorizationHealthResponse,
    summary="Categorizer health check",
    description="Check if categorizer is ready"
)
def categorizer_health() -> CategorizationHealthResponse:
    """Check if categorizer is initialized and ready"""
    try:
        categorizer = get_categorizer()
        
        return CategorizationHealthResponse(
            status="healthy",
            categorizer="HuggingFace",
            available=categorizer.is_available(),
            supported_categories=categorizer.get_supported_categories(),
            fallback_method="keyword"
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Categorizer health check failed"
        )


@router.post(
    "/batch-categorize",
    summary="Batch categorize expenses",
    description="Categorize multiple expenses at once"
)
def batch_categorize(requests: list[CategorizationRequest]) -> dict:
    """
    Categorize multiple expenses in a single request.
    
    Returns a list of categorization results.
    """
    start_time = time.time()
    
    try:
        if not requests:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one expense required"
            )
        
        if len(requests) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 100 expenses per batch"
            )
        
        categorizer = get_categorizer()
        results = []
        
        for req in requests:
            result = categorizer.categorize(
                description=req.description,
                amount=req.amount,
                date=req.date,
                user_id=req.user_id
            )
            
            results.append({
                "description": req.description,
                "category": result.category,
                "confidence": result.confidence,
                "alternatives": result.alternatives
            })
        
        processing_time = int((time.time() - start_time) * 1000)
        
        logger.info(f"Batch categorized {len(results)} expenses in {processing_time}ms")
        
        return {
            "success": True,
            "total": len(results),
            "results": results,
            "processing_time_ms": processing_time,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch categorization error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch categorization failed: {str(e)}"
        )


@router.get(
    "/categories",
    summary="Get supported categories",
    description="Get list of all supported expense categories"
)
def get_categories() -> dict:
    """Get list of supported expense categories"""
    try:
        categorizer = get_categorizer()
        categories = categorizer.get_supported_categories()
        
        return {
            "success": True,
            "categories": categories,
            "total": len(categories)
        }
    except Exception as e:
        logger.error(f"Failed to get categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve categories"
        )
