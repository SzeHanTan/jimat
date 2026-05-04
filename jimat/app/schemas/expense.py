from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Annotated, Union


# ✅ 定义 reusable 类型（很专业的写法）
AmountType = Annotated[
    Decimal,
    Field(gt=0)
]


class ExpenseCreate(BaseModel):
    """Schema for creating a new expense (POST request body)"""
    amount: AmountType
    description: str = Field(..., min_length=1, max_length=255)
    date: date
    category_id: int = Field(..., gt=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "amount": "29.99",
                "description": "Lunch at coffee shop",
                "date": "2025-05-01",
                "category_id": 1
            }
        }
    )


class ExpenseUpdate(BaseModel):
    """Schema for updating an expense (PUT request body) - all fields optional"""
    amount: Union[Decimal, None] = None
    description: Union[str, None] = None
    date: Union[date, None] = None
    category_id: Union[int, None] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "amount": "35.00",
                "description": "Updated lunch cost"
            }
        }
    )


class ExpenseResponse(BaseModel):
    """Schema for returning expense (GET response)"""
    id: int
    amount: Decimal
    description: str
    date: date
    category_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "amount": "29.99",
                "description": "Lunch at coffee shop",
                "date": "2025-05-01",
                "category_id": 1,
                "created_at": "2025-05-01T10:00:00",
                "updated_at": "2025-05-01T10:00:00"
            }
        }
    }