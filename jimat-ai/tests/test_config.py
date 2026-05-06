"""Tests for configuration and settings"""

import pytest
from app.core.config import Settings, get_settings, SUPPORTED_DOMAINS, SUPPORTED_INTENTS


class TestSettings:
    """Test Settings configuration class"""
    
    def test_settings_defaults(self):
        """Test default settings values"""
        settings = Settings()
        assert settings.app_name == "Jimat AI Service"
        assert settings.debug == True
        assert settings.port == 8001
        assert settings.llm_provider == "huggingface"
        assert settings.temperature == 0.3
    
    def test_settings_from_env(self, monkeypatch):
        """Test loading settings from environment variables"""
        monkeypatch.setenv("APP_NAME", "Test App")
        monkeypatch.setenv("DEBUG", "False")
        monkeypatch.setenv("PORT", "9000")
        
        settings = Settings()
        assert settings.app_name == "Test App"
        assert settings.debug == False
        assert settings.port == 9000
    
    def test_settings_thresholds(self):
        """Test confidence thresholds"""
        settings = get_settings()
        assert settings.router_confidence_threshold == 0.7
        assert settings.categorization_confidence_threshold == 0.7
        assert 0 <= settings.temperature <= 1
    
    def test_supported_domains(self):
        """Test supported domains configuration"""
        assert "expenses" in SUPPORTED_DOMAINS
        assert "insurance" in SUPPORTED_DOMAINS
        assert "insights" in SUPPORTED_DOMAINS
        
        # Check domain structure
        for domain_key, domain_info in SUPPORTED_DOMAINS.items():
            assert "name" in domain_info
            assert "description" in domain_info
            assert "keywords" in domain_info
            assert isinstance(domain_info["keywords"], list)
    
    def test_supported_intents(self):
        """Test supported intents configuration"""
        assert "categorize" in SUPPORTED_INTENTS
        assert "analyze" in SUPPORTED_INTENTS
        assert "query" in SUPPORTED_INTENTS
        
        # Each intent should have a description
        for intent_key, intent_desc in SUPPORTED_INTENTS.items():
            assert isinstance(intent_desc, str)
            assert len(intent_desc) > 0
    
    def test_settings_singleton(self):
        """Test that get_settings returns cached instance"""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2  # Should be same object


class TestLLMConfiguration:
    """Test LLM provider configuration"""
    
    def test_llm_provider_options(self):
        """Test that LLM provider is one of supported options"""
        settings = get_settings()
        supported = ["huggingface", "gemini", "ollama"]
        assert settings.llm_provider in supported
    
    def test_model_parameters(self):
        """Test model parameter ranges"""
        settings = get_settings()
        assert settings.max_tokens > 0
        assert 0 <= settings.temperature <= 1
        assert 0 <= settings.top_p <= 1
