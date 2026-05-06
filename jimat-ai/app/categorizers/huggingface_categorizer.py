"""Hugging Face LLM-based expense categorizer"""

import logging
import os
from typing import List, Optional
from functools import lru_cache

from app.categorizers.base import BaseCategorizer, CategorizationResult
from app.core.config import get_settings

logger = logging.getLogger(__name__)


# Common expense categories (can be extended)
EXPENSE_CATEGORIES = {
    "Food & Dining": ["restaurant", "coffee", "grocery", "food", "lunch", "dinner", "breakfast", "cafe"],
    "Transportation": ["taxi", "uber", "fuel", "gas", "parking", "metro", "bus", "train", "flight"],
    "Utilities": ["electricity", "water", "internet", "phone", "utility", "bills", "bill", "electric"],
    "Entertainment": ["movie", "concert", "game", "entertainment", "streaming", "netflix", "spotify"],
    "Shopping": ["amazon", "mall", "store", "shopping", "clothes", "apparel", "purchase"],
    "Health": ["pharmacy", "doctor", "hospital", "medicine", "health", "dental", "gym"],
    "Travel": ["hotel", "airbnb", "resort", "vacation", "travel", "lodging"],
    "Work": ["office", "supply", "stationery", "work", "business", "conference"],
    "Education": ["school", "course", "book", "tuition", "education", "training"],
    "Personal": ["haircut", "salon", "personal", "care"],
}


class HuggingFaceCategorizer(BaseCategorizer):
    """Expense categorizer using Hugging Face LLM with keyword fallback"""
    
    def __init__(self):
        """Initialize Hugging Face categorizer"""
        settings = get_settings()
        self.api_key = os.getenv("HF_API_KEY", settings.hf_api_key)
        self.model_id = settings.hf_model
        self.base_url = "https://api-inference.huggingface.co/models"
        self.available = self._check_availability()
        
        if self.available:
            logger.info(f"HuggingFace categorizer initialized with model: {self.model_id}")
        else:
            logger.warning("HuggingFace categorizer unavailable - will use keyword fallback")
    
    def _check_availability(self) -> bool:
        """Check if HF API is available"""
        if not self.api_key:
            logger.warning("HF_API_KEY not configured - using keyword fallback only")
            return False
        
        try:
            import requests
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            # Test with a simple request
            response = requests.post(
                f"{self.base_url}/{self.model_id}",
                headers=headers,
                json={"inputs": "test"},
                timeout=5
            )
            
            # 503 = model loading, which is fine
            return response.status_code in [200, 503]
        except Exception as e:
            logger.warning(f"HF API availability check failed: {str(e)}")
            return False
    
    def _get_llm_category(self, description: str) -> Optional[CategorizationResult]:
        """Try to categorize using LLM"""
        if not self.available or not self.api_key:
            return None
        
        try:
            import requests
            
            # Create a prompt for the LLM
            prompt = f"""Categorize this expense into ONE of these categories: {', '.join(EXPENSE_CATEGORIES.keys())}

Expense description: {description}

Respond with ONLY the category name, nothing else."""
            
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.post(
                f"{self.base_url}/{self.model_id}",
                headers=headers,
                json={"inputs": prompt, "parameters": {"max_new_tokens": 20}},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Parse response
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "").strip()
                    
                    # Extract category from response
                    for category in EXPENSE_CATEGORIES.keys():
                        if category.lower() in generated_text.lower():
                            return CategorizationResult(
                                category=category,
                                confidence=0.85,  # LLM confidence
                                explanation=f"LLM categorized based on description: '{description}'",
                                alternatives=self._get_alternatives(category, generated_text),
                                metadata={"method": "llm", "model": self.model_id}
                            )
            
            logger.debug(f"LLM response status: {response.status_code}")
            return None
            
        except Exception as e:
            logger.debug(f"LLM categorization failed: {str(e)}")
            return None
    
    def _categorize_by_keywords(self, description: str) -> CategorizationResult:
        """Fallback: categorize using keyword matching"""
        description_lower = description.lower()
        scores = {}
        
        for category, keywords in EXPENSE_CATEGORIES.items():
            matches = sum(1 for keyword in keywords if keyword in description_lower)
            if matches > 0:
                scores[category] = matches
        
        if scores:
            best_category = max(scores, key=scores.get)
            confidence = min(scores[best_category] / 3.0, 1.0)  # Normalize to 0-1
            
            return CategorizationResult(
                category=best_category,
                confidence=confidence,
                explanation=f"Keyword match in description: '{description}'",
                alternatives=sorted(
                    [c for c in scores if c != best_category],
                    key=lambda x: scores[x],
                    reverse=True
                )[:2],
                metadata={"method": "keyword", "keyword_matches": scores[best_category]}
            )
        
        # Default fallback
        return CategorizationResult(
            category="Other",
            confidence=0.3,
            explanation="No matching keywords found",
            alternatives=["Food & Dining", "Shopping", "Entertainment"],
            metadata={"method": "default"}
        )
    
    def _get_alternatives(self, primary_category: str, context: str) -> List[str]:
        """Get alternative categories based on context"""
        alternatives = []
        context_lower = context.lower()
        
        for category in EXPENSE_CATEGORIES.keys():
            if category == primary_category:
                continue
            
            # Check if category keywords appear in context
            keywords = EXPENSE_CATEGORIES[category]
            if any(keyword in context_lower for keyword in keywords):
                alternatives.append(category)
        
        return alternatives[:2]  # Top 2 alternatives
    
    def categorize(
        self,
        description: str,
        amount: Optional[float] = None,
        date: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> CategorizationResult:
        """
        Categorize an expense using LLM with keyword fallback.
        
        Args:
            description: Expense description
            amount: Expense amount (optional)
            date: Transaction date (optional)
            user_id: User ID (optional)
        
        Returns:
            CategorizationResult with category and confidence
        """
        # Try LLM first
        if self.available:
            result = self._get_llm_category(description)
            if result:
                logger.info(f"LLM categorized '{description}' as '{result.category}' (confidence: {result.confidence})")
                return result
        
        # Fallback to keyword matching
        result = self._categorize_by_keywords(description)
        logger.info(f"Keyword categorized '{description}' as '{result.category}' (confidence: {result.confidence})")
        return result
    
    def get_supported_categories(self) -> List[str]:
        """Get list of supported expense categories"""
        return list(EXPENSE_CATEGORIES.keys())
    
    def is_available(self) -> bool:
        """Check if categorizer is available"""
        return True  # Always available (uses keyword fallback)


@lru_cache(maxsize=1)
def get_categorizer() -> HuggingFaceCategorizer:
    """Get singleton instance of HuggingFaceCategorizer"""
    return HuggingFaceCategorizer()
