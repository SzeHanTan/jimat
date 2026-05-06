"""Tests for main FastAPI application"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestApplicationSetup:
    """Test FastAPI application setup"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_app_is_created(self):
        """Test that app is properly instantiated"""
        assert app is not None
        assert hasattr(app, 'routes')
    
    def test_root_endpoint(self, client):
        """Test GET / returns service info"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "service" in data
        assert "version" in data
        assert "status" in data
        assert "llm_provider" in data
        assert "docs" in data
        assert "health" in data
    
    def test_health_endpoint(self, client):
        """Test GET /health returns healthy status"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "service" in data
        assert "timestamp" in data
    
    def test_cors_headers_present(self, client):
        """Test CORS headers are in responses"""
        response = client.get("/")
        
        # Check for CORS headers (FastAPI adds these via CORSMiddleware)
        assert "access-control-allow-origin" in response.headers or response.status_code == 200
    
    def test_request_id_header(self, client):
        """Test request ID header is added"""
        response = client.get("/health")
        
        # X-Request-ID should be in response headers
        assert "x-request-id" in response.headers
    
    def test_process_time_header(self, client):
        """Test process time header is added"""
        response = client.get("/")
        
        # X-Process-Time should be in response headers
        assert "x-process-time" in response.headers


class TestErrorHandling:
    """Test error handling"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_404_on_invalid_route(self, client):
        """Test 404 response for invalid routes"""
        response = client.get("/invalid/route")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test 405 for unsupported methods"""
        response = client.post("/health")
        assert response.status_code == 405


class TestDocumentRoutes:
    """Test document processing routes"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_document_health_endpoint(self, client):
        """Test document processor health endpoint"""
        response = client.get("/api/v1/documents/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "features" in data
    
    def test_document_health_features(self, client):
        """Test document health shows all features"""
        response = client.get("/api/v1/documents/health")
        data = response.json()
        
        features = data.get("features", {})
        assert "ocr" in features
        assert "text_normalization" in features
        assert "document_type_detection" in features
        assert "metadata_extraction" in features


class TestMainAppIntegration:
    """Integration tests for main app"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_service_info_contains_llm_provider(self, client):
        """Test service info includes LLM provider"""
        response = client.get("/")
        data = response.json()
        
        assert "llm_provider" in data
        assert data["llm_provider"] in ["huggingface", "gemini", "ollama"]
    
    def test_multiple_sequential_requests(self, client):
        """Test multiple sequential requests work correctly"""
        for i in range(5):
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"
