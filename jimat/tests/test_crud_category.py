"""
Unit tests for Category CRUD functions.

These tests directly test the CRUD layer (database operations),
not the API endpoints.
"""

import pytest
from sqlalchemy.orm import Session
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.crud import category as crud_category


class TestCreateCategory:
    """Test category.create_category()"""
    
    def test_create_category(self, db: Session):
        """Test creating a category in the database"""
        category_in = CategoryCreate(name="Food", color="#FF5733")
        db_category = crud_category.create_category(db, category_in)
        
        assert db_category.id is not None
        assert db_category.name == "Food"
        assert db_category.color == "#FF5733"
        assert db_category.created_at is not None
        assert db_category.updated_at is not None
    
    def test_create_multiple_categories(self, db: Session):
        """Test creating multiple categories"""
        cat1 = CategoryCreate(name="Food", color="#FF5733")
        cat2 = CategoryCreate(name="Transport", color="#00FF00")
        
        db_cat1 = crud_category.create_category(db, cat1)
        db_cat2 = crud_category.create_category(db, cat2)
        
        assert db_cat1.id != db_cat2.id
        assert db_cat1.name == "Food"
        assert db_cat2.name == "Transport"


class TestGetCategories:
    """Test category.get_categories()"""
    
    def test_get_empty_categories(self, db: Session):
        """Test getting categories when none exist"""
        categories = crud_category.get_categories(db)
        assert categories == []
    
    def test_get_all_categories(self, db: Session):
        """Test getting all categories after creating some"""
        # Create 2 categories
        crud_category.create_category(db, CategoryCreate(name="Food", color="#FF5733"))
        crud_category.create_category(db, CategoryCreate(name="Transport", color="#00FF00"))
        
        # Get all
        categories = crud_category.get_categories(db)
        assert len(categories) == 2
        assert categories[0].name == "Food"
        assert categories[1].name == "Transport"


class TestGetCategory:
    """Test category.get_category()"""
    
    def test_get_category_by_id(self, db: Session):
        """Test getting a specific category by ID"""
        # Create a category
        created = crud_category.create_category(db, CategoryCreate(name="Food", color="#FF5733"))
        
        # Get it by ID
        category = crud_category.get_category(db, created.id)
        assert category is not None
        assert category.id == created.id
        assert category.name == "Food"
    
    def test_get_category_not_found(self, db: Session):
        """Test getting a category that doesn't exist"""
        category = crud_category.get_category(db, 999)
        assert category is None


class TestUpdateCategory:
    """Test category.update_category()"""
    
    def test_update_category_name(self, db: Session):
        """Test updating category name"""
        # Create category
        created = crud_category.create_category(db, CategoryCreate(name="Food", color="#FF5733"))
        
        # Update name
        updated = crud_category.update_category(
            db, 
            created.id, 
            CategoryUpdate(name="Food Updated")
        )
        
        assert updated.name == "Food Updated"
        assert updated.color == "#FF5733"  # Should not change
    
    def test_update_category_color(self, db: Session):
        """Test updating category color"""
        # Create category
        created = crud_category.create_category(db, CategoryCreate(name="Food", color="#FF5733"))
        
        # Update color
        updated = crud_category.update_category(
            db, 
            created.id, 
            CategoryUpdate(color="#00FF00")
        )
        
        assert updated.name == "Food"  # Should not change
        assert updated.color == "#00FF00"
    
    def test_update_category_both(self, db: Session):
        """Test updating both name and color"""
        # Create category
        created = crud_category.create_category(db, CategoryCreate(name="Food", color="#FF5733"))
        
        # Update both
        updated = crud_category.update_category(
            db, 
            created.id, 
            CategoryUpdate(name="Transport", color="#0000FF")
        )
        
        assert updated.name == "Transport"
        assert updated.color == "#0000FF"
    
    def test_update_category_not_found(self, db: Session):
        """Test updating a category that doesn't exist"""
        result = crud_category.update_category(
            db, 
            999, 
            CategoryUpdate(name="New")
        )
        assert result is None


class TestDeleteCategory:
    """Test category.delete_category()"""
    
    def test_delete_category(self, db: Session):
        """Test deleting a category"""
        # Create category
        created = crud_category.create_category(db, CategoryCreate(name="Food", color="#FF5733"))
        
        # Delete it
        result = crud_category.delete_category(db, created.id)
        assert result is True
        
        # Verify it's gone
        category = crud_category.get_category(db, created.id)
        assert category is None
    
    def test_delete_category_not_found(self, db: Session):
        """Test deleting a category that doesn't exist"""
        result = crud_category.delete_category(db, 999)
        assert result is False
