"""
CRUD operations for Category.
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def create_category(db: Session, category_in: CategoryCreate) -> Category:
    """
    Create a new category in the database.
    
    Args:
        db: Database session
        category_in: Pydantic schema with category data
    
    Returns:
        The created Category object
    
    Why we take Pydantic schema as input:
    - Data is already validated (Pydantic checked field types, lengths, etc.)
    - Type-safe (editor knows what fields are available)
    - Single source of truth for what fields are required
    """
    db_category = Category(
        name=category_in.name,
        color=category_in.color
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)  # Refresh to get auto-generated fields like id, created_at
    return db_category


def get_categories(db: Session) -> list[Category]:
    """Get all categories"""
    return db.query(Category).all()


def get_category(db: Session, category_id: int) -> Optional[Category]:
    """Get a specific category by ID"""
    return db.query(Category).filter(Category.id == category_id).first()


def update_category(db: Session, category_id: int, category_in: CategoryUpdate) -> Optional[Category]:
    """
    Update an existing category.
    
    Only updates fields that are provided (not None).
    """
    db_category = get_category(db, category_id)
    if not db_category:
        return None
    
    # Only update fields that were provided (not None)
    if category_in.name is not None:
        db_category.name = category_in.name
    if category_in.color is not None:
        db_category.color = category_in.color
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int) -> bool:
    """
    Delete a category.
    
    Returns True if deleted, False if not found.
    """
    db_category = get_category(db, category_id)
    if not db_category:
        return False
    
    db.delete(db_category)
    db.commit()
    return True
