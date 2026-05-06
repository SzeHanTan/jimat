"""
CRUD operations for Expense.
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate


def create_expense(db: Session, expense_in: ExpenseCreate) -> Expense:
    """Create a new expense"""
    db_expense = Expense(
        amount=expense_in.amount,
        description=expense_in.description,
        date=expense_in.date,
        category_id=expense_in.category_id
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def get_expenses(db: Session, skip: int = 0, limit: int = 50) -> list[Expense]:
    """
    Get all expenses with pagination.
    
    Why pagination:
    - Prevents loading millions of records at once
    - Improves API response time
    - Better user experience (load data incrementally)
    
    Typical usage: skip=0, limit=20 (first 20 items)
    For next page: skip=20, limit=20 (items 20-40)
    """
    return db.query(Expense).offset(skip).limit(limit).all()


def get_expense(db: Session, expense_id: int) -> Optional[Expense]:
    """Get a specific expense by ID"""
    return db.query(Expense).filter(Expense.id == expense_id).first()


def update_expense(db: Session, expense_id: int, expense_in: ExpenseUpdate) -> Optional[Expense]:
    """
    Update an existing expense.
    
    Only updates fields that are provided (not None).
    """
    db_expense = get_expense(db, expense_id)
    if not db_expense:
        return None
    
    # Only update fields that were provided (use 'is not None' to allow updating to 0/empty)
    if expense_in.amount is not None:
        db_expense.amount = expense_in.amount
    if expense_in.description is not None:
        db_expense.description = expense_in.description
    if expense_in.date is not None:
        db_expense.date = expense_in.date
    if expense_in.category_id is not None:
        db_expense.category_id = expense_in.category_id
    
    db.commit()
    db.refresh(db_expense)
    return db_expense


def delete_expense(db: Session, expense_id: int) -> bool:
    """Delete an expense. Returns True if deleted, False if not found."""
    db_expense = get_expense(db, expense_id)
    if not db_expense:
        return False
    
    db.delete(db_expense)
    db.commit()
    return True


def get_expenses_by_category(db: Session, category_id: int) -> list[Expense]:
    """Get all expenses for a specific category"""
    return db.query(Expense).filter(Expense.category_id == category_id).all()


def get_expenses_by_date_range(db: Session, start_date, end_date) -> list[Expense]:
    """Get expenses within a date range"""
    return db.query(Expense).filter(
        Expense.date >= start_date,
        Expense.date <= end_date
    ).all()
