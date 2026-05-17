"""Insights and analytics API routes"""

import logging
import time
from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from app.insights import InsightsEngine
from app.schemas.insights import (
    SummaryRequest,
    SummaryResponse,
    PatternsRequest,
    PatternsResponse,
    TrendsRequest,
    TrendsResponse,
    BudgetRequest,
    BudgetResponse,
    TopExpensesRequest,
    TopExpensesResponse,
    InsightsHealthResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/insights",
    tags=["insights"],
    responses={
        400: {"description": "Invalid request"},
        500: {"description": "Server error"}
    }
)

# Initialize insights engine
insights_engine = InsightsEngine()


@router.post(
    "/summary",
    response_model=SummaryResponse,
    summary="Generate expense summary",
    description="Generate summary analytics for expenses (daily/weekly/monthly/yearly)"
)
def get_summary(request: SummaryRequest) -> SummaryResponse:
    """
    Generate summary analytics for expenses.
    
    - **expenses**: List of expenses to analyze
    - **period**: Aggregation period (daily, weekly, monthly, yearly)
    
    Returns summary with totals, averages, and category breakdown.
    """
    start_time = time.time()
    
    try:
        logger.info(f"Generating {request.period} summary for {len(request.expenses)} expenses")
        
        # Convert to dict for engine
        expenses_data = [exp.model_dump() for exp in request.expenses]
        
        # Generate summary
        summary = insights_engine.generate_summary(
            expenses=expenses_data,
            period=request.period
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        logger.info(f"Summary generated in {processing_time}ms")
        
        return SummaryResponse(
            success=True,
            period=summary["period"],
            total_spending=summary["total_spending"],
            transaction_count=summary["transaction_count"],
            average_transaction=summary["average_transaction"],
            biggest_transaction=summary["biggest_transaction"],
            smallest_transaction=summary["smallest_transaction"],
            biggest_category=summary["biggest_category"],
            category_breakdown=summary["category_breakdown"],
            processing_time_ms=processing_time,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Summary generation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summary generation failed: {str(e)}"
        )


@router.post(
    "/patterns",
    response_model=PatternsResponse,
    summary="Detect spending patterns",
    description="Detect anomalies and patterns in spending behavior"
)
def detect_patterns(request: PatternsRequest) -> PatternsResponse:
    """
    Detect spending patterns and anomalies.
    
    - **expenses**: List of expenses to analyze
    - **baseline_days**: Days to consider for baseline (default: 30)
    
    Returns detected patterns with severity and confidence scores.
    """
    start_time = time.time()
    
    try:
        logger.info(f"Detecting patterns from {len(request.expenses)} expenses")
        
        # Convert to dict for engine
        expenses_data = [exp.model_dump() for exp in request.expenses]
        
        # Detect patterns
        patterns = insights_engine.detect_patterns(
            expenses=expenses_data,
            baseline_days=request.baseline_days
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        logger.info(f"Detected {len(patterns)} patterns in {processing_time}ms")
        
        return PatternsResponse(
            success=True,
            patterns_detected=len(patterns),
            patterns=[
                {
                    "pattern_type": p.pattern_type,
                    "description": p.description,
                    "severity": p.severity,
                    "confidence": p.confidence,
                }
                for p in patterns
            ],
            processing_time_ms=processing_time,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Pattern detection error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pattern detection failed: {str(e)}"
        )


@router.post(
    "/trends",
    response_model=TrendsResponse,
    summary="Analyze spending trends",
    description="Analyze spending trends over time periods"
)
def analyze_trends(request: TrendsRequest) -> TrendsResponse:
    """
    Analyze spending trends over time.
    
    - **expenses**: List of expenses to analyze
    - **comparison_days**: Days to analyze (default: 30)
    
    Returns trend analysis comparing two periods.
    """
    start_time = time.time()
    
    try:
        logger.info(f"Analyzing trends for {len(request.expenses)} expenses")
        
        # Convert to dict for engine
        expenses_data = [exp.model_dump() for exp in request.expenses]
        
        # Analyze trends
        trends = insights_engine.analyze_trends(
            expenses=expenses_data,
            comparison_days=request.comparison_days
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        # Check for error
        if "error" in trends:
            logger.warning(f"Trend analysis returned error: {trends['error']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=trends["error"]
            )
        
        logger.info(f"Trends analyzed in {processing_time}ms")
        
        return TrendsResponse(
            success=True,
            date_range_days=trends["date_range_days"],
            first_date=trends["first_date"],
            last_date=trends["last_date"],
            period1=trends["period1"],
            period2=trends["period2"],
            trend=trends["trend"],
            processing_time_ms=processing_time,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Trend analysis error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Trend analysis failed: {str(e)}"
        )


@router.post(
    "/budget-recommendations",
    response_model=BudgetResponse,
    summary="Get budget recommendations",
    description="Generate budget recommendations based on historical spending"
)
def get_budget_recommendations(request: BudgetRequest) -> BudgetResponse:
    """
    Generate budget recommendations based on historical spending.
    
    - **expenses**: List of expenses to analyze
    - **safety_margin**: Budget multiplier (1.0 = exact average, 1.2 = 20% above)
    
    Returns per-category budget recommendations.
    """
    start_time = time.time()
    
    try:
        logger.info(f"Generating budget recommendations from {len(request.expenses)} expenses")
        
        # Convert to dict for engine
        expenses_data = [exp.model_dump() for exp in request.expenses]
        
        # Get recommendations
        recommendations = insights_engine.recommend_budget(
            expenses=expenses_data,
            safety_margin=request.safety_margin
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        # Calculate totals
        total_recommended = sum(r.recommended_budget for r in recommendations)
        total_historical = sum(float(e.amount) for e in request.expenses)
        
        logger.info(f"Generated {len(recommendations)} budget recommendations in {processing_time}ms")
        
        return BudgetResponse(
            success=True,
            total_historical_spending=round(total_historical, 2),
            recommended_total_budget=round(total_recommended, 2),
            recommendations=[
                {
                    "category": r.category,
                    "recommended_budget": r.recommended_budget,
                    "historical_average": r.historical_average,
                    "variance": r.variance,
                    "reasoning": r.reasoning,
                }
                for r in recommendations
            ],
            processing_time_ms=processing_time,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Budget recommendation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Budget recommendation failed: {str(e)}"
        )


@router.post(
    "/top-expenses",
    response_model=TopExpensesResponse,
    summary="Get top expenses",
    description="Get the biggest expenses from a list"
)
def get_top_expenses(request: TopExpensesRequest) -> TopExpensesResponse:
    """
    Get the biggest expenses.
    
    - **expenses**: List of expenses to analyze
    - **limit**: Number of top expenses to return (default: 5, max: 100)
    
    Returns top expenses sorted by amount (highest first).
    """
    start_time = time.time()
    
    try:
        logger.info(f"Getting top {request.limit} expenses from {len(request.expenses)} total")
        
        # Convert to dict for engine
        expenses_data = [exp.model_dump() for exp in request.expenses]
        
        # Get top expenses
        top_expenses = insights_engine.get_biggest_expenses(
            expenses=expenses_data,
            limit=request.limit
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        # Calculate total of top expenses
        total_of_top = sum(float(e["amount"]) for e in top_expenses)
        
        logger.info(f"Retrieved {len(top_expenses)} top expenses in {processing_time}ms")
        
        return TopExpensesResponse(
            success=True,
            count=len(top_expenses),
            total_of_top=round(total_of_top, 2),
            expenses=[
                {
                    "amount": e["amount"],
                    "date": str(e["date"]),
                    "category": e.get("category"),
                    "description": e.get("description"),
                }
                for e in top_expenses
            ],
            processing_time_ms=processing_time,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Top expenses error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Top expenses retrieval failed: {str(e)}"
        )


@router.get(
    "/health",
    response_model=InsightsHealthResponse,
    summary="Insights health check",
    description="Check if insights engine is ready"
)
def insights_health() -> InsightsHealthResponse:
    """Check if insights engine is initialized and ready"""
    try:
        return InsightsHealthResponse(
            status="healthy",
            engine="InsightsEngine",
            available=True,
            features=[
                "summary_analytics",
                "pattern_detection",
                "trend_analysis",
                "budget_recommendations",
                "top_expenses",
            ]
        )
    
    except Exception as e:
        logger.error(f"Health check error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )
