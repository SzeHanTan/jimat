"""
Database connection and session management.

This module sets up SQLAlchemy to connect to PostgreSQL (Supabase).

Why we do this:
- Centralized database connection (reuse everywhere)
- SessionLocal factory (each request gets its own database session)
- Dependency injection (FastAPI will provide sessions automatically)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings


# Create the database engine
# The engine is like a "connection pool" - manages multiple connections to PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    # echo=True  # Uncomment to see SQL queries being executed (helpful for debugging)
)

# Create a session factory
# Each time we call SessionLocal(), we get a new database session
SessionLocal = sessionmaker(
    autocommit=False,  # Don't auto-commit (we'll commit explicitly)
    autoflush=False,   # Don't auto-flush (we'll flush explicitly)
    bind=engine
)


def get_db() -> Session:
    """
    FastAPI dependency that provides a database session.
    
    Usage in routes:
    @app.get("/items")
    def get_items(db: Session = Depends(get_db)):
        # db is a database session, ready to use
        return db.query(Item).all()
    
    Why it's a generator:
    - The 'yield' returns the session to the route handler
    - After the route completes, 'finally' closes the session (cleanup)
    - This ensures sessions are always closed, preventing connection leaks
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
