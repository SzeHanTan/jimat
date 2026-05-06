"""Document processing module for OCR and text extraction"""

import base64
import re
import logging
from typing import Tuple, Optional, Literal
from abc import ABC, abstractmethod
from pathlib import Path
from io import BytesIO

from PIL import Image, ImageEnhance, ImageOps
import numpy as np

logger = logging.getLogger(__name__)


class BaseDocumentProcessor(ABC):
    """Abstract base class for document processors"""
    
    @abstractmethod
    async def extract_text(self, image_data: bytes) -> Tuple[str, float]:
        """
        Extract text from image.
        
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        pass


class TesseractProcessor(BaseDocumentProcessor):
    """OCR processor using Tesseract via pytesseract"""
    
    def __init__(self):
        """Initialize Tesseract processor"""
        try:
            import pytesseract
            self.pytesseract = pytesseract
            logger.info("Tesseract processor initialized")
        except ImportError:
            logger.warning("pytesseract not available. Tesseract OCR will not work.")
            self.pytesseract = None
    
    async def extract_text(self, image_data: bytes) -> Tuple[str, float]:
        """Extract text from image using Tesseract"""
        if not self.pytesseract:
            return "", 0.0
        
        try:
            # Open image
            image = Image.open(BytesIO(image_data))
            
            # Preprocess image
            processed_image = self._preprocess_image(image)
            
            # Extract text with confidence
            data = self.pytesseract.image_to_data(processed_image, output_type=self.pytesseract.Output.DICT)
            
            text = " ".join(data.get("text", []))
            confidences = [int(conf) for conf in data.get("conf", []) if int(conf) > 0]
            
            # Calculate average confidence
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            confidence_score = avg_confidence / 100.0  # Normalize to 0-1
            
            # Clean extracted text
            cleaned_text = self._clean_text(text)
            
            logger.info(f"Extracted {len(cleaned_text)} characters with confidence {confidence_score:.2f}")
            
            return cleaned_text, confidence_score
            
        except Exception as e:
            logger.error(f"Tesseract extraction error: {str(e)}")
            return "", 0.0
    
    @staticmethod
    def _preprocess_image(image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR accuracy"""
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
        
        # Resize if too small
        if image.width < 200 or image.height < 200:
            scale = max(200 / image.width, 200 / image.height)
            new_size = (int(image.width * scale), int(image.height * scale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2)
        
        return image
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean extracted text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that are likely OCR errors
        # Keep: alphanumeric, currency symbols, common punctuation
        text = re.sub(r'[^\w\s\$₹€£¥₨.,\-:/@\(\)&]', '', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text


class DocumentProcessor:
    """Main document processor with fallback strategies"""
    
    def __init__(self):
        """Initialize document processor"""
        self.tesseract = TesseractProcessor()
        logger.info("DocumentProcessor initialized")
    
    def extract_text_from_image(self, image_base64: str) -> Tuple[str, float]:
        """
        Extract text from base64-encoded image.
        
        Args:
            image_base64: Base64-encoded image data
        
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        try:
            # Decode base64
            image_data = base64.b64decode(image_base64)
            
            # Try Tesseract (synchronous)
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            text, confidence = loop.run_until_complete(self.tesseract.extract_text(image_data))
            
            if text:
                return text, confidence
            
            # Fallback: return empty with low confidence
            logger.warning("No text extracted from image")
            return "", 0.0
            
        except Exception as e:
            logger.error(f"Image decoding error: {str(e)}")
            return "", 0.0
    
    def detect_document_type(self, text: str) -> Literal["receipt", "invoice", "manual_entry"]:
        """
        Detect document type from extracted text.
        
        Returns:
            Document type: "receipt", "invoice", or "manual_entry"
        """
        text_lower = text.lower()
        
        # Receipt indicators
        receipt_keywords = ["receipt", "cashier", "total", "payment", "thank you", "change", "item"]
        receipt_score = sum(1 for kw in receipt_keywords if kw in text_lower)
        
        # Invoice indicators
        invoice_keywords = ["invoice", "bill", "customer", "due date", "amount due", "account"]
        invoice_score = sum(1 for kw in invoice_keywords if kw in text_lower)
        
        # Determine type
        if receipt_score > invoice_score:
            return "receipt"
        elif invoice_score > 0:
            return "invoice"
        else:
            return "manual_entry"
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize extracted text for further processing.
        
        Removes duplicates, standardizes formatting, etc.
        """
        # Remove duplicate lines
        lines = text.split('\n')
        unique_lines = []
        seen = set()
        
        for line in lines:
            line_stripped = line.strip()
            if line_stripped and line_stripped not in seen:
                unique_lines.append(line_stripped)
                seen.add(line_stripped)
        
        return '\n'.join(unique_lines)
    
    def extract_amount(self, text: str) -> Optional[float]:
        """
        Extract monetary amount from text.
        
        Returns:
            Extracted amount or None
        """
        # Regex patterns for amounts
        patterns = [
            r'total[:\s]+([₹$€£¥₨]?\s*[\d,]+\.?\d*)',  # Total: $50.00
            r'([₹$€£¥₨]\s*[\d,]+\.?\d*)',  # $50.00
            r'([\d,]+\.?\d*\s*(?:rupees|dollars|pounds|euros))',  # 50.00 rupees
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1)
                # Remove currency symbols and commas
                amount_str = re.sub(r'[^\d.]', '', amount_str)
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        return None
    
    def extract_date(self, text: str) -> Optional[str]:
        """
        Extract date from text.
        
        Returns:
            Extracted date string or None
        """
        # Common date patterns (most specific first)
        date_patterns = [
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',    # YYYY-MM-DD (priority: 4-digit year first)
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # DD/MM/YYYY or MM/DD/YYYY
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}[,]?\s+\d{4}',  # Jan 15, 2024
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None


# Global processor instance
_processor_instance: Optional[DocumentProcessor] = None


def get_document_processor() -> DocumentProcessor:
    """Get or create global document processor instance"""
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = DocumentProcessor()
    return _processor_instance
