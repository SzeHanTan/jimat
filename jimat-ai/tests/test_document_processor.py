"""Tests for document processor module"""

import pytest
from app.processors.document import (
    DocumentProcessor,
    get_document_processor,
    TesseractProcessor
)


class TestDocumentProcessor:
    """Test DocumentProcessor class"""
    
    @pytest.fixture
    def processor(self):
        """Create a document processor instance"""
        return DocumentProcessor()
    
    def test_processor_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None
        assert hasattr(processor, 'tesseract')
    
    def test_normalize_text_removes_duplicates(self, processor, duplicate_text):
        """Test text normalization removes duplicate lines"""
        normalized = processor.normalize_text(duplicate_text)
        lines = normalized.split('\n')
        
        # Should have 3 unique lines
        assert len(lines) == 3
        assert "Line 1" in lines
        assert "Line 2" in lines
        assert "Line 3" in lines
    
    def test_normalize_text_removes_empty_lines(self, processor):
        """Test normalization removes empty lines"""
        text_with_empty = "Line 1\n\n\nLine 2\n\nLine 3"
        normalized = processor.normalize_text(text_with_empty)
        
        assert "\n\n" not in normalized
        assert normalized.count('\n') == 2  # Only 2 newlines between 3 lines
    
    def test_detect_document_type_receipt(self, processor, sample_receipt_text):
        """Test receipt document type detection"""
        doc_type = processor.detect_document_type(sample_receipt_text)
        assert doc_type == "receipt"
    
    def test_detect_document_type_invoice(self, processor, sample_invoice_text):
        """Test invoice document type detection"""
        doc_type = processor.detect_document_type(sample_invoice_text)
        assert doc_type == "invoice"
    
    def test_detect_document_type_manual_entry(self, processor, sample_manual_entry_text):
        """Test manual entry document type detection"""
        doc_type = processor.detect_document_type(sample_manual_entry_text)
        assert doc_type == "manual_entry"
    
    def test_extract_amount_with_currency_symbol(self, processor):
        """Test amount extraction with currency symbol"""
        text = "Total: $12.50"
        amount = processor.extract_amount(text)
        assert amount == 12.50
    
    def test_extract_amount_with_rupees(self, processor):
        """Test amount extraction with rupees symbol"""
        text = "Amount: ₹500"
        amount = processor.extract_amount(text)
        assert amount == 500.0
    
    def test_extract_amount_with_comma(self, processor):
        """Test amount extraction with comma separator"""
        text = "Total: $1,250.50"
        amount = processor.extract_amount(text)
        assert amount == 1250.50
    
    def test_extract_amount_not_found(self, processor):
        """Test amount extraction when no amount present"""
        text = "Just some random text"
        amount = processor.extract_amount(text)
        assert amount is None
    
    def test_extract_date_dd_mm_yyyy(self, processor):
        """Test date extraction in DD/MM/YYYY format"""
        text = "Date: 05/05/2024"
        date = processor.extract_date(text)
        assert date == "05/05/2024"
    
    def test_extract_date_yyyy_mm_dd(self, processor):
        """Test date extraction in YYYY-MM-DD format"""
        text = "Purchase date: 2024-05-05"
        date = processor.extract_date(text)
        assert date == "2024-05-05"
    
    def test_extract_date_long_format(self, processor):
        """Test date extraction in long format"""
        text = "May 5, 2024"
        date = processor.extract_date(text)
        assert "May" in date or "05" in date
    
    def test_extract_date_not_found(self, processor):
        """Test date extraction when no date present"""
        text = "No date information here"
        date = processor.extract_date(text)
        assert date is None
    
    def test_extract_text_from_image_invalid_base64(self, processor):
        """Test extraction with invalid base64 returns empty"""
        text, confidence = processor.extract_text_from_image("not-valid-base64!!!")
        assert text == ""
        assert confidence == 0.0


class TestTesseractProcessor:
    """Test TesseractProcessor class"""
    
    @pytest.fixture
    def tesseract_processor(self):
        """Create a Tesseract processor instance"""
        return TesseractProcessor()
    
    def test_tesseract_initialization(self, tesseract_processor):
        """Test Tesseract processor initializes"""
        assert tesseract_processor is not None
    
    def test_preprocess_image_grayscale(self, tesseract_processor):
        """Test image preprocessing converts to grayscale"""
        from PIL import Image
        import io
        
        # Create a simple RGB image
        img = Image.new('RGB', (100, 100), color='red')
        
        # Preprocess
        processed = tesseract_processor._preprocess_image(img)
        
        # Should be grayscale
        assert processed.mode == 'L'
    
    def test_clean_text_removes_special_chars(self, tesseract_processor):
        """Test text cleaning removes unwanted special characters but preserves @ for emails"""
        dirty_text = "Hello@#%World***Test"
        clean = tesseract_processor._clean_text(dirty_text)
        
        # @ is preserved for email addresses, but others removed
        assert "@" in clean  # Email symbol preserved
        assert "#" not in clean
        assert "%" not in clean
        assert "*" not in clean
    
    def test_clean_text_preserves_currency(self, tesseract_processor):
        """Test cleaning preserves currency symbols"""
        text = "Price: $100 or ₹5000"
        clean = tesseract_processor._clean_text(text)
        
        assert "$" in clean
        assert "₹" in clean


class TestDocumentProcessorGlobal:
    """Test global processor instance"""
    
    def test_get_document_processor_singleton(self):
        """Test get_document_processor returns singleton"""
        processor1 = get_document_processor()
        processor2 = get_document_processor()
        
        assert processor1 is processor2
    
    def test_processor_has_required_methods(self):
        """Test processor has all required methods"""
        processor = get_document_processor()
        
        assert hasattr(processor, 'extract_text_from_image')
        assert hasattr(processor, 'detect_document_type')
        assert hasattr(processor, 'normalize_text')
        assert hasattr(processor, 'extract_amount')
        assert hasattr(processor, 'extract_date')


class TestComplexScenarios:
    """Test complex document processing scenarios"""
    
    @pytest.fixture
    def processor(self):
        return DocumentProcessor()
    
    def test_receipt_with_all_metadata(self, processor):
        """Test extraction of all metadata from complete receipt"""
        receipt = "Starbucks\nCoffee $4.50\nTotal: $4.50\nDate: 05/05/2024\nThank you!"
        
        # Detect type
        doc_type = processor.detect_document_type(receipt)
        assert doc_type == "receipt"
        
        # Extract amount
        amount = processor.extract_amount(receipt)
        assert amount == 4.50
        
        # Extract date
        date = processor.extract_date(receipt)
        assert date == "05/05/2024"
    
    def test_multiline_normalization_with_duplicates_and_empty_lines(self, processor):
        """Test complex normalization scenario"""
        text = """
        Item 1
        
        Item 2
        Item 1
        
        
        Item 3
        Item 2
        """
        
        normalized = processor.normalize_text(text)
        
        # Should have no extra whitespace
        assert "\n\n" not in normalized
        # Should have only unique items
        assert normalized.count("Item 1") == 1
        assert normalized.count("Item 2") == 1
        assert normalized.count("Item 3") == 1
