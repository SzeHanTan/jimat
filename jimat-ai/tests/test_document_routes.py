"""Tests for document API endpoints"""

import pytest
import json
from fastapi.testclient import TestClient
from app.main import app


class TestAnalyzeDocumentEndpoint:
    """Test POST /api/v1/documents/analyze endpoint"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_analyze_text_document_success(self, client):
        """Test successful text document analysis"""
        payload = {
            "content_type": "text",
            "content": "Starbucks Receipt\nTotal: $12.50\nDate: 05/05/2024"
        }
        
        response = client.post("/api/v1/documents/analyze", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "raw_text" in data
        assert "normalized_text" in data
        assert "document_type" in data
        assert "ocr_confidence" in data
        assert data["ocr_confidence"] == 1.0  # Text input has full confidence
    
    def test_analyze_detects_receipt_type(self, client):
        """Test receipt type detection"""
        payload = {
            "content_type": "text",
            "content": "Starbucks\nCoffee $4.50\nTotal: $4.50\nThank you!"
        }
        
        response = client.post("/api/v1/documents/analyze", json=payload)
        data = response.json()
        
        assert data["document_type"] == "receipt"
    
    def test_analyze_detects_invoice_type(self, client):
        """Test invoice type detection"""
        payload = {
            "content_type": "text",
            "content": "Invoice #12345\nCustomer: John\nAmount Due: $150\nDue Date: 05/15/2024"
        }
        
        response = client.post("/api/v1/documents/analyze", json=payload)
        data = response.json()
        
        assert data["document_type"] == "invoice"
    
    def test_analyze_extracts_metadata(self, client):
        """Test metadata extraction (amount, date)"""
        payload = {
            "content_type": "text",
            "content": "Total: $25.99\nDate: 05/05/2024"
        }
        
        response = client.post("/api/v1/documents/analyze", json=payload)
        data = response.json()
        
        assert "extracted_metadata" in data
        assert "amount" in data["extracted_metadata"]
        assert "date" in data["extracted_metadata"]
        assert data["extracted_metadata"]["amount"] == 25.99
        assert data["extracted_metadata"]["date"] == "05/05/2024"
    
    def test_analyze_returns_processing_time(self, client):
        """Test that processing time is returned"""
        payload = {
            "content_type": "text",
            "content": "Sample text"
        }
        
        response = client.post("/api/v1/documents/analyze", json=payload)
        data = response.json()
        
        assert "processing_time_ms" in data
        assert data["processing_time_ms"] >= 0
    
    def test_analyze_invalid_content_type(self, client):
        """Test error on invalid content type"""
        payload = {
            "content_type": "invalid",
            "content": "Some content"
        }
        
        response = client.post("/api/v1/documents/analyze", json=payload)
        
        # FastAPI returns 422 for validation errors on Literal enum fields
        assert response.status_code in [400, 422]
    
    def test_analyze_missing_required_fields(self, client):
        """Test error when required fields missing"""
        payload = {
            "content_type": "text"
            # Missing 'content'
        }
        
        response = client.post("/api/v1/documents/analyze", json=payload)
        
        assert response.status_code == 422  # Validation error
    
    def test_analyze_with_metadata(self, client):
        """Test including metadata in request"""
        payload = {
            "content_type": "text",
            "content": "Receipt from Starbucks",
            "metadata": {"user_id": "user-123", "source": "mobile"}
        }
        
        response = client.post("/api/v1/documents/analyze", json=payload)
        
        assert response.status_code == 200
        assert response.json()["success"] is True
    
    def test_analyze_response_has_timestamp(self, client):
        """Test response includes timestamp"""
        payload = {
            "content_type": "text",
            "content": "Test"
        }
        
        response = client.post("/api/v1/documents/analyze", json=payload)
        data = response.json()
        
        assert "timestamp" in data
        assert data["timestamp"] is not None


class TestNormalizeTextEndpoint:
    """Test POST /api/v1/documents/normalize-text endpoint"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_normalize_text_removes_duplicates(self, client):
        """Test normalization removes duplicate lines"""
        payload = {
            "text": "Line 1\nLine 2\nLine 1\nLine 3"
        }
        
        response = client.post("/api/v1/documents/normalize-text", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "normalized_text" in data
        assert "lines_deduplicated" in data
        assert data["lines_deduplicated"] == 1
        assert data["normalized_text"].count("Line 1") == 1
    
    def test_normalize_text_returns_original(self, client):
        """Test original text is returned"""
        text = "Original Text"
        payload = {"text": text}
        
        response = client.post("/api/v1/documents/normalize-text", json=payload)
        data = response.json()
        
        assert data["original_text"] == text
    
    def test_normalize_text_processing_time(self, client):
        """Test processing time is included"""
        payload = {"text": "Test text"}
        
        response = client.post("/api/v1/documents/normalize-text", json=payload)
        data = response.json()
        
        assert "processing_time_ms" in data
        assert data["processing_time_ms"] >= 0
    
    def test_normalize_complex_text(self, client):
        """Test normalization on complex text with many duplicates"""
        text = "A\nB\nA\nC\nB\nA\nD\nC\nB\nA"
        payload = {"text": text}
        
        response = client.post("/api/v1/documents/normalize-text", json=payload)
        data = response.json()
        
        normalized_lines = data["normalized_text"].split('\n')
        assert len(normalized_lines) == 4  # A, B, C, D
        assert data["lines_deduplicated"] == 6


class TestEndpointErrorHandling:
    """Test error handling in document endpoints"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_analyze_with_empty_text(self, client):
        """Test handling empty text"""
        payload = {
            "content_type": "text",
            "content": ""
        }
        
        response = client.post("/api/v1/documents/analyze", json=payload)
        
        # Should not fail, but might have empty results
        assert response.status_code in [200, 400]
    
    def test_normalize_with_empty_text(self, client):
        """Test normalizing empty text"""
        payload = {"text": ""}
        
        response = client.post("/api/v1/documents/normalize-text", json=payload)
        
        assert response.status_code == 200
    
    def test_analyze_malformed_json(self, client):
        """Test error on malformed JSON"""
        response = client.post(
            "/api/v1/documents/analyze",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in [400, 422]


class TestDocumentEndpointIntegration:
    """Integration tests for document endpoints"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_sequential_analyze_and_normalize(self, client):
        """Test analyzing then normalizing text"""
        # First: analyze
        analyze_payload = {
            "content_type": "text",
            "content": "Item 1\nItem 1\nItem 2"
        }
        analyze_response = client.post("/api/v1/documents/analyze", json=analyze_payload)
        assert analyze_response.status_code == 200
        
        normalized_from_analyze = analyze_response.json()["normalized_text"]
        
        # Second: normalize the already-normalized text
        normalize_payload = {"text": normalized_from_analyze}
        normalize_response = client.post("/api/v1/documents/normalize-text", json=normalize_payload)
        assert normalize_response.status_code == 200
        
        # Should still have the same structure
        final_normalized = normalize_response.json()["normalized_text"]
        assert "Item 1" in final_normalized
        assert "Item 2" in final_normalized
    
    def test_performance_many_requests(self, client):
        """Test performance with multiple concurrent-like requests"""
        for i in range(10):
            payload = {
                "content_type": "text",
                "content": f"Request {i} - Amount: ${i * 10}"
            }
            response = client.post("/api/v1/documents/analyze", json=payload)
            assert response.status_code == 200
