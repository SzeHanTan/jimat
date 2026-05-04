"""
Category model - represents an expense category (Food, Transport, Entertainment, etc.)

Why we separate models into different files:
- Each file handles one entity (single responsibility principle)
- Easier to maintain and understand
- Scales well as app grows
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from jimat.app.models import Base


class Category(Base):
    """
    Category table in PostgreSQL.
    
    Attributes:
        id: Unique identifier (primary key)
        name: Category name (Food, Transport, etc.)
        color: Hex color for UI display (#FF5733)
        created_at: When the category was created
        updated_at: When the category was last modified
    
    Why these fields:
    - 'id': Every table needs a primary key (unique identifier)
    - 'name': The actual category name
    - 'color': For frontend UI (optional, but nice for organization)
    - 'created_at', 'updated_at': Audit trail (when was this created/modified)
    """
    
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    color = Column(String(7), default="#6366F1")  # Default to indigo blue
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<Category(id={self.id}, name='{self.name}')>"
