"""
LangGraph Agent State Schema
Defines the state structure for the chatbot agent
"""

from typing import TypedDict, List, Dict, Optional, Literal
from datetime import datetime


class Message(TypedDict):
    """Single message in conversation"""
    role: Literal['user', 'assistant', 'system']
    content: str
    timestamp: str


class AgentState(TypedDict):
    """
    Complete state for the chatbot agent
    Tracks conversation context, intent, and tool results
    """
    
    # Current user message
    user_message: str
    
    # Conversation history (last 10 messages)
    conversation_history: List[Message]
    
    # Session information
    session_id: str
    
    # Intent detection
    detected_intent: Optional[Literal['faq', 'dhl_tracking', 'general_chat', 'greeting', 'unknown']]
    intent_confidence: float
    
    # Extracted entities
    tracking_number: Optional[str]
    faq_query: Optional[str]
    
    # Tool results
    faq_results: Optional[List[Dict]]
    dhl_tracking_result: Optional[Dict]
    
    # Final response
    final_response: str
    
    # Metadata
    response_time_ms: int
    tools_used: List[str]
    
    # Error handling
    error: Optional[str]


def create_initial_state(
    user_message: str,
    session_id: str,
    conversation_history: Optional[List[Message]] = None
) -> AgentState:
    """
    Create initial agent state for a new message
    
    Args:
        user_message: Current user message
        session_id: Session UUID
        conversation_history: Previous messages (optional)
    
    Returns:
        AgentState: Initialized state
    """
    return AgentState(
        user_message=user_message,
        conversation_history=conversation_history or [],
        session_id=session_id,
        detected_intent=None,
        intent_confidence=0.0,
        tracking_number=None,
        faq_query=None,
        faq_results=None,
        dhl_tracking_result=None,
        final_response='',
        response_time_ms=0,
        tools_used=[],
        error=None
    )


def add_message_to_history(
    state: AgentState,
    role: Literal['user', 'assistant'],
    content: str
) -> AgentState:
    """
    Add a message to conversation history (keep last 10)
    
    Args:
        state: Current agent state
        role: Message role
        content: Message content
    
    Returns:
        AgentState: Updated state with new message
    """
    new_message = Message(
        role=role,
        content=content,
        timestamp=datetime.now().isoformat()
    )
    
    # Add to history
    history = state['conversation_history'] + [new_message]
    
    # Keep only last 10 messages
    if len(history) > 10:
        history = history[-10:]
    
    state['conversation_history'] = history
    return state


def get_context_string(state: AgentState) -> str:
    """
    Convert conversation history to string context
    
    Args:
        state: Current agent state
    
    Returns:
        str: Formatted conversation history
    """
    if not state['conversation_history']:
        return ""
    
    context = "Previous conversation:\n"
    for msg in state['conversation_history'][-5:]:  # Last 5 messages
        role = msg['role'].capitalize()
        content = msg['content']
        context += f"{role}: {content}\n"
    
    return context