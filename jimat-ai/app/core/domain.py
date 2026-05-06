"""Domain-agnostic type definitions"""
from typing import TypedDict, List, Dict, Any, Optional, Literal
from dataclasses import dataclass
from datetime import datetime


class CategorizationResult(TypedDict, total=False):
    """Result from any domain's categorization"""
    category: str
    confidence: float
    explanation: str
    alternatives: List[Dict[str, Any]]


class InsightResult(TypedDict, total=False):
    """Result from insight generation"""
    period: Literal["daily", "weekly", "monthly"]
    summary: str
    metrics: Dict[str, Any]
    trends: Dict[str, Any]
    insights: List[Dict[str, str]]


@dataclass
class DocumentInput:
    """Standardized document input from user"""
    content_type: Literal["image", "text", "speech"]
    content: str  # base64 for image, plain text for text/speech
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ProcessingStep:
    """Metadata about a processing step"""
    step: str
    duration_ms: int
    status: Literal["success", "error", "skipped"] = "success"
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


class ConversationMessage(TypedDict, total=False):
    """A single message in conversation history"""
    role: Literal["user", "assistant"]
    content: str
    timestamp: str
    metadata: Dict[str, Any]
