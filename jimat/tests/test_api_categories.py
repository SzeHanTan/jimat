"""
Tests for Category API endpoints.

This file tests all Category-related endpoints:
- POST /api/v1/categories (create)
- GET /api/v1/categories (read all)
- GET /api/v1/categories/{id} (read one)
- PUT /api/v1/categories/{id} (update)
- DELETE /api/v1/categories/{id} (delete)
"""

import pytest
from fastapi.testclient import TestClient


class TestCreateCategory:
    """Test POST /api/v1/categories"""
    
    def test_create_category_success(self, client: TestClient):
        """Test creating a category with valid data"""
        response = client.post(
            "/api/v1/categories",
            json={"name": "Food", "color": "#FF5733"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Food"
        assert data["color"] == "#FF5733"
        assert data["id"] == 1
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_category_with_default_color(self, client: TestClient):
        """Test creating a category with default color"""
        response = client.post(
            "/api/v1/categories",
            json={"name": "Transport"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Transport"
        assert data["color"] == "#6366F1"  # Default color
    
    def test_create_category_missing_name(self, client: TestClient):
        """Test creating a category without name (should fail)"""
        response = client.post(
            "/api/v1/categories",
            json={"color": "#FF5733"}
        )
        assert response.status_code == 422  # Validation error
    
    def test_create_category_empty_name(self, client: TestClient):
        """Test creating a category with empty name (should fail)"""
        response = client.post(
            "/api/v1/categories",
            json={"name": "", "color": "#FF5733"}
        )
        assert response.status_code == 422  # Validation error
    
    def test_create_category_name_too_long(self, client: TestClient):
        """Test creating a category with name > 50 chars"""
        long_name = "A" * 51
        response = client.post(
            "/api/v1/categories",
            json={"name": long_name, "color": "#FF5733"}
        )
        assert response.status_code == 422  # Validation error


class TestGetCategories:
    """Test GET /api/v1/categories"""
    
    def test_get_empty_categories(self, client: TestClient):
        """Test getting categories when none exist"""
        response = client.get("/api/v1/categories")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_all_categories(self, client: TestClient):
        """Test getting all categories after creating some"""
        # Create two categories
        client.post("/api/v1/categories", json={"name": "Food", "color": "#FF5733"})
        client.post("/api/v1/categories", json={"name": "Transport", "color": "#00FF00"})
        
        # Get all
        response = client.get("/api/v1/categories")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Food"
        assert data[1]["name"] == "Transport"


class TestGetCategory:
    """Test GET /api/v1/categories/{category_id}"""
    
    def test_get_category_success(self, client: TestClient):
        """Test getting a specific category"""
        # Create a category
        client.post("/api/v1/categories", json={"name": "Food", "color": "#FF5733"})
        
        # Get it
        response = client.get("/api/v1/categories/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Food"
        assert data["color"] == "#FF5733"
    
    def test_get_category_not_found(self, client: TestClient):
        """Test getting a category that doesn't exist"""
        response = client.get("/api/v1/categories/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_category_invalid_id(self, client: TestClient):
        """Test getting a category with invalid ID format"""
        response = client.get("/api/v1/categories/invalid")
        assert response.status_code == 422  # Validation error


class TestUpdateCategory:
    """Test PUT /api/v1/categories/{category_id}"""
    
    def test_update_category_name(self, client: TestClient):
        """Test updating category name only"""
        # Create a category
        client.post("/api/v1/categories", json={"name": "Food", "color": "#FF5733"})
        
        # Update name
        response = client.put(
            "/api/v1/categories/1",
            json={"name": "Food Updated"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Food Updated"
        assert data["color"] == "#FF5733"  # Should remain unchanged
    
    def test_update_category_color(self, client: TestClient):
        """Test updating category color only"""
        # Create a category
        client.post("/api/v1/categories", json={"name": "Food", "color": "#FF5733"})
        
        # Update color
        response = client.put(
            "/api/v1/categories/1",
            json={"color": "#00FF00"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Food"  # Should remain unchanged
        assert data["color"] == "#00FF00"
    
    def test_update_category_both(self, client: TestClient):
        """Test updating both name and color"""
        # Create a category
        client.post("/api/v1/categories", json={"name": "Food", "color": "#FF5733"})
        
        # Update both
        response = client.put(
            "/api/v1/categories/1",
            json={"name": "Transport", "color": "#0000FF"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Transport"
        assert data["color"] == "#0000FF"
    
    def test_update_category_not_found(self, client: TestClient):
        """Test updating a category that doesn't exist"""
        response = client.put(
            "/api/v1/categories/999",
            json={"name": "New Name"}
        )
        assert response.status_code == 404
    
    def test_update_category_empty_body(self, client: TestClient):
        """Test updating a category with empty body (should work - all optional)"""
        # Create a category
        client.post("/api/v1/categories", json={"name": "Food", "color": "#FF5733"})
        
        # Update with empty body
        response = client.put(
            "/api/v1/categories/1",
            json={}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Food"  # Unchanged
        assert data["color"] == "#FF5733"  # Unchanged


class TestDeleteCategory:
    """Test DELETE /api/v1/categories/{category_id}"""
    
    def test_delete_category_success(self, client: TestClient):
        """Test deleting an existing category"""
        # Create a category
        client.post("/api/v1/categories", json={"name": "Food", "color": "#FF5733"})
        
        # Delete it
        response = client.delete("/api/v1/categories/1")
        assert response.status_code == 204
        
        # Verify it's gone
        response = client.get("/api/v1/categories/1")
        assert response.status_code == 404
    
    def test_delete_category_not_found(self, client: TestClient):
        """Test deleting a category that doesn't exist"""
        response = client.delete("/api/v1/categories/999")
        assert response.status_code == 404
    
    def test_delete_category_twice(self, client: TestClient):
        """Test deleting the same category twice"""
        # Create a category
        client.post("/api/v1/categories", json={"name": "Food", "color": "#FF5733"})
        
        # Delete it
        response = client.delete("/api/v1/categories/1")
        assert response.status_code == 204
        
        # Try to delete again
        response = client.delete("/api/v1/categories/1")
        assert response.status_code == 404
