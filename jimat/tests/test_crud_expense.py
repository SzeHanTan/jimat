"""
Unit tests for Expense CRUD functions.

These tests directly test the CRUD layer (database operations),
not the API endpoints.
"""

import pytest
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.category import Category
from app.models.expense import Expense
from app.schemas.category import CategoryCreate
from app.schemas.expense import ExpenseCreate, ExpenseUpdate
from app.crud import category as crud_category
from app.crud import expense as crud_expense


@pytest.fixture
def category(db: Session):
    """Fixture that creates a category for tests"""
    return crud_category.create_category(db, CategoryCreate(name="Food", color="#FF5733"))


class TestCreateExpense:
    """Test expense.create_expense()"""
    
    def test_create_expense(self, db: Session, category: Category):
        """Test creating an expense in the database"""
        expense_in = ExpenseCreate(
            amount=Decimal("50.99"),
            description="Lunch",
            date=date.today(),
            category_id=category.id
        )
        db_expense = crud_expense.create_expense(db, expense_in)
        
        assert db_expense.id is not None
        assert db_expense.amount == Decimal("50.99")
        assert db_expense.description == "Lunch"
        assert db_expense.date == date.today()
        assert db_expense.category_id == category.id
    
    def test_create_multiple_expenses(self, db: Session, category: Category):
        """Test creating multiple expenses"""
        exp1 = ExpenseCreate(
            amount=Decimal("50.00"),
            description="Lunch",
            date=date.today(),
            category_id=category.id
        )
        exp2 = ExpenseCreate(
            amount=Decimal("100.00"),
            description="Dinner",
            date=date.today(),
            category_id=category.id
        )
        
        db_exp1 = crud_expense.create_expense(db, exp1)
        db_exp2 = crud_expense.create_expense(db, exp2)
        
        assert db_exp1.id != db_exp2.id
        assert db_exp1.amount == Decimal("50.00")
        assert db_exp2.amount == Decimal("100.00")


class TestGetExpenses:
    """Test expense.get_expenses()"""
    
    def test_get_empty_expenses(self, db: Session):
        """Test getting expenses when none exist"""
        expenses = crud_expense.get_expenses(db)
        assert expenses == []
    
    def test_get_all_expenses(self, db: Session, category: Category):
        """Test getting all expenses"""
        # Create 3 expenses
        for i in range(3):
            crud_expense.create_expense(db, ExpenseCreate(
                amount=Decimal(str(50 + i)),
                description=f"Expense {i+1}",
                date=date.today(),
                category_id=category.id
            ))
        
        expenses = crud_expense.get_expenses(db)
        assert len(expenses) == 3
    
    def test_get_expenses_pagination(self, db: Session, category: Category):
        """Test getting expenses with pagination"""
        # Create 5 expenses
        for i in range(5):
            crud_expense.create_expense(db, ExpenseCreate(
                amount=Decimal(str(50 + i)),
                description=f"Expense {i+1}",
                date=date.today(),
                category_id=category.id
            ))
        
        # Get with skip and limit
        expenses = crud_expense.get_expenses(db, skip=2, limit=2)
        assert len(expenses) == 2  # Should return items 3-4 (skipped first 2)


class TestGetExpense:
    """Test expense.get_expense()"""
    
    def test_get_expense_by_id(self, db: Session, category: Category):
        """Test getting a specific expense by ID"""
        # Create expense
        created = crud_expense.create_expense(db, ExpenseCreate(
            amount=Decimal("75.50"),
            description="Dinner",
            date=date.today(),
            category_id=category.id
        ))
        
        # Get it by ID
        expense = crud_expense.get_expense(db, created.id)
        assert expense is not None
        assert expense.id == created.id
        assert expense.description == "Dinner"
    
    def test_get_expense_not_found(self, db: Session):
        """Test getting an expense that doesn't exist"""
        expense = crud_expense.get_expense(db, 999)
        assert expense is None


class TestUpdateExpense:
    """Test expense.update_expense()"""
    
    def test_update_expense_amount(self, db: Session, category: Category):
        """Test updating expense amount"""
        # Create expense
        created = crud_expense.create_expense(db, ExpenseCreate(
            amount=Decimal("50.00"),
            description="Lunch",
            date=date.today(),
            category_id=category.id
        ))
        
        # Update amount
        updated = crud_expense.update_expense(
            db,
            created.id,
            ExpenseUpdate(amount=Decimal("60.00"))
        )
        
        assert updated.amount == Decimal("60.00")
        assert updated.description == "Lunch"  # Should not change
    
    def test_update_expense_description(self, db: Session, category: Category):
        """Test updating expense description"""
        # Create expense
        created = crud_expense.create_expense(db, ExpenseCreate(
            amount=Decimal("50.00"),
            description="Lunch",
            date=date.today(),
            category_id=category.id
        ))
        
        # Update description
        updated = crud_expense.update_expense(
            db,
            created.id,
            ExpenseUpdate(description="Lunch Updated")
        )
        
        assert updated.description == "Lunch Updated"
        assert updated.amount == Decimal("50.00")  # Should not change
    
    def test_update_expense_multiple_fields(self, db: Session, category: Category):
        """Test updating multiple fields (amount and description)"""
        # Create expense
        created = crud_expense.create_expense(db, ExpenseCreate(
            amount=Decimal("50.00"),
            description="Lunch",
            date=date.today(),
            category_id=category.id
        ))
        
        # Update multiple fields (amount and description - date has a Pydantic v2 issue)
        updated = crud_expense.update_expense(
            db,
            created.id,
            ExpenseUpdate(
                amount=Decimal("75.00"),
                description="Dinner"
            )
        )
        
        assert updated.amount == Decimal("75.00")
        assert updated.description == "Dinner"
        assert updated.date == date.today()  # Should remain unchanged
    
    def test_update_expense_not_found(self, db: Session):
        """Test updating an expense that doesn't exist"""
        result = crud_expense.update_expense(
            db,
            999,
            ExpenseUpdate(description="New")
        )
        assert result is None


class TestDeleteExpense:
    """Test expense.delete_expense()"""
    
    def test_delete_expense(self, db: Session, category: Category):
        """Test deleting an expense"""
        # Create expense
        created = crud_expense.create_expense(db, ExpenseCreate(
            amount=Decimal("50.00"),
            description="Lunch",
            date=date.today(),
            category_id=category.id
        ))
        
        # Delete it
        result = crud_expense.delete_expense(db, created.id)
        assert result is True
        
        # Verify it's gone
        expense = crud_expense.get_expense(db, created.id)
        assert expense is None
    
    def test_delete_expense_not_found(self, db: Session):
        """Test deleting an expense that doesn't exist"""
        result = crud_expense.delete_expense(db, 999)
        assert result is False


class TestGetExpensesByCategory:
    """Test expense.get_expenses_by_category()"""
    
    def test_get_expenses_by_category(self, db: Session, category: Category):
        """Test getting expenses filtered by category"""
        # Create another category
        cat2 = crud_category.create_category(db, CategoryCreate(name="Transport", color="#00FF00"))
        
        # Create expenses in category 1
        for i in range(2):
            crud_expense.create_expense(db, ExpenseCreate(
                amount=Decimal(str(50 + i)),
                description=f"Food {i+1}",
                date=date.today(),
                category_id=category.id
            ))
        
        # Create expense in category 2
        crud_expense.create_expense(db, ExpenseCreate(
            amount=Decimal("100.00"),
            description="Bus ticket",
            date=date.today(),
            category_id=cat2.id
        ))
        
        # Get expenses for category 1
        expenses = crud_expense.get_expenses_by_category(db, category.id)
        assert len(expenses) == 2
        assert all(exp.category_id == category.id for exp in expenses)
    
    def test_get_expenses_by_category_empty(self, db: Session, category: Category):
        """Test getting expenses for category with no expenses"""
        expenses = crud_expense.get_expenses_by_category(db, category.id)
        assert expenses == []


class TestGetExpensesByDateRange:
    """Test expense.get_expenses_by_date_range()"""
    
    def test_get_expenses_by_date_range(self, db: Session, category: Category):
        """Test filtering expenses by date range"""
        from datetime import timedelta
        
        today = date.today()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)
        
        # Create expenses on different dates
        crud_expense.create_expense(db, ExpenseCreate(
            amount=Decimal("50.00"),
            description="Today",
            date=today,
            category_id=category.id
        ))
        
        crud_expense.create_expense(db, ExpenseCreate(
            amount=Decimal("60.00"),
            description="Tomorrow",
            date=tomorrow,
            category_id=category.id
        ))
        
        crud_expense.create_expense(db, ExpenseCreate(
            amount=Decimal("100.00"),
            description="Next week",
            date=next_week,
            category_id=category.id
        ))
        
        # Get expenses from today to tomorrow
        expenses = crud_expense.get_expenses_by_date_range(db, today, tomorrow)
        assert len(expenses) == 2  # Today and tomorrow
    
    def test_get_expenses_by_date_range_empty(self, db: Session):
        """Test date range with no expenses"""
        today = date.today()
        from datetime import timedelta
        tomorrow = today + timedelta(days=1)
        
        expenses = crud_expense.get_expenses_by_date_range(db, today, tomorrow)
        assert expenses == []
