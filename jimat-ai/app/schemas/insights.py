"""Schemas for insights API"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal
from datetime import datetime


class ExpenseData(BaseModel):
    """Input expense data for analysis"""
    amount: float = Field(..., gt=0, description="Expense amount")
    date: str = Field(..., description="Expense date (YYYY-MM-DD)")
    category: Optional[str] = Field(None, description="Expense category")
    description: Optional[str] = Field(None, description="Expense description")


class CategoryBreakdown(BaseModel):
    """Category spending breakdown"""
    category: str = Field(..., description="Category name")
    total: float = Field(..., description="Total spending in category")
    percentage: float = Field(..., description="Percentage of total spending")
    count: int = Field(..., description="Number of transactions")
    average: float = Field(..., description="Average transaction amount")
    min: float = Field(..., description="Minimum transaction amount")
    max: float = Field(..., description="Maximum transaction amount")


class SummaryRequest(BaseModel):
    """Request for summary analytics"""
    expenses: List[ExpenseData] = Field(..., description="List of expenses to analyze")
    period: Literal["daily", "weekly", "monthly", "yearly"] = Field(
        "monthly", 
        description="Time period for aggregation"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "expenses": [
                    {"amount": 25.50, "date": "2024-05-01", "category": "Food", "description": "Lunch"},
                    {"amount": 45.00, "date": "2024-05-02", "category": "Transport", "description": "Uber ride"},
                ],
                "period": "monthly"
            }
        }


class SummaryResponse(BaseModel):
    """Summary analytics response"""
    success: bool = Field(True, description="Whether analysis was successful")
    period: str = Field(..., description="Analysis period")
    total_spending: float = Field(..., description="Total spending")
    transaction_count: int = Field(..., description="Number of transactions")
    average_transaction: float = Field(..., description="Average transaction amount")
    biggest_transaction: float = Field(..., description="Largest single transaction")
    smallest_transaction: float = Field(..., description="Smallest single transaction")
    biggest_category: Optional[CategoryBreakdown] = Field(None, description="Top spending category")
    category_breakdown: List[CategoryBreakdown] = Field(..., description="Breakdown by category")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    timestamp: str = Field(..., description="ISO timestamp")


class SpendingPatternResponse(BaseModel):
    """Single spending pattern"""
    pattern_type: str = Field(..., description="Type of pattern (high, low, unusual, consistent)")
    description: str = Field(..., description="Description of pattern")
    severity: float = Field(..., ge=0, le=1, description="Severity score 0-1")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")


class PatternsRequest(BaseModel):
    """Request for pattern detection"""
    expenses: List[ExpenseData] = Field(..., description="List of expenses to analyze")
    baseline_days: int = Field(30, ge=1, description="Days to consider for baseline")
    
    class Config:
        json_schema_extra = {
            "example": {
                "expenses": [
                    {"amount": 25.50, "date": "2024-05-01", "category": "Food"},
                ],
                "baseline_days": 30
            }
        }


class PatternsResponse(BaseModel):
    """Pattern detection response"""
    success: bool = Field(True, description="Whether analysis was successful")
    patterns_detected: int = Field(..., description="Number of patterns found")
    patterns: List[SpendingPatternResponse] = Field(..., description="List of detected patterns")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    timestamp: str = Field(..., description="ISO timestamp")


class PeriodAnalysis(BaseModel):
    """Analysis for a time period"""
    start_date: str = Field(..., description="Period start date")
    end_date: str = Field(..., description="Period end date")
    total_spending: float = Field(..., description="Total spending in period")
    count: int = Field(..., description="Transaction count")
    average: float = Field(..., description="Average transaction amount")


class TrendData(BaseModel):
    """Trend comparison data"""
    change_percentage: float = Field(..., description="Percentage change")
    direction: str = Field(..., description="Trend direction (↑ increasing, ↓ decreasing, → stable)")


class TrendsRequest(BaseModel):
    """Request for trend analysis"""
    expenses: List[ExpenseData] = Field(..., description="List of expenses to analyze")
    comparison_days: int = Field(30, ge=1, description="Days to analyze")
    
    class Config:
        json_schema_extra = {
            "example": {
                "expenses": [
                    {"amount": 25.50, "date": "2024-05-01"},
                ],
                "comparison_days": 30
            }
        }


class TrendsResponse(BaseModel):
    """Trend analysis response"""
    success: bool = Field(True, description="Whether analysis was successful")
    date_range_days: int = Field(..., description="Total days in analysis range")
    first_date: str = Field(..., description="First expense date")
    last_date: str = Field(..., description="Last expense date")
    period1: PeriodAnalysis = Field(..., description="First period analysis")
    period2: PeriodAnalysis = Field(..., description="Second period analysis")
    trend: TrendData = Field(..., description="Trend information")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    timestamp: str = Field(..., description="ISO timestamp")


class BudgetRecommendationData(BaseModel):
    """Budget recommendation for a category"""
    category: str = Field(..., description="Category name")
    recommended_budget: float = Field(..., description="Recommended monthly budget")
    historical_average: float = Field(..., description="Historical average spending")
    variance: float = Field(..., description="High-low variance")
    reasoning: str = Field(..., description="Reasoning for recommendation")


class BudgetRequest(BaseModel):
    """Request for budget recommendations"""
    expenses: List[ExpenseData] = Field(..., description="List of expenses to analyze")
    safety_margin: float = Field(1.2, ge=1.0, le=2.0, description="Safety margin multiplier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "expenses": [
                    {"amount": 25.50, "date": "2024-05-01", "category": "Food"},
                ],
                "safety_margin": 1.2
            }
        }


class BudgetResponse(BaseModel):
    """Budget recommendations response"""
    success: bool = Field(True, description="Whether analysis was successful")
    total_historical_spending: float = Field(..., description="Total historical spending")
    recommended_total_budget: float = Field(..., description="Total recommended budget")
    recommendations: List[BudgetRecommendationData] = Field(..., description="Per-category recommendations")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    timestamp: str = Field(..., description="ISO timestamp")


class TopExpenseData(BaseModel):
    """Top expense information"""
    amount: float = Field(..., description="Expense amount")
    date: str = Field(..., description="Expense date")
    category: Optional[str] = Field(None, description="Category")
    description: Optional[str] = Field(None, description="Description")


class TopExpensesRequest(BaseModel):
    """Request for top expenses"""
    expenses: List[ExpenseData] = Field(..., description="List of expenses")
    limit: int = Field(5, ge=1, le=100, description="Number of top expenses to return")
    
    class Config:
        json_schema_extra = {
            "example": {
                "expenses": [
                    {"amount": 25.50, "date": "2024-05-01", "category": "Food"},
                ],
                "limit": 5
            }
        }


class TopExpensesResponse(BaseModel):
    """Top expenses response"""
    success: bool = Field(True, description="Whether analysis was successful")
    count: int = Field(..., description="Number of top expenses returned")
    total_of_top: float = Field(..., description="Total of returned top expenses")
    expenses: List[TopExpenseData] = Field(..., description="List of top expenses")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    timestamp: str = Field(..., description="ISO timestamp")


class InsightsHealthResponse(BaseModel):
    """Health check response for insights"""
    status: str = Field(..., description="Health status")
    engine: str = Field("InsightsEngine", description="Engine type")
    available: bool = Field(True, description="Whether insights engine is operational")
    features: List[str] = Field(..., description="Available features")
