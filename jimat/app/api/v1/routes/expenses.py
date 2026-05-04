"""
Expense API routes (endpoints).
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import date
from jimat.app.database.session import get_db
from jimat.app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from jimat.app.crud import expense as crud_expense


router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseResponse, status_code=201)
def create_expense(
    expense_in: ExpenseCreate,
    db: Session = Depends(get_db)
):
    """Create a new expense"""
    try:
        db_expense = crud_expense.create_expense(db, expense_in)
        return db_expense
    except IntegrityError as e:
        # Handle foreign key constraint and other database integrity errors
        raise HTTPException(
            status_code=400,
            detail="Invalid category_id or data integrity violation"
        )


@router.get("", response_model=list[ExpenseResponse])
def get_expenses(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all expenses with pagination.
    
    Query parameters:
    - skip: How many records to skip (default 0)
    - limit: How many records to return (default 50, max 100)
    
    Example: GET /api/v1/expenses?skip=20&limit=10
    Returns items 20-30
    """
    expenses = crud_expense.get_expenses(db, skip=skip, limit=limit)
    return expenses


# 特定路由必须放在通用路由之前！
@router.get("/date-range/search", response_model=list[ExpenseResponse])
def get_expenses_by_date(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db)
):
    """
    Get expenses within a date range.
    
    Example: GET /api/v1/expenses/date-range/search?start_date=2025-01-01&end_date=2025-05-01
    """
    expenses = crud_expense.get_expenses_by_date_range(db, start_date, end_date)
    return expenses


@router.get("/category/{category_id}", response_model=list[ExpenseResponse])
def get_expenses_by_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Get all expenses for a specific category"""
    expenses = crud_expense.get_expenses_by_category(db, category_id)
    return expenses


# 通用路由放在最后
@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    """Get a specific expense by ID"""
    expense = crud_expense.get_expense(db, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    expense_in: ExpenseUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing expense"""
    expense = crud_expense.update_expense(db, expense_id, expense_in)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.delete("/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    """Delete an expense"""
    success = crud_expense.delete_expense(db, expense_id)
    if not success:
        raise HTTPException(status_code=404, detail="Expense not found")
