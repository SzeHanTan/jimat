"""
Tests for Expense API endpoints.

This file tests all Expense-related endpoints:
- POST /api/v1/expenses (create)
- GET /api/v1/expenses (read all with pagination)
- GET /api/v1/expenses/{id} (read one)
- PUT /api/v1/expenses/{id} (update)
- DELETE /api/v1/expenses/{id} (delete)
- GET /api/v1/expenses/category/{category_id} (filter by category)
- GET /api/v1/expenses/date-range/search (filter by date range)
"""

import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from decimal import Decimal


@pytest.fixture
def category_id(client: TestClient):
    """Fixture that creates a category and returns its ID"""
    response = client.post(
        "/api/v1/categories",
        json={"name": "Food", "color": "#FF5733"}
    )
    return response.json()["id"]


class TestCreateExpense:
    """Test POST /api/v1/expenses"""
    
    def test_create_expense_success(self, client: TestClient, category_id: int):
        """Test creating an expense with valid data"""
        response = client.post(
            "/api/v1/expenses",
            json={
                "amount": "50.99",
                "description": "Lunch at restaurant",
                "date": "2025-05-01",
                "category_id": category_id
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["description"] == "Lunch at restaurant"
        assert Decimal(str(data["amount"])) == Decimal("50.99")
        assert data["date"] == "2025-05-01"
        assert data["category_id"] == category_id
        assert "id" in data
    
    def test_create_expense_missing_fields(self, client: TestClient, category_id: int):
        """Test creating expense without required fields"""
        # Missing description
        response = client.post(
            "/api/v1/expenses",
            json={
                "amount": "50.00",
                "date": "2025-05-01",
                "category_id": category_id
            }
        )
        assert response.status_code == 422
    
    def test_create_expense_invalid_amount(self, client: TestClient, category_id: int):
        """Test creating expense with invalid amount (negative or zero)"""
        response = client.post(
            "/api/v1/expenses",
            json={
                "amount": "-10.00",
                "description": "Test",
                "date": "2025-05-01",
                "category_id": category_id
            }
        )
        assert response.status_code == 422
    
    def test_create_expense_invalid_category(self, client: TestClient):
        """Test creating expense with non-existent category"""
        response = client.post(
            "/api/v1/expenses",
            json={
                "amount": "50.00",
                "description": "Test",
                "date": "2025-05-01",
                "category_id": 999
            }
        )
        # Should fail due to foreign key constraint
        # FastAPI catches IntegrityError and returns 400 (Bad Request)
        assert response.status_code == 400


class TestGetExpenses:
    """Test GET /api/v1/expenses"""
    
    def test_get_empty_expenses(self, client: TestClient):
        """Test getting expenses when none exist"""
        response = client.get("/api/v1/expenses")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_all_expenses(self, client: TestClient, category_id: int):
        """Test getting all expenses"""
        # Create multiple expenses
        for i in range(3):
            client.post(
                "/api/v1/expenses",
                json={
                    "amount": str(50 + i),
                    "description": f"Expense {i+1}",
                    "date": "2025-05-01",
                    "category_id": category_id
                }
            )
        
        # Get all
        response = client.get("/api/v1/expenses")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
    
    def test_get_expenses_pagination(self, client: TestClient, category_id: int):
        """Test pagination parameters"""
        # Create 5 expenses
        for i in range(5):
            client.post(
                "/api/v1/expenses",
                json={
                    "amount": str(50 + i),
                    "description": f"Expense {i+1}",
                    "date": "2025-05-01",
                    "category_id": category_id
                }
            )
        
        # Get with skip and limit
        response = client.get("/api/v1/expenses?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Should return 2 items (skipped first 2)
    
    def test_get_expenses_invalid_pagination(self, client: TestClient):
        """Test invalid pagination parameters"""
        # Negative skip
        response = client.get("/api/v1/expenses?skip=-1")
        assert response.status_code == 422
        
        # Zero limit
        response = client.get("/api/v1/expenses?limit=0")
        assert response.status_code == 422


class TestGetExpense:
    """Test GET /api/v1/expenses/{expense_id}"""
    
    def test_get_expense_success(self, client: TestClient, category_id: int):
        """Test getting a specific expense"""
        # Create expense
        client.post(
            "/api/v1/expenses",
            json={
                "amount": "75.50",
                "description": "Dinner",
                "date": "2025-05-01",
                "category_id": category_id
            }
        )
        
        # Get it
        response = client.get("/api/v1/expenses/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["description"] == "Dinner"
    
    def test_get_expense_not_found(self, client: TestClient):
        """Test getting an expense that doesn't exist"""
        response = client.get("/api/v1/expenses/999")
        assert response.status_code == 404


class TestUpdateExpense:
    """Test PUT /api/v1/expenses/{expense_id}"""
    
    def test_update_expense_description(self, client: TestClient, category_id: int):
        """Test updating expense description only"""
        # Create expense
        client.post(
            "/api/v1/expenses",
            json={
                "amount": "50.00",
                "description": "Lunch",
                "date": "2025-05-01",
                "category_id": category_id
            }
        )
        
        # Update description
        response = client.put(
            "/api/v1/expenses/1",
            json={"description": "Lunch Updated"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Lunch Updated"
        assert Decimal(str(data["amount"])) == Decimal("50.00")  # Unchanged
    
    def test_update_expense_amount(self, client: TestClient, category_id: int):
        """Test updating expense amount only"""
        # Create expense
        client.post(
            "/api/v1/expenses",
            json={
                "amount": "50.00",
                "description": "Lunch",
                "date": "2025-05-01",
                "category_id": category_id
            }
        )
        
        # Update amount
        response = client.put(
            "/api/v1/expenses/1",
            json={"amount": "60.00"}
        )
        assert response.status_code == 200
        data = response.json()
        assert Decimal(str(data["amount"])) == Decimal("60.00")
        assert data["description"] == "Lunch"  # Unchanged
    
    def test_update_expense_not_found(self, client: TestClient):
        """Test updating an expense that doesn't exist"""
        response = client.put(
            "/api/v1/expenses/999",
            json={"description": "New"}
        )
        assert response.status_code == 404


class TestDeleteExpense:
    """Test DELETE /api/v1/expenses/{expense_id}"""
    
    def test_delete_expense_success(self, client: TestClient, category_id: int):
        """Test deleting an existing expense"""
        # Create expense
        client.post(
            "/api/v1/expenses",
            json={
                "amount": "50.00",
                "description": "Lunch",
                "date": "2025-05-01",
                "category_id": category_id
            }
        )
        
        # Delete it
        response = client.delete("/api/v1/expenses/1")
        assert response.status_code == 204
        
        # Verify it's gone
        response = client.get("/api/v1/expenses/1")
        assert response.status_code == 404
    
    def test_delete_expense_not_found(self, client: TestClient):
        """Test deleting an expense that doesn't exist"""
        response = client.delete("/api/v1/expenses/999")
        assert response.status_code == 404


class TestGetExpensesByCategory:
    """Test GET /api/v1/expenses/category/{category_id}"""
    
    def test_get_expenses_by_category(self, client: TestClient, category_id: int):
        """Test getting expenses filtered by category"""
        # Create category 2
        response = client.post(
            "/api/v1/categories",
            json={"name": "Transport", "color": "#00FF00"}
        )
        category_2_id = response.json()["id"]
        
        # Create expenses in category 1
        client.post(
            "/api/v1/expenses",
            json={
                "amount": "50.00",
                "description": "Lunch 1",
                "date": "2025-05-01",
                "category_id": category_id
            }
        )
        client.post(
            "/api/v1/expenses",
            json={
                "amount": "60.00",
                "description": "Lunch 2",
                "date": "2025-05-01",
                "category_id": category_id
            }
        )
        
        # Create expense in category 2
        client.post(
            "/api/v1/expenses",
            json={
                "amount": "100.00",
                "description": "Bus ticket",
                "date": "2025-05-01",
                "category_id": category_2_id
            }
        )
        
        # Get expenses for category 1
        response = client.get(f"/api/v1/expenses/category/{category_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(exp["category_id"] == category_id for exp in data)
    
    def test_get_expenses_by_category_empty(self, client: TestClient, category_id: int):
        """Test getting expenses for category with no expenses"""
        response = client.get(f"/api/v1/expenses/category/{category_id}")
        assert response.status_code == 200
        assert response.json() == []


class TestGetExpensesByDateRange:
    """Test GET /api/v1/expenses/date-range/search"""
    
    def test_get_expenses_by_date_range(self, client: TestClient, category_id: int):
        """Test filtering expenses by date range"""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)
        
        # Create expense today
        client.post(
            "/api/v1/expenses",
            json={
                "amount": "50.00",
                "description": "Today",
                "date": str(today),
                "category_id": category_id
            }
        )
        
        # Create expense tomorrow
        client.post(
            "/api/v1/expenses",
            json={
                "amount": "60.00",
                "description": "Tomorrow",
                "date": str(tomorrow),
                "category_id": category_id
            }
        )
        
        # Create expense next week
        client.post(
            "/api/v1/expenses",
            json={
                "amount": "100.00",
                "description": "Next week",
                "date": str(next_week),
                "category_id": category_id
            }
        )
        
        # Get expenses from today to tomorrow
        response = client.get(
            f"/api/v1/expenses/date-range/search?start_date={today}&end_date={tomorrow}"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Today and tomorrow
    
    def test_get_expenses_by_date_range_empty(self, client: TestClient):
        """Test date range with no expenses"""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        response = client.get(
            f"/api/v1/expenses/date-range/search?start_date={today}&end_date={tomorrow}"
        )
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_expenses_by_date_range_missing_params(self, client: TestClient):
        """Test date range endpoint without required parameters"""
        response = client.get("/api/v1/expenses/date-range/search")
        assert response.status_code == 422
