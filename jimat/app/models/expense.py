"""
Expense model - represents a single expense record.

Why we use Numeric instead of Float:
- Float has rounding errors (bad for money!)
- Numeric stores exact decimal values (safe for currency)
"""

from sqlalchemy import Column, Integer, Numeric, String, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.models import Base


class Expense(Base):
    """
    Expense table in PostgreSQL.
    
    Attributes:
        id: Unique identifier
        amount: How much was spent (stored as Numeric for precision)
        description: What was spent on
        date: When the expense occurred
        category_id: Foreign key to Category (which category is this expense in)
        created_at: When the record was created
        updated_at: When the record was last modified
    
    Why Numeric for amount:
    - Money requires precision (e.g., $10.99 not 10.989999...)
    - Float has rounding errors in binary representation
    - Numeric stores exact decimal values
    
    Why Foreign Key:
    - Links each expense to a category
    - Database enforces referential integrity (can't create expense for non-existent category)
    - Allows efficient filtering/aggregation by category
    """
    
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)  # 10 total digits, 2 after decimal (max $99,999.99)
    description = Column(String(255), nullable=False)
    date = Column(Date, nullable=False, index=True)  # Index for efficient date filtering
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship (one-to-many direction)
    # This allows: expense.category to get the related Category object
    category = relationship("Category")
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<Expense(id={self.id}, amount={self.amount}, category_id={self.category_id})>"
