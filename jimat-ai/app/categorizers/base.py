"""Base categorizer interface"""

from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class CategorizationResult:
    """Result of expense categorization"""
    category: str  # Primary category
    confidence: float  # 0-1 confidence score
    explanation: str  # Why this category
    alternatives: List[str]  # Other possible categories
    metadata: dict  # Additional info (amount, date, etc.)


class BaseCategorizer(ABC):
    """Abstract base class for expense categorizers"""
    
    @abstractmethod
    def categorize(
        self,
        description: str,
        amount: Optional[float] = None,
        date: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> CategorizationResult:
        """
        Categorize an expense based on description and optional metadata.
        
        Args:
            description: Expense description (from OCR or manual entry)
            amount: Expense amount (optional)
            date: Transaction date (optional)
            user_id: User ID for personalization (optional)
        
        Returns:
            CategorizationResult with category, confidence, and alternatives
        """
        pass
    
    @abstractmethod
    def get_supported_categories(self) -> List[str]:
        """Get list of supported expense categories"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if categorizer is available/healthy"""
        pass
