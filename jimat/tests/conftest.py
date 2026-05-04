"""
Pytest configuration and fixtures for testing.

This file:
1. Sets up a temporary SQLite database for testing
2. Creates FastAPI test client
3. Provides fixtures that tests can use
"""

import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.models import Base
from app.database.session import get_db


# Create a temporary SQLite database for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# Create engine with StaticPool to keep connection alive for in-memory DB
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Enable foreign keys for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Create session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables once at startup
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override the get_db dependency to use test database"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def clear_db():
    """
    Clear all tables before each test.
    autouse=True means this runs for every test automatically.
    """
    # Delete all data from all tables (in reverse order to handle foreign keys)
    connection = engine.connect()
    for table in reversed(Base.metadata.sorted_tables):
        connection.execute(table.delete())
    connection.commit()
    connection.close()
    
    yield  # Test runs here
    
    # Optional: cleanup after test (not strictly necessary)


@pytest.fixture(scope="function")
def db():
    """
    Fixture that provides a database session for each test.
    
    Usage in CRUD unit tests:
    def test_something(db):
        category = crud_category.create_category(db, ...)
        assert category.id == 1
    """
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client():
    """
    Fixture that provides a FastAPI test client.
    
    Usage in API endpoint tests:
    def test_something(client):
        response = client.get("/api/v1/categories")
        assert response.status_code == 200
    """
    with TestClient(app) as test_client:
        yield test_client

