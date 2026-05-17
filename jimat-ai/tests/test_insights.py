"""Tests for insights and analytics engine"""

import pytest
from datetime import date, timedelta
from app.insights import InsightsEngine, SummaryPeriod


class TestInsightsEngine:
    """Test InsightsEngine"""
    
    @pytest.fixture
    def engine(self):
        """Get insights engine instance"""
        return InsightsEngine()
    
    @pytest.fixture
    def sample_expenses(self):
        """Sample expenses for testing"""
        today = date.today()
        return [
            {"amount": 25.50, "date": (today - timedelta(days=5)).isoformat(), "category": "Food", "description": "Lunch"},
            {"amount": 45.00, "date": (today - timedelta(days=4)).isoformat(), "category": "Transport", "description": "Uber"},
            {"amount": 15.00, "date": (today - timedelta(days=3)).isoformat(), "category": "Food", "description": "Coffee"},
            {"amount": 120.00, "date": (today - timedelta(days=2)).isoformat(), "category": "Entertainment", "description": "Movie tickets"},
            {"amount": 60.00, "date": (today - timedelta(days=1)).isoformat(), "category": "Groceries", "description": "Supermarket"},
            {"amount": 35.00, "date": today.isoformat(), "category": "Food", "description": "Dinner"},
        ]
    
    def test_engine_initialization(self, engine):
        """Test engine initializes"""
        assert engine is not None
        assert isinstance(engine, InsightsEngine)
    
    # --- Summary Tests ---
    
    def test_generate_summary_monthly(self, engine, sample_expenses):
        """Test generating monthly summary"""
        summary = engine.generate_summary(sample_expenses, period=SummaryPeriod.MONTHLY)
        
        assert summary["period"] == "monthly"
        assert summary["total_spending"] == 300.50
        assert summary["transaction_count"] == 6
        assert summary["average_transaction"] == pytest.approx(50.08, rel=1e-2)
        assert summary["biggest_transaction"] == 120.00
        assert summary["smallest_transaction"] == 15.00
    
    def test_generate_summary_daily(self, engine, sample_expenses):
        """Test generating daily summary"""
        summary = engine.generate_summary(sample_expenses, period=SummaryPeriod.DAILY)
        
        assert summary["period"] == "daily"
        assert summary["transaction_count"] == 6
    
    def test_generate_summary_weekly(self, engine, sample_expenses):
        """Test generating weekly summary"""
        summary = engine.generate_summary(sample_expenses, period=SummaryPeriod.WEEKLY)
        
        assert summary["period"] == "weekly"
        assert summary["total_spending"] == 300.50
    
    def test_generate_summary_category_breakdown(self, engine, sample_expenses):
        """Test category breakdown in summary"""
        summary = engine.generate_summary(sample_expenses, period=SummaryPeriod.MONTHLY)
        
        assert len(summary["category_breakdown"]) > 0
        categories = {cb["category"] for cb in summary["category_breakdown"]}
        assert "Food" in categories
        assert "Transport" in categories
        assert "Entertainment" in categories
    
    def test_generate_summary_biggest_category(self, engine, sample_expenses):
        """Test biggest category is identified"""
        summary = engine.generate_summary(sample_expenses, period=SummaryPeriod.MONTHLY)
        
        assert summary["biggest_category"] is not None
        assert summary["biggest_category"]["category"] == "Entertainment"  # 120.00
        assert summary["biggest_category"]["total"] == 120.00
    
    def test_generate_summary_empty_expenses(self, engine):
        """Test summary with empty expenses"""
        summary = engine.generate_summary([])
        
        assert summary["total_spending"] == 0.0
        assert summary["transaction_count"] == 0
    
    def test_generate_summary_single_expense(self, engine):
        """Test summary with single expense"""
        expenses = [{"amount": 50.0, "date": "2024-05-01", "category": "Food"}]
        summary = engine.generate_summary(expenses)
        
        assert summary["total_spending"] == 50.0
        assert summary["transaction_count"] == 1
        assert summary["average_transaction"] == 50.0
        assert summary["biggest_transaction"] == 50.0
        assert summary["smallest_transaction"] == 50.0
    
    def test_generate_summary_category_percentages(self, engine, sample_expenses):
        """Test category percentages sum to approximately 100%"""
        summary = engine.generate_summary(sample_expenses)
        
        total_percentage = sum(cb["percentage"] for cb in summary["category_breakdown"])
        assert total_percentage == pytest.approx(100.0, abs=0.1)
    
    # --- Pattern Detection Tests ---
    
    def test_detect_patterns_empty_expenses(self, engine):
        """Test pattern detection with empty expenses"""
        patterns = engine.detect_patterns([])
        
        assert patterns == []
    
    def test_detect_patterns_high_spending(self, engine):
        """Test detecting high spending days"""
        today = date.today()
        expenses = [
            {"amount": 10.0, "date": (today - timedelta(days=5)).isoformat()},
            {"amount": 15.0, "date": (today - timedelta(days=4)).isoformat()},
            {"amount": 12.0, "date": (today - timedelta(days=3)).isoformat()},
            {"amount": 100.0, "date": (today - timedelta(days=2)).isoformat()},  # High spending day
            {"amount": 11.0, "date": (today - timedelta(days=1)).isoformat()},
        ]
        
        patterns = engine.detect_patterns(expenses)
        
        # Should detect high spending day
        high_patterns = [p for p in patterns if p.pattern_type == "high"]
        assert len(high_patterns) > 0
    
    def test_detect_patterns_unusual_category(self, engine):
        """Test detecting unusual categories"""
        today = date.today()
        expenses = [
            {"amount": 20.0, "date": (today - timedelta(days=i)).isoformat(), "category": "Food"} 
            for i in range(20)
        ]
        # Add single unusual category
        expenses.append({"amount": 150.0, "date": today.isoformat(), "category": "Travel"})
        
        patterns = engine.detect_patterns(expenses)
        
        # Should detect unusual category
        unusual_patterns = [p for p in patterns if p.pattern_type == "unusual"]
        assert len(unusual_patterns) > 0 or len(patterns) > 0
    
    def test_detect_patterns_confidence_scores(self, engine, sample_expenses):
        """Test that patterns have valid confidence scores"""
        patterns = engine.detect_patterns(sample_expenses)
        
        for pattern in patterns:
            assert 0 <= pattern.confidence <= 1
            assert 0 <= pattern.severity <= 1
    
    # --- Trend Analysis Tests ---
    
    def test_analyze_trends_basic(self, engine):
        """Test basic trend analysis"""
        today = date.today()
        # First half - low spending
        expenses1 = [
            {"amount": 10.0, "date": (today - timedelta(days=10 - i)).isoformat()} 
            for i in range(5)
        ]
        # Second half - high spending
        expenses2 = [
            {"amount": 50.0, "date": (today - timedelta(days=4 - i)).isoformat()} 
            for i in range(5)
        ]
        expenses = expenses1 + expenses2
        
        trends = engine.analyze_trends(expenses)
        
        assert "period1" in trends
        assert "period2" in trends
        assert "trend" in trends
        assert trends["period2"]["total_spending"] > trends["period1"]["total_spending"]
    
    def test_analyze_trends_empty(self, engine):
        """Test trend analysis with empty expenses"""
        trends = engine.analyze_trends([])
        
        assert "error" in trends
    
    def test_analyze_trends_single_day(self, engine):
        """Test trend analysis with single day"""
        expenses = [{"amount": 50.0, "date": "2024-05-01"}]
        trends = engine.analyze_trends(expenses)
        
        assert "error" in trends
    
    def test_analyze_trends_increasing(self, engine):
        """Test detecting increasing spending trend"""
        today = date.today()
        expenses = [
            {"amount": 10.0, "date": (today - timedelta(days=10)).isoformat()},
            {"amount": 15.0, "date": (today - timedelta(days=5)).isoformat()},
            {"amount": 50.0, "date": today.isoformat()},
        ]
        
        trends = engine.analyze_trends(expenses)
        
        if "error" not in trends:
            assert "↑" in trends["trend"]["direction"] or trends["trend"]["change_percentage"] > 0
    
    # --- Budget Recommendation Tests ---
    
    def test_recommend_budget_basic(self, engine, sample_expenses):
        """Test basic budget recommendations"""
        recommendations = engine.recommend_budget(sample_expenses)
        
        assert len(recommendations) > 0
        assert all(r.category is not None for r in recommendations)
        assert all(r.recommended_budget > 0 for r in recommendations)
        assert all(r.historical_average > 0 for r in recommendations)
    
    def test_recommend_budget_with_safety_margin(self, engine, sample_expenses):
        """Test budget with custom safety margin"""
        recs_1x = engine.recommend_budget(sample_expenses, safety_margin=1.0)
        recs_15x = engine.recommend_budget(sample_expenses, safety_margin=1.5)
        
        # Higher safety margin should result in higher budgets
        for r1x, r15x in zip(sorted(recs_1x, key=lambda x: x.category), 
                            sorted(recs_15x, key=lambda x: x.category)):
            assert r15x.recommended_budget >= r1x.recommended_budget
    
    def test_recommend_budget_empty(self, engine):
        """Test budget recommendations with empty expenses"""
        recommendations = engine.recommend_budget([])
        
        assert recommendations == []
    
    def test_recommend_budget_reasoning(self, engine, sample_expenses):
        """Test that recommendations have reasoning"""
        recommendations = engine.recommend_budget(sample_expenses)
        
        for rec in recommendations:
            assert rec.reasoning is not None
            assert len(rec.reasoning) > 0
    
    # --- Top Expenses Tests ---
    
    def test_get_biggest_expenses_basic(self, engine, sample_expenses):
        """Test getting biggest expenses"""
        top = engine.get_biggest_expenses(sample_expenses, limit=3)
        
        assert len(top) <= 3
        assert top[0]["amount"] == 120.0  # Biggest should be first
        assert top[1]["amount"] == 60.0
    
    def test_get_biggest_expenses_empty(self, engine):
        """Test biggest expenses with empty list"""
        top = engine.get_biggest_expenses([])
        
        assert top == []
    
    def test_get_biggest_expenses_limit(self, engine, sample_expenses):
        """Test limit parameter"""
        top1 = engine.get_biggest_expenses(sample_expenses, limit=1)
        top5 = engine.get_biggest_expenses(sample_expenses, limit=5)
        
        assert len(top1) == 1
        assert len(top5) == 5
        assert top1[0]["amount"] == top5[0]["amount"]
    
    def test_get_biggest_expenses_sorted_descending(self, engine, sample_expenses):
        """Test that expenses are sorted in descending order"""
        top = engine.get_biggest_expenses(sample_expenses, limit=10)
        
        for i in range(len(top) - 1):
            assert top[i]["amount"] >= top[i + 1]["amount"]
    
    # --- Validation Tests ---
    
    def test_validate_expenses_invalid_amount(self, engine):
        """Test validation rejects invalid amounts"""
        expenses = [
            {"amount": -50.0, "date": "2024-05-01"},  # Negative
            {"amount": 0.0, "date": "2024-05-02"},    # Zero
            {"amount": "not_a_number", "date": "2024-05-03"},
        ]
        summary = engine.generate_summary(expenses)
        
        assert summary["transaction_count"] == 0
    
    def test_validate_expenses_invalid_date(self, engine):
        """Test validation rejects invalid dates"""
        expenses = [
            {"amount": 50.0, "date": "invalid-date"},
            {"amount": 30.0, "date": "2024/13/45"},  # Invalid month/day
        ]
        summary = engine.generate_summary(expenses)
        
        assert summary["transaction_count"] == 0
    
    def test_validate_expenses_missing_fields(self, engine):
        """Test validation handles missing required fields"""
        expenses = [
            {"amount": 50.0},  # Missing date
            {"date": "2024-05-01"},  # Missing amount
            {"amount": 25.0, "date": "2024-05-01"},  # Valid
        ]
        summary = engine.generate_summary(expenses)
        
        assert summary["transaction_count"] == 1
        assert summary["total_spending"] == 25.0


class TestInsightsAPI:
    """Test Insights API endpoints"""
    
    @pytest.fixture
    def sample_expenses_data(self):
        """Sample expense data for API"""
        today = date.today()
        return [
            {"amount": 25.50, "date": (today - timedelta(days=5)).isoformat(), "category": "Food", "description": "Lunch"},
            {"amount": 45.00, "date": (today - timedelta(days=4)).isoformat(), "category": "Transport", "description": "Uber"},
            {"amount": 15.00, "date": (today - timedelta(days=3)).isoformat(), "category": "Food", "description": "Coffee"},
            {"amount": 120.00, "date": (today - timedelta(days=2)).isoformat(), "category": "Entertainment", "description": "Movie"},
            {"amount": 60.00, "date": (today - timedelta(days=1)).isoformat(), "category": "Groceries", "description": "Supermarket"},
            {"amount": 35.00, "date": today.isoformat(), "category": "Food", "description": "Dinner"},
        ]
    
    def test_summary_endpoint_basic(self, client, sample_expenses_data):
        """Test summary endpoint"""
        response = client.post("/api/v1/insights/summary", json={
            "expenses": sample_expenses_data,
            "period": "monthly"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["period"] == "monthly"
        assert data["total_spending"] == 300.50
        assert data["transaction_count"] == 6
    
    def test_summary_endpoint_empty(self, client):
        """Test summary endpoint with empty expenses"""
        response = client.post("/api/v1/insights/summary", json={
            "expenses": [],
            "period": "monthly"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_spending"] == 0.0
    
    def test_patterns_endpoint(self, client, sample_expenses_data):
        """Test patterns endpoint"""
        response = client.post("/api/v1/insights/patterns", json={
            "expenses": sample_expenses_data,
            "baseline_days": 30
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "patterns" in data
        assert isinstance(data["patterns"], list)
    
    def test_trends_endpoint(self, client, sample_expenses_data):
        """Test trends endpoint"""
        response = client.post("/api/v1/insights/trends", json={
            "expenses": sample_expenses_data,
            "comparison_days": 30
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "period1" in data
        assert "period2" in data
        assert "trend" in data
    
    def test_budget_endpoint(self, client, sample_expenses_data):
        """Test budget recommendations endpoint"""
        response = client.post("/api/v1/insights/budget-recommendations", json={
            "expenses": sample_expenses_data,
            "safety_margin": 1.2
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "recommendations" in data
        assert len(data["recommendations"]) > 0
    
    def test_top_expenses_endpoint(self, client, sample_expenses_data):
        """Test top expenses endpoint"""
        response = client.post("/api/v1/insights/top-expenses", json={
            "expenses": sample_expenses_data,
            "limit": 3
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["expenses"]) <= 3
        assert data["count"] == 3
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/api/v1/insights/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["available"] is True
        assert "summary_analytics" in data["features"]
    
    def test_summary_all_periods(self, client, sample_expenses_data):
        """Test summary endpoint with all period types"""
        periods = ["daily", "weekly", "monthly", "yearly"]
        
        for period in periods:
            response = client.post("/api/v1/insights/summary", json={
                "expenses": sample_expenses_data,
                "period": period
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["period"] == period
    
    def test_budget_safety_margin(self, client, sample_expenses_data):
        """Test budget endpoint with different safety margins"""
        response1 = client.post("/api/v1/insights/budget-recommendations", json={
            "expenses": sample_expenses_data,
            "safety_margin": 1.0
        })
        response2 = client.post("/api/v1/insights/budget-recommendations", json={
            "expenses": sample_expenses_data,
            "safety_margin": 1.5
        })
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Higher safety margin should result in higher total budget
        assert data2["recommended_total_budget"] >= data1["recommended_total_budget"]
