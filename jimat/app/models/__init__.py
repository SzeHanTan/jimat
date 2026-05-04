"""
Database models (ORM layer).

Models define the structure of tables in PostgreSQL using SQLAlchemy.
Each class becomes a table, each attribute becomes a column.
"""

from sqlalchemy.orm import declarative_base

# Base class for all models
# All models inherit from this to become SQLAlchemy models
Base = declarative_base()
