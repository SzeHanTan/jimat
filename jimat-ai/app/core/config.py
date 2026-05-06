"""Core configuration and settings"""
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App Settings
    app_name: str = "Jimat AI Service"
    debug: bool = True
    port: int = 8001
    
    # LLM Configuration
    llm_provider: Literal["huggingface", "gemini", "ollama"] = "huggingface"
    hf_api_key: str = ""
    hf_model: str = "mistral-7b-instruct"
    gemini_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    
    # Service URLs
    main_app_url: str = "http://localhost:8000"
    ai_service_url: str = "http://localhost:8001"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    enable_memory: bool = False
    
    # Database Configuration
    database_url: str = ""
    
    # Confidence Thresholds
    router_confidence_threshold: float = 0.7
    categorization_confidence_threshold: float = 0.7
    
    # Model Settings
    max_tokens: int = 500
    temperature: float = 0.3
    top_p: float = 0.9
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Available domains for routing
SUPPORTED_DOMAINS = {
    "expenses": {
        "name": "Expenses",
        "description": "Expense tracking, categorization, budgeting",
        "keywords": ["spent", "expense", "receipt", "cost", "charge", "category", "budget", "spending"]
    },
    "insurance": {
        "name": "Insurance",
        "description": "Insurance claims, coverage, policies",
        "keywords": ["claim", "insurance", "policy", "coverage", "medical", "auto", "home", "injury"]
    },
    "insights": {
        "name": "Insights",
        "description": "Financial analytics, trends, patterns",
        "keywords": ["summary", "insight", "trend", "analysis", "weekly", "monthly", "daily", "report", "statistic"]
    }
}

# Intents that can be detected
SUPPORTED_INTENTS = {
    "categorize": "Classify or categorize an item",
    "analyze": "Analyze data or detect patterns",
    "query": "Answer a question about data",
    "create": "Create or add a new item",
    "update": "Update or modify an item",
    "delete": "Remove or delete an item",
    "summarize": "Generate a summary or report",
    "assess": "Assess or evaluate something",
    "validate": "Validate or check something"
}
