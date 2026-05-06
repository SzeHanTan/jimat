"""
Category API routes (endpoints).

Why keep routes separate from CRUD:
- Routes handle HTTP (request/response, status codes)
- CRUD handles database (queries, transactions)
- Easy to test each layer independently
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.crud import category as crud_category


# Create router for category endpoints
# Later, this router will be included in the main app with prefix="/api/v1"
router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", response_model=CategoryResponse, status_code=201)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new category.
    
    FastAPI automatically:
    1. Validates the request body matches CategoryCreate schema
    2. Provides a database session via Depends(get_db)
    3. Returns response as CategoryResponse schema (ensures only expected fields are returned)
    """
    db_category = crud_category.create_category(db, category_in)
    return db_category


@router.get("", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    categories = crud_category.get_categories(db)
    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """
    Get a specific category by ID.
    
    Path parameter syntax: {category_id}
    FastAPI automatically extracts this from the URL and validates it's an integer.
    """
    category = crud_category.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing category"""
    category = crud_category.update_category(db, category_id, category_in)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """
    Delete a category.
    
    Returns 204 No Content (standard for successful DELETE with no response body)
    """
    success = crud_category.delete_category(db, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
