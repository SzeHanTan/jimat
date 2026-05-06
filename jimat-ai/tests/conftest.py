"""Configuration and fixtures for pytest"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def sample_receipt_text():
    """Sample receipt text for testing"""
    return "Starbucks Receipt\nCoffee $4.50\nTea $3.25\nTotal: $7.75\nDate: 05/05/2024\nThank you!"


@pytest.fixture
def sample_invoice_text():
    """Sample invoice text for testing"""
    return "Invoice #12345\nCustomer: John Doe\nAmount Due: $150.00\nDue Date: 05/15/2024\nAccount: 5001"


@pytest.fixture
def sample_manual_entry_text():
    """Sample manual entry text for testing"""
    return "Lunch with team at Italian restaurant"


@pytest.fixture
def duplicate_text():
    """Text with duplicates for normalization testing"""
    return "Line 1\nLine 2\nLine 1\nLine 3\nLine 2\nLine 1"
