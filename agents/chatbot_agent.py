"""
LangGraph Chatbot Agent
Main agent orchestration with StateGraph workflow
"""

import time
import logging
from langgraph.graph import StateGraph, END
from .state import AgentState, create_initial_state, add_message_to_history
from .nodes import (
    intent_analysis_node,
    faq_retrieval_node,
    dhl_tracking_node,
    response_generation_node,
    error_handler_node
)

logger = logging.getLogger('chatbot')


def route_after_intent(state: AgentState) -> str:
    """
    Route to appropriate tool based on detected intent
    
    Args:
        state: Current agent state
    
    Returns:
        str: Next node name to execute
    """
    intent = state['detected_intent']
    
    # Handle errors first
    if state['error']:
        logger.info(f"🔀 Routing to error_handler due to error")
        return "error_handler"
    
    # Route based on intent
    if intent == 'faq':
        logger.info(f"🔀 Routing to FAQ retrieval")
        return "faq_retrieval"
    
    elif intent == 'dhl_tracking':
        logger.info(f"🔀 Routing to DHL tracking")
        return "dhl_tracking"
    
    elif intent in ['greeting', 'general_chat', 'unknown']:
        logger.info(f"🔀 Routing directly to response generation")
        return "response_generation"
    
    else:
        logger.warning(f"⚠️  Unknown intent: {intent}, routing to response generation")
        return "response_generation"


def route_after_tools(state: AgentState) -> str:
    """
    Route after tool execution (always go to response generation)
    
    Args:
        state: Current agent state
    
    Returns:
        str: Next node name (always response_generation or error_handler)
    """
    if state['error']:
        logger.info(f"🔀 Routing to error_handler after tool execution")
        return "error_handler"
    
    logger.info(f"🔀 Routing to response generation after tool execution")
    return "response_generation"


# ============================================
# BUILD THE STATERGRAPH WORKFLOW
# ============================================

logger.info("🏗️  Building LangGraph StateGraph workflow...")

# Initialize StateGraph with AgentState type
workflow = StateGraph(AgentState)

# Add all nodes to the graph
workflow.add_node("intent_analysis", intent_analysis_node)
workflow.add_node("faq_retrieval", faq_retrieval_node)
workflow.add_node("dhl_tracking", dhl_tracking_node)
workflow.add_node("response_generation", response_generation_node)
workflow.add_node("error_handler", error_handler_node)

# Set the entry point (first node to execute)
workflow.set_entry_point("intent_analysis")

# Add conditional routing after intent analysis
workflow.add_conditional_edges(
    "intent_analysis",
    route_after_intent,
    {
        "faq_retrieval": "faq_retrieval",
        "dhl_tracking": "dhl_tracking",
        "response_generation": "response_generation",
        "error_handler": "error_handler"
    }
)

# Tool nodes always go to response generation
workflow.add_edge("faq_retrieval", "response_generation")
workflow.add_edge("dhl_tracking", "response_generation")

# Response generation and error handler end the workflow
workflow.add_edge("response_generation", END)
workflow.add_edge("error_handler", END)

# Compile the graph into an executable app
app = workflow.compile()

logger.info("✅ LangGraph workflow compiled successfully!")

# ============================================
# MAIN AGENT INTERFACE
# ============================================


def process_message(
    user_message: str,
    session_id: str,
    conversation_history: list = None
) -> dict:
    """
    Process a user message through the complete agent workflow
    
    Args:
        user_message (str): User's input message
        session_id (str): Session UUID for tracking
        conversation_history (list): Previous messages in conversation
    
    Returns:
        dict: Response with message and metadata
            {
                'reply': str,
                'session_id': str,
                'response_time_ms': int,
                'intent': str,
                'tools_used': list,
                'conversation_history': list,
                'error': str (optional)
            }
    """
    start_time = time.time()
    
    try:
        logger.info(f"\n{'='*70}")
        logger.info(f"🤖 PROCESSING MESSAGE")
        logger.info(f"{'='*70}")
        logger.info(f"Session: {session_id}")
        logger.info(f"Message: {user_message[:100]}...")
        
        # Create initial agent state
        initial_state = create_initial_state(
            user_message=user_message,
            session_id=session_id,
            conversation_history=conversation_history
        )
        
        logger.info(f"📋 Initial state created with {len(conversation_history or [])} previous messages")
        
        # Run the message through the agent workflow
        logger.info("🚀 Starting agent workflow...")
        final_state = app.invoke(initial_state)
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        final_state['response_time_ms'] = response_time_ms
        
        # Add current exchange to conversation history
        final_state = add_message_to_history(final_state, 'user', user_message)
        final_state = add_message_to_history(final_state, 'assistant', final_state['final_response'])
        
        logger.info(f"✅ Agent workflow completed in {response_time_ms}ms")
        logger.info(f"Intent: {final_state['detected_intent']}")
        logger.info(f"Tools used: {final_state['tools_used']}")
        logger.info(f"Response length: {len(final_state['final_response'])} chars")
        logger.info(f"{'='*70}\n")
        
        # Prepare response
        response = {
            'reply': final_state['final_response'],
            'session_id': session_id,
            'response_time_ms': response_time_ms,
            'intent': final_state['detected_intent'],
            'tools_used': final_state['tools_used'],
            'conversation_history': final_state['conversation_history']
        }
        
        # Include error if present
        if final_state.get('error'):
            response['error'] = final_state['error']
            logger.warning(f"⚠️  Response includes error: {final_state['error']}")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Critical error processing message: {str(e)}", exc_info=True)
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        return {
            'reply': "I apologize, but I'm experiencing technical difficulties right now. Please try again in a moment, or contact our support team at support@chakancha.com for immediate assistance.",
            'session_id': session_id,
            'response_time_ms': response_time_ms,
            'intent': 'unknown',
            'tools_used': [],
            'conversation_history': conversation_history or [],
            'error': str(e)
        }


def get_workflow_diagram() -> str:
    """
    Get a text representation of the workflow graph
    
    Returns:
        str: ASCII diagram of the workflow
    """
    diagram = """
    LangGraph Agent Workflow:
    
    ┌─────────────────┐
    │  User Message   │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Intent Analysis │ (Claude analyzes message)
    └────────┬────────┘
             │
             ├─── FAQ Intent ──────► ┌──────────────┐
             │                       │ FAQ Retrieval│ (Pinecone search)
             │                       └──────┬───────┘
             │                              │
             ├─── DHL Intent ──────► ┌──────────────┐
             │                       │ DHL Tracking │ (API call)
             │                       └──────┬───────┘
             │                              │
             ├─── Greeting/Chat ───────────┼─────────────┐
             │                              │             │
             │                              ▼             ▼
             │                       ┌────────────────────────┐
             │                       │ Response Generation    │ (Claude generates reply)
             │                       └───────────┬────────────┘
             │                                   │
             ▼                                   ▼
    ┌────────────────┐                  ┌──────────────┐
    │ Error Handler  │                  │   END        │
    └────────┬───────┘                  └──────────────┘
             │
             ▼
    ┌──────────────┐
    │   END        │
    └──────────────┘
    """
    return diagram


# ============================================
# TESTING INTERFACE
# ============================================


def test_agent(test_messages: list = None):
    """
    Test the agent with sample messages
    
    Args:
        test_messages (list): Optional list of test messages
    """
    if test_messages is None:
        test_messages = [
            "Hello!",
            "What teas do you sell?",
            "Track my shipment TEST123",
            "How much does your tea cost?",
            "What is the Chakan Tree program?"
        ]
    
    print("\n" + "="*70)
    print("🧪 TESTING LANGGRAPH AGENT")
    print("="*70 + "\n")
    
    session_id = "test-session-123"
    conversation_history = []
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{'─'*70}")
        print(f"Test {i}/{len(test_messages)}: {message}")
        print(f"{'─'*70}\n")
        
        result = process_message(
            user_message=message,
            session_id=session_id,
            conversation_history=conversation_history
        )
        
        print(f"Intent: {result['intent']}")
        print(f"Tools Used: {result['tools_used']}")
        print(f"Response Time: {result['response_time_ms']}ms")
        print(f"\nReply:\n{result['reply']}\n")
        
        # Update conversation history for next test
        conversation_history = result['conversation_history']
    
    print("="*70)
    print("✅ AGENT TESTING COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Run tests if executed directly
    test_agent()