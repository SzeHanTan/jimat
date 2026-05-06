"""Agent conversation state management"""
from typing import TypedDict, List, Dict, Any


class ConversationState(TypedDict, total=False):
    """Shared state across all agents in multi-turn conversation"""
    
    # Request Context
    user_id: str
    input: str
    conversation_id: str
    
    # Conversation History
    conversation_history: List[Dict[str, str]]  # [{"role": "user", "content": "..."}, ...]
    
    # Router Output
    detected_domain: str  # "expenses" | "insurance" | "insights"
    detected_intent: str  # "categorize" | "analyze" | "query" | etc
    router_confidence: float
    
    # Agent Routing
    selected_agent: str  # "expense_agent" | "insurance_agent" | "insights_agent" | "clarify"
    
    # Agent Processing
    agent_response: Dict[str, Any]
    agent_error: str
    
    # Final Output
    final_answer: str
    success: bool
    
    # Metadata
    processing_chain: List[Dict[str, Any]]  # Metadata: steps executed with timing
    total_duration_ms: int
