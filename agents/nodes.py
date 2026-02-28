"""
LangGraph Agent Nodes
Each node performs a specific task in the agent workflow
"""

import json
import logging
import anthropic
from typing import Dict
from django.conf import settings
from .state import AgentState, get_context_string
from .prompts import (
    INTENT_DETECTION_PROMPT,
    RESPONSE_GENERATION_PROMPT,
    GREETING_RESPONSE_TEMPLATE,
    ERROR_RESPONSE_TEMPLATE,
    NO_RESULTS_FAQ_TEMPLATE,
    TRACKING_NOT_FOUND_TEMPLATE
)
from rag.retriever import FAQRetriever
from services.dhl_api import DHLTrackingClient

logger = logging.getLogger('chatbot')


# Initialize tools
faq_retriever = FAQRetriever()
dhl_client = DHLTrackingClient()
anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def intent_analysis_node(state: AgentState) -> AgentState:
    """
    Analyze user message to detect intent using Claude
    
    Args:
        state: Current agent state
    
    Returns:
        AgentState: Updated state with intent information
    """
    try:
        logger.info(f"🔍 Analyzing intent for: {state['user_message'][:50]}...")
        
        # Get conversation context
        context = get_context_string(state)
        
        # Build prompt
        prompt = INTENT_DETECTION_PROMPT.format(
            user_message=state['user_message'],
            context=context if context else "No previous context"
        )
        
        # Call Claude for intent detection
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            temperature=0.3,  # Lower temperature for more consistent intent detection
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse JSON response
        result_text = response.content[0].text.strip()
        
        # Extract JSON from response (handle markdown wrapping)
        try:
            # Try direct JSON parse first
            result = json.loads(result_text)
        except json.JSONDecodeError:
            # Try to extract JSON if wrapped in markdown
            if "```json" in result_text:
                json_start = result_text.find("```json") + 7
                json_end = result_text.find("```", json_start)
                result_text = result_text[json_start:json_end].strip()
                result = json.loads(result_text)
            elif "```" in result_text:
                # Remove any code block markers
                result_text = result_text.replace("```", "").strip()
                result = json.loads(result_text)
            else:
                raise ValueError(f"Could not parse intent response: {result_text}")
        
        # Update state with intent information
        state['detected_intent'] = result.get('intent', 'unknown')
        state['intent_confidence'] = float(result.get('confidence', 0.0))
        state['tracking_number'] = result.get('tracking_number')
        state['faq_query'] = result.get('faq_query')
        
        logger.info(f"✅ Intent: {state['detected_intent']} (confidence: {state['intent_confidence']:.2f})")
        
        if state['tracking_number']:
            logger.info(f"📦 Tracking number extracted: {state['tracking_number']}")
        
        if state['faq_query']:
            logger.info(f"❓ FAQ query: {state['faq_query'][:50]}...")
        
        return state
        
    except Exception as e:
        logger.error(f"❌ Error in intent analysis: {str(e)}", exc_info=True)
        state['error'] = f"Intent analysis failed: {str(e)}"
        state['detected_intent'] = 'unknown'
        state['intent_confidence'] = 0.0
        return state


def faq_retrieval_node(state: AgentState) -> AgentState:
    """
    Retrieve relevant FAQs from Pinecone vector database
    
    Args:
        state: Current agent state
    
    Returns:
        AgentState: Updated state with FAQ results
    """
    try:
        if state['detected_intent'] != 'faq':
            logger.info("⏭️  Skipping FAQ retrieval (intent not 'faq')")
            return state
        
        # Use FAQ query if available, otherwise use original message
        query = state['faq_query'] or state['user_message']
        logger.info(f"🔎 Retrieving FAQs for: {query[:50]}...")
        
        # Retrieve FAQs from Pinecone
        results = faq_retriever.retrieve(
            query=query,
            top_k=3,
            min_score=0.7
        )
        
        state['faq_results'] = results
        state['tools_used'].append('faq_retriever')
        
        logger.info(f"✅ Retrieved {len(results)} relevant FAQs")
        
        # Log FAQ matches for debugging
        for i, faq in enumerate(results, 1):
            logger.debug(f"  FAQ {i}: {faq['question'][:60]}... (score: {faq['score']:.3f})")
        
        return state
        
    except Exception as e:
        logger.error(f"❌ Error retrieving FAQs: {str(e)}", exc_info=True)
        state['error'] = f"FAQ retrieval failed: {str(e)}"
        return state


def dhl_tracking_node(state: AgentState) -> AgentState:
    """
    Track DHL shipment using tracking number
    
    Args:
        state: Current agent state
    
    Returns:
        AgentState: Updated state with tracking results
    """
    try:
        if state['detected_intent'] != 'dhl_tracking':
            logger.info("⏭️  Skipping DHL tracking (intent not 'dhl_tracking')")
            return state
        
        tracking_number = state['tracking_number']
        
        if not tracking_number:
            logger.warning("⚠️  No tracking number found in message")
            state['error'] = "No tracking number found"
            state['dhl_tracking_result'] = {
                'success': False,
                'error': 'No tracking number provided'
            }
            return state
        
        logger.info(f"📦 Tracking DHL shipment: {tracking_number}")
        
        # Track shipment
        result = dhl_client.track_shipment(tracking_number)
        
        state['dhl_tracking_result'] = result
        state['tools_used'].append('dhl_tracker')
        
        if result.get('success'):
            logger.info(f"✅ Tracking successful: {result['status']}")
        else:
            logger.warning(f"⚠️  Tracking failed: {result.get('error')}")
        
        return state
        
    except Exception as e:
        logger.error(f"❌ Error tracking shipment: {str(e)}", exc_info=True)
        state['error'] = f"Shipment tracking failed: {str(e)}"
        state['dhl_tracking_result'] = {
            'success': False,
            'error': str(e)
        }
        return state


def response_generation_node(state: AgentState) -> AgentState:
    """
    Generate final response using Claude based on tool results
    
    Args:
        state: Current agent state
    
    Returns:
        AgentState: Updated state with final response
    """
    try:
        logger.info("💬 Generating final response...")
        
        # Handle greetings directly
        if state['detected_intent'] == 'greeting':
            state['final_response'] = GREETING_RESPONSE_TEMPLATE
            logger.info("👋 Using greeting template")
            return state
        
        # Handle errors
        if state['error']:
            state['final_response'] = ERROR_RESPONSE_TEMPLATE
            logger.warning("⚠️  Using error template")
            return state
        
        # Prepare tool results for prompt
        tool_results = _format_tool_results(state)
        
        # Get conversation context
        context = get_context_string(state)
        
        # Build response generation prompt
        prompt = RESPONSE_GENERATION_PROMPT.format(
            user_message=state['user_message'],
            intent=state['detected_intent'],
            tool_results=tool_results,
            context=context if context else "No previous context"
        )
        
        # Generate response with Claude
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        
        final_response = response.content[0].text.strip()
        
        state['final_response'] = final_response
        
        logger.info(f"✅ Response generated ({len(final_response)} chars)")
        logger.debug(f"Response preview: {final_response[:100]}...")
        
        return state
        
    except Exception as e:
        logger.error(f"❌ Error generating response: {str(e)}", exc_info=True)
        state['error'] = f"Response generation failed: {str(e)}"
        state['final_response'] = ERROR_RESPONSE_TEMPLATE
        return state


def error_handler_node(state: AgentState) -> AgentState:
    """
    Handle errors and generate fallback response
    
    Args:
        state: Current agent state
    
    Returns:
        AgentState: Updated state with error response
    """
    if state['error']:
        logger.error(f"🚨 Error in agent workflow: {state['error']}")
        
        # Provide specific error messages based on context
        if 'tracking' in state['error'].lower():
            state['final_response'] = TRACKING_NOT_FOUND_TEMPLATE
        elif 'faq' in state['error'].lower() or 'retrieval' in state['error'].lower():
            state['final_response'] = NO_RESULTS_FAQ_TEMPLATE
        else:
            state['final_response'] = ERROR_RESPONSE_TEMPLATE
        
        logger.info("ℹ️  Using fallback error response")
    
    return state


def _format_tool_results(state: AgentState) -> str:
    """
    Format tool results into readable text for prompt
    
    Args:
        state: Current agent state
    
    Returns:
        str: Formatted tool results
    """
    tool_results = ""
    
    # Format FAQ results
    if state['faq_results']:
        tool_results += "=== FAQ KNOWLEDGE BASE RESULTS ===\n\n"
        
        if len(state['faq_results']) == 0:
            tool_results += "No relevant FAQs found.\n"
        else:
            for i, faq in enumerate(state['faq_results'], 1):
                tool_results += f"FAQ {i} (Relevance: {faq['score']:.0%}):\n"
                tool_results += f"Question: {faq['question']}\n"
                tool_results += f"Answer: {faq['answer']}\n"
                tool_results += f"Category: {faq['category']}\n"
                tool_results += "\n"
    
    # Format DHL tracking results
    if state['dhl_tracking_result']:
        tool_results += "=== DHL TRACKING RESULTS ===\n\n"
        
        tracking_data = state['dhl_tracking_result']
        
        if tracking_data.get('success'):
            # Use the formatted tracking response
            formatted = dhl_client.format_tracking_response(tracking_data)
            tool_results += formatted + "\n"
        else:
            error_msg = tracking_data.get('error', 'Unknown error')
            tool_results += f"❌ Tracking Error: {error_msg}\n"
            tool_results += "Tracking number may be invalid or not found in system.\n"
    
    # If no tool results
    if not tool_results:
        tool_results = "No tool results available. Respond based on general knowledge about Chakancha Global."
    
    return tool_results