"""Tests for expense categorization"""

import pytest
from app.categorizers import get_categorizer, HuggingFaceCategorizer, CategorizationResult


class TestHuggingFaceCategorizer:
    """Test HuggingFace categorizer"""
    
    @pytest.fixture
    def categorizer(self):
        """Get categorizer instance"""
        return get_categorizer()
    
    def test_categorizer_initialization(self, categorizer):
        """Test categorizer initializes"""
        assert categorizer is not None
        assert isinstance(categorizer, HuggingFaceCategorizer)
    
    def test_categorizer_is_available(self, categorizer):
        """Test categorizer availability check"""
        assert categorizer.is_available() is True  # Always available (keyword fallback)
    
    def test_get_supported_categories(self, categorizer):
        """Test getting supported categories"""
        categories = categorizer.get_supported_categories()
        
        assert isinstance(categories, list)
        assert len(categories) > 0
        assert "Food & Dining" in categories
        assert "Transportation" in categories
    
    def test_categorize_food_expense(self, categorizer):
        """Test categorizing food expense"""
        result = categorizer.categorize("Starbucks coffee and pastry")
        
        assert isinstance(result, CategorizationResult)
        assert result.category == "Food & Dining"
        assert 0 <= result.confidence <= 1
        assert result.explanation is not None
    
    def test_categorize_transportation(self, categorizer):
        """Test categorizing transportation expense"""
        result = categorizer.categorize("Uber ride to downtown")
        
        assert result.category == "Transportation"
        assert result.confidence > 0.3
    
    def test_categorize_utilities(self, categorizer):
        """Test categorizing utilities expense"""
        result = categorizer.categorize("Electric bill payment")
        
        assert result.category == "Utilities"
    
    def test_categorize_shopping(self, categorizer):
        """Test categorizing shopping expense"""
        result = categorizer.categorize("Amazon purchase - laptop charger")
        
        assert result.category == "Shopping"
    
    def test_categorize_with_amount(self, categorizer):
        """Test categorization with amount"""
        result = categorizer.categorize(
            description="Dinner at restaurant",
            amount=45.50
        )
        
        assert result.category == "Food & Dining"
        assert result.metadata.get("amount") is None  # Amount not in metadata yet
    
    def test_categorize_with_date(self, categorizer):
        """Test categorization with date"""
        result = categorizer.categorize(
            description="Movie ticket",
            date="2024-05-05"
        )
        
        assert result.category == "Entertainment"
    
    def test_categorize_unknown_expense(self, categorizer):
        """Test categorizing unknown/generic expense"""
        result = categorizer.categorize("Random purchase XYZ")
        
        # Should still return a category
        assert result.category in categorizer.get_supported_categories()
        assert result.confidence > 0  # May be low confidence
    
    def test_categorize_empty_description_fallback(self, categorizer):
        """Test categorizing empty description"""
        result = categorizer.categorize("")
        
        # Should use default/fallback
        assert result.category is not None
    
    def test_categorization_result_structure(self, categorizer):
        """Test categorization result has all required fields"""
        result = categorizer.categorize("Coffee shop")
        
        assert hasattr(result, "category")
        assert hasattr(result, "confidence")
        assert hasattr(result, "explanation")
        assert hasattr(result, "alternatives")
        assert hasattr(result, "metadata")
        
        assert isinstance(result.category, str)
        assert isinstance(result.confidence, float)
        assert isinstance(result.explanation, str)
        assert isinstance(result.alternatives, list)
        assert isinstance(result.metadata, dict)
    
    def test_categorization_confidence_range(self, categorizer):
        """Test confidence is always in valid range"""
        expenses = [
            "Starbucks coffee",
            "Taxi",
            "Hospital visit",
            "Random item"
        ]
        
        for expense in expenses:
            result = categorizer.categorize(expense)
            assert 0 <= result.confidence <= 1, f"Invalid confidence for '{expense}': {result.confidence}"
    
    def test_categorizer_singleton(self):
        """Test categorizer is singleton"""
        cat1 = get_categorizer()
        cat2 = get_categorizer()
        
        assert cat1 is cat2  # Same instance


class TestKeywordFallback:
    """Test keyword-based fallback categorization"""
    
    @pytest.fixture
    def categorizer(self):
        return get_categorizer()
    
    def test_keyword_matching_food(self, categorizer):
        """Test keyword matching for food"""
        result = categorizer._categorize_by_keywords("restaurant dinner")
        assert result.category == "Food & Dining"
    
    def test_keyword_matching_transport(self, categorizer):
        """Test keyword matching for transport"""
        result = categorizer._categorize_by_keywords("taxi uber")
        assert result.category == "Transportation"
    
    def test_keyword_multiple_matches(self, categorizer):
        """Test when multiple keywords match"""
        result = categorizer._categorize_by_keywords("coffee restaurant food")
        
        # Should pick category with most matches
        assert result.category == "Food & Dining"
        assert result.confidence > 0
    
    def test_keyword_no_matches(self, categorizer):
        """Test when no keywords match"""
        result = categorizer._categorize_by_keywords("xyz123 abc")
        
        # Should fall back to default
        assert result.category == "Other"
        assert result.confidence == 0.3


class TestBatchCategorization:
    """Test batch categorization (if implemented)"""
    
    @pytest.fixture
    def categorizer(self):
        return get_categorizer()
    
    def test_batch_multiple_expenses(self, categorizer):
        """Test categorizing multiple expenses"""
        expenses = [
            "Starbucks coffee",
            "Uber ride",
            "Electric bill"
        ]
        
        results = []
        for desc in expenses:
            result = categorizer.categorize(desc)
            results.append(result)
        
        assert len(results) == 3
        assert results[0].category == "Food & Dining"
        assert results[1].category == "Transportation"
        assert results[2].category == "Utilities"
