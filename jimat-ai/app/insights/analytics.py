"""Core insights and analytics engine for expense analysis"""

import logging
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from decimal import Decimal
import statistics

logger = logging.getLogger(__name__)


class SummaryPeriod(str, Enum):
    """Time period for summary analytics"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass
class CategorySpending:
    """Category-level spending details"""
    category: str
    total: float
    percentage: float
    count: int
    average: float
    min: float
    max: float


@dataclass
class SpendingPattern:
    """Pattern detection result"""
    pattern_type: str  # "high", "low", "unusual", "consistent"
    description: str
    severity: float  # 0-1 scale
    confidence: float  # 0-1 scale


@dataclass
class BudgetRecommendation:
    """Budget recommendation based on historical data"""
    category: str
    recommended_budget: float
    historical_average: float
    variance: float
    reasoning: str


@dataclass
class TrendData:
    """Trend analysis for a period"""
    period: str
    start_date: str
    end_date: str
    total_spending: float
    transaction_count: int
    average_transaction: float


class InsightsEngine:
    """Engine for generating insights from expense data"""
    
    def __init__(self):
        """Initialize insights engine"""
        logger.info("Insights engine initialized")
    
    def generate_summary(
        self,
        expenses: List[Dict],
        period: str = "monthly"
    ) -> Dict:
        """
        Generate summary analytics for expenses.
        
        Args:
            expenses: List of expense dicts with amount, date, category, description
            period: Time period for aggregation (string or SummaryPeriod enum)
        
        Returns:
            Summary analytics dict
        """
        # Convert period to string if it's an enum
        period_str = period.value if hasattr(period, 'value') else str(period)
        
        if not expenses:
            return self._empty_summary()
        
        logger.info(f"Generating {period_str} summary for {len(expenses)} expenses")
        
        # Parse and validate expenses
        valid_expenses = self._validate_expenses(expenses)
        if not valid_expenses:
            return self._empty_summary()
        
        # Calculate totals
        total_spending = sum(float(e["amount"]) for e in valid_expenses)
        
        # Group by category
        by_category = self._group_by_category(valid_expenses)
        category_spending = self._calculate_category_spending(by_category, total_spending)
        
        # Find statistics
        amounts = [float(e["amount"]) for e in valid_expenses]
        biggest_expense = max(amounts)
        smallest_expense = min(amounts)
        avg_expense = sum(amounts) / len(amounts)
        
        # Find biggest category
        biggest_category = max(category_spending, key=lambda x: x.total) if category_spending else None
        
        return {
            "period": period_str,
            "total_spending": round(total_spending, 2),
            "transaction_count": len(valid_expenses),
            "average_transaction": round(avg_expense, 2),
            "biggest_transaction": round(biggest_expense, 2),
            "smallest_transaction": round(smallest_expense, 2),
            "biggest_category": asdict(biggest_category) if biggest_category else None,
            "category_breakdown": [asdict(cs) for cs in category_spending],
        }
    
    def detect_patterns(
        self,
        expenses: List[Dict],
        baseline_days: int = 30
    ) -> List[SpendingPattern]:
        """
        Detect spending patterns and anomalies.
        
        Args:
            expenses: List of expense dicts
            baseline_days: Days to consider for baseline
        
        Returns:
            List of detected patterns
        """
        if not expenses:
            return []
        
        logger.info(f"Detecting patterns from {len(expenses)} expenses")
        
        valid_expenses = self._validate_expenses(expenses)
        if not valid_expenses:
            return []
        
        patterns = []
        
        # Check for high spending days
        daily_spending = self._group_by_date(valid_expenses)
        daily_totals = [sum(float(e["amount"]) for e in day_expenses) 
                       for day_expenses in daily_spending.values()]
        
        if daily_totals:
            mean_daily = statistics.mean(daily_totals)
            stdev_daily = statistics.stdev(daily_totals) if len(daily_totals) > 1 else 0
            
            # Detect high spending days (> mean + 1 stdev)
            if stdev_daily > 0:
                for date_str, day_expenses in daily_spending.items():
                    day_total = sum(float(e["amount"]) for e in day_expenses)
                    z_score = (day_total - mean_daily) / stdev_daily if stdev_daily > 0 else 0
                    
                    if z_score > 1.5:
                        patterns.append(SpendingPattern(
                            pattern_type="high",
                            description=f"High spending on {date_str}: ${day_total:.2f}",
                            severity=min(1.0, z_score / 3),
                            confidence=0.85
                        ))
        
        # Check for unusual categories
        categories_count = self._count_categories(valid_expenses)
        if len(categories_count) > 1:
            total_transactions = sum(categories_count.values())
            for category, count in categories_count.items():
                proportion = count / total_transactions
                
                # If category is < 5% of transactions, might be unusual
                if 0 < proportion < 0.05:
                    category_total = sum(float(e["amount"]) for e in valid_expenses 
                                        if e.get("category") == category)
                    patterns.append(SpendingPattern(
                        pattern_type="unusual",
                        description=f"Unusual category '{category}': {count} transactions (${category_total:.2f})",
                        severity=0.5,
                        confidence=0.7
                    ))
        
        logger.info(f"Detected {len(patterns)} patterns")
        return patterns
    
    def analyze_trends(
        self,
        expenses: List[Dict],
        comparison_days: int = 30
    ) -> Dict:
        """
        Analyze spending trends over time.
        
        Args:
            expenses: List of expense dicts
            comparison_days: Days to analyze
        
        Returns:
            Trend analysis dict
        """
        if not expenses:
            return {"error": "No expenses to analyze"}
        
        logger.info(f"Analyzing trends for {len(expenses)} expenses")
        
        valid_expenses = self._validate_expenses(expenses)
        if not valid_expenses:
            return {"error": "No valid expenses"}
        
        # Sort by date
        sorted_expenses = sorted(valid_expenses, key=lambda x: x["date"])
        
        # Get date range
        first_date = self._parse_date(sorted_expenses[0]["date"])
        last_date = self._parse_date(sorted_expenses[-1]["date"])
        date_range = (last_date - first_date).days
        
        if date_range == 0:
            return {"error": "All expenses on same date"}
        
        # Split into periods
        mid_date = first_date + timedelta(days=date_range // 2)
        
        period1_expenses = [e for e in sorted_expenses 
                           if self._parse_date(e["date"]) <= mid_date]
        period2_expenses = [e for e in sorted_expenses 
                           if self._parse_date(e["date"]) > mid_date]
        
        total1 = sum(float(e["amount"]) for e in period1_expenses)
        total2 = sum(float(e["amount"]) for e in period2_expenses)
        
        # Calculate trend
        if total1 > 0:
            trend_percentage = ((total2 - total1) / total1) * 100
        else:
            trend_percentage = 0
        
        trend_direction = "↑ increasing" if trend_percentage > 5 else \
                         "↓ decreasing" if trend_percentage < -5 else \
                         "→ stable"
        
        return {
            "date_range_days": date_range,
            "first_date": first_date.isoformat(),
            "last_date": last_date.isoformat(),
            "period1": {
                "start_date": first_date.isoformat(),
                "end_date": mid_date.isoformat(),
                "total_spending": round(total1, 2),
                "count": len(period1_expenses),
                "average": round(total1 / len(period1_expenses), 2) if period1_expenses else 0,
            },
            "period2": {
                "start_date": (mid_date + timedelta(days=1)).isoformat(),
                "end_date": last_date.isoformat(),
                "total_spending": round(total2, 2),
                "count": len(period2_expenses),
                "average": round(total2 / len(period2_expenses), 2) if period2_expenses else 0,
            },
            "trend": {
                "change_percentage": round(trend_percentage, 2),
                "direction": trend_direction,
            }
        }
    
    def recommend_budget(
        self,
        expenses: List[Dict],
        safety_margin: float = 1.2
    ) -> List[BudgetRecommendation]:
        """
        Recommend budgets based on historical spending.
        
        Args:
            expenses: List of expense dicts
            safety_margin: Multiplier for recommended budget (1.0 = exact average, 1.2 = 20% above)
        
        Returns:
            List of budget recommendations
        """
        if not expenses:
            return []
        
        logger.info(f"Generating budget recommendations from {len(expenses)} expenses")
        
        valid_expenses = self._validate_expenses(expenses)
        if not valid_expenses:
            return []
        
        recommendations = []
        by_category = self._group_by_category(valid_expenses)
        total_spending = sum(float(e["amount"]) for e in valid_expenses)
        
        for category, category_expenses in by_category.items():
            amounts = [float(e["amount"]) for e in category_expenses]
            avg = sum(amounts) / len(amounts)
            variance = max(amounts) - min(amounts)
            
            # Recommended budget is average * safety margin
            recommended = avg * safety_margin
            
            # Reasoning based on variance
            if variance > avg:
                reasoning = f"High variance detected. Budget {recommended:.2f} to accommodate fluctuations."
            elif len(amounts) >= 10:
                reasoning = f"Based on {len(amounts)} transactions. Average is {avg:.2f}."
            else:
                reasoning = f"Limited history ({len(amounts)} transactions). Recommend monitoring."
            
            recommendations.append(BudgetRecommendation(
                category=category,
                recommended_budget=round(recommended, 2),
                historical_average=round(avg, 2),
                variance=round(variance, 2),
                reasoning=reasoning
            ))
        
        # Sort by recommended budget (highest first)
        recommendations.sort(key=lambda x: x.recommended_budget, reverse=True)
        
        logger.info(f"Generated {len(recommendations)} budget recommendations")
        return recommendations
    
    def get_biggest_expenses(
        self,
        expenses: List[Dict],
        limit: int = 5
    ) -> List[Dict]:
        """
        Get the biggest expenses.
        
        Args:
            expenses: List of expense dicts
            limit: Number of top expenses to return
        
        Returns:
            List of top expenses sorted by amount (highest first)
        """
        if not expenses:
            return []
        
        valid_expenses = self._validate_expenses(expenses)
        if not valid_expenses:
            return []
        
        # Sort by amount descending
        sorted_expenses = sorted(valid_expenses, 
                               key=lambda x: float(x["amount"]), 
                               reverse=True)
        
        return sorted_expenses[:limit]
    
    # Helper methods
    
    def _validate_expenses(self, expenses: List[Dict]) -> List[Dict]:
        """Validate and clean expense data"""
        valid = []
        for exp in expenses:
            try:
                # Ensure required fields exist
                if not all(k in exp for k in ["amount", "date"]):
                    logger.warning(f"Expense missing required fields: {exp}")
                    continue
                
                # Validate amount
                amount = float(exp["amount"])
                if amount <= 0:
                    logger.warning(f"Expense has non-positive amount: {exp}")
                    continue
                
                # Validate date
                _ = self._parse_date(exp["date"])
                
                valid.append(exp)
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid expense: {exp} - {e}")
                continue
        
        return valid
    
    def _parse_date(self, date_str) -> date:
        """Parse date string to date object"""
        if isinstance(date_str, date):
            return date_str
        
        # Try common formats
        for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%m-%d-%Y"]:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_str}")
    
    def _group_by_category(self, expenses: List[Dict]) -> Dict[str, List[Dict]]:
        """Group expenses by category"""
        grouped = {}
        for exp in expenses:
            category = exp.get("category", "Uncategorized")
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(exp)
        return grouped
    
    def _group_by_date(self, expenses: List[Dict]) -> Dict[str, List[Dict]]:
        """Group expenses by date"""
        grouped = {}
        for exp in expenses:
            date_str = str(exp.get("date", "unknown"))
            if date_str not in grouped:
                grouped[date_str] = []
            grouped[date_str].append(exp)
        return grouped
    
    def _count_categories(self, expenses: List[Dict]) -> Dict[str, int]:
        """Count expenses per category"""
        counts = {}
        for exp in expenses:
            category = exp.get("category", "Uncategorized")
            counts[category] = counts.get(category, 0) + 1
        return counts
    
    def _calculate_category_spending(
        self,
        by_category: Dict[str, List[Dict]],
        total_spending: float
    ) -> List[CategorySpending]:
        """Calculate spending per category with statistics"""
        results = []
        
        for category, category_expenses in by_category.items():
            amounts = [float(e["amount"]) for e in category_expenses]
            total = sum(amounts)
            percentage = (total / total_spending * 100) if total_spending > 0 else 0
            
            results.append(CategorySpending(
                category=category,
                total=round(total, 2),
                percentage=round(percentage, 2),
                count=len(category_expenses),
                average=round(total / len(amounts), 2),
                min=round(min(amounts), 2),
                max=round(max(amounts), 2),
            ))
        
        # Sort by total spending descending
        results.sort(key=lambda x: x.total, reverse=True)
        return results
    
    def _empty_summary(self) -> Dict:
        """Return empty summary structure"""
        return {
            "period": "monthly",
            "total_spending": 0.0,
            "transaction_count": 0,
            "average_transaction": 0.0,
            "biggest_transaction": 0.0,
            "smallest_transaction": 0.0,
            "biggest_category": None,
            "category_breakdown": [],
        }
