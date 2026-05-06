"""Document processing API routes"""

import logging
import time
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from app.processors.document import get_document_processor
from app.schemas.document import (
    DocumentAnalyzeRequest,
    DocumentAnalyzeResponse,
    TextNormalizeRequest,
    TextNormalizeResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/documents",
    tags=["documents"],
    responses={
        400: {"description": "Invalid request"},
        500: {"description": "Server error"}
    }
)


@router.post(
    "/analyze",
    response_model=DocumentAnalyzeResponse,
    summary="Analyze document (OCR or text)",
    description="Extract text from image or normalize provided text"
)
def analyze_document(request: DocumentAnalyzeRequest) -> DocumentAnalyzeResponse:
    """
    Analyze a document by extracting text via OCR or normalizing provided text.
    
    - **content_type**: "image" for base64-encoded image, "text" for plain text
    - **content**: Image data (base64) or text string
    - **metadata**: Optional metadata for tracking
    
    Returns extracted text, document type, confidence score, and processing time.
    """
    start_time = time.time()
    
    try:
        processor = get_document_processor()
        
        if request.content_type == "image":
            # OCR processing
            logger.info("Processing image document")
            raw_text, ocr_confidence = processor.extract_text_from_image(request.content)
            
            if not raw_text:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not extract text from image. Image may be blank or unreadable."
                )
        
        elif request.content_type == "text":
            # Text normalization
            logger.info("Processing text document")
            raw_text = request.content
            ocr_confidence = 1.0  # Full confidence for manually entered text
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid content_type: {request.content_type}. Use 'image' or 'text'."
            )
        
        # Normalize text
        normalized_text = processor.normalize_text(raw_text)
        
        # Detect document type
        document_type = processor.detect_document_type(normalized_text)
        
        # Extract metadata
        extracted_metadata = {
            "amount": processor.extract_amount(normalized_text),
            "date": processor.extract_date(normalized_text),
        }
        
        # Remove None values
        extracted_metadata = {k: v for k, v in extracted_metadata.items() if v is not None}
        
        processing_time = int((time.time() - start_time) * 1000)
        
        logger.info(
            f"Document analysis complete: "
            f"type={document_type}, confidence={ocr_confidence:.2f}, time={processing_time}ms"
        )
        
        return DocumentAnalyzeResponse(
            success=True,
            raw_text=raw_text,
            normalized_text=normalized_text,
            document_type=document_type,
            ocr_confidence=ocr_confidence,
            extracted_metadata=extracted_metadata,
            processing_time_ms=processing_time,
            timestamp=datetime.utcnow()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document analysis error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document analysis failed: {str(e)}"
        )


@router.post(
    "/normalize-text",
    response_model=TextNormalizeResponse,
    summary="Normalize text",
    description="Clean and deduplicate text"
)
def normalize_text(request: TextNormalizeRequest) -> TextNormalizeResponse:
    """
    Normalize and clean text by removing duplicates and extra whitespace.
    """
    start_time = time.time()
    
    try:
        processor = get_document_processor()
        
        original_text = request.text
        normalized_text = processor.normalize_text(original_text)
        
        # Count deduplicated lines
        original_lines = len(original_text.split('\n'))
        normalized_lines = len(normalized_text.split('\n'))
        lines_deduplicated = original_lines - normalized_lines
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return TextNormalizeResponse(
            original_text=original_text,
            normalized_text=normalized_text,
            lines_deduplicated=lines_deduplicated,
            processing_time_ms=processing_time
        )
    
    except Exception as e:
        logger.error(f"Text normalization error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text normalization failed: {str(e)}"
        )


@router.get(
    "/health",
    summary="Document processor health check",
    description="Check if document processor is ready"
)
def document_processor_health():
    """Check if document processor is initialized and ready"""
    try:
        processor = get_document_processor()
        return {
            "status": "healthy",
            "service": "Document Processor",
            "features": {
                "ocr": processor.tesseract.pytesseract is not None,
                "text_normalization": True,
                "document_type_detection": True,
                "metadata_extraction": True
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document processor health check failed"
        )
