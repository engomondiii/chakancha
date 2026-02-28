"""
Chatbot API Views
Matches the frontend API service (api.js) exactly
Includes rate limiting and comprehensive logging
NOW WITH FULL LANGGRAPH AGENT INTEGRATION
"""

from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import Conversation, Message, Feedback
from .serializers import (
    ChatMessageSerializer,
    FeedbackSerializer,
    ConversationSerializer,
    HealthCheckSerializer
)
import logging
import time

# Import LangGraph agent
from agents import process_message

logger = logging.getLogger('chatbot')


class ChatRateThrottle(AnonRateThrottle):
    """Custom rate throttle for chat endpoint"""
    rate = '60/minute'  # 60 requests per minute


@api_view(['POST'])
@throttle_classes([ChatRateThrottle])
def chat_endpoint(request):
    """
    Main chat endpoint - receives user message, returns AI response
    NOW USES FULL LANGGRAPH AGENT WITH FAQ + DHL TRACKING
    
    Frontend expects:
    Request: { "message": "...", "session_id": "..." }
    Response: { "reply": "...", "session_id": "...", "response_time_ms": 123 }
    """
    start_time = time.time()
    
    try:
        # Log incoming request
        logger.info(f"Chat request from {request.META.get('REMOTE_ADDR')}")
        
        # Validate request
        serializer = ChatMessageSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Invalid request data: {serializer.errors}")
            return Response({
                'error': 'Invalid request data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user_message = serializer.validated_data['message']
        session_id = serializer.validated_data['session_id']
        
        logger.info(f"Processing message for session {session_id}: '{user_message[:50]}...'")
        
        # Get or create conversation
        conversation, created = Conversation.objects.get_or_create(
            session_id=session_id,
            defaults={
                'language': 'en',
                'status': 'active',
                'user_metadata': {
                    'ip': request.META.get('REMOTE_ADDR'),
                    'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200]
                }
            }
        )
        
        if created:
            logger.info(f"✨ Created new conversation: {session_id}")
        
        # Save user message to database
        user_msg = Message.objects.create(
            session=conversation,
            role='user',
            content=user_message,
            metadata={
                'input_length': len(user_message),
                'ip': request.META.get('REMOTE_ADDR')
            }
        )
        
        # ============================================
        # LANGGRAPH AGENT INTEGRATION
        # ============================================
        
        # Get conversation history from database (last 10 messages)
        messages = Message.objects.filter(
            session=conversation
        ).order_by('timestamp')[:10]
        
        conversation_history = [
            {
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat()
            }
            for msg in messages
        ]
        
        logger.info(f"📚 Loaded {len(conversation_history)} previous messages for context")
        
        # Process message with LangGraph agent
        logger.info("🤖 Calling LangGraph agent...")
        
        agent_response = process_message(
            user_message=user_message,
            session_id=str(conversation.session_id),
            conversation_history=conversation_history
        )
        
        # Extract AI response
        ai_response = agent_response['reply']
        detected_intent = agent_response.get('intent', 'unknown')
        tools_used = agent_response.get('tools_used', [])
        agent_response_time = agent_response.get('response_time_ms', 0)
        
        logger.info(f"✅ Agent response received")
        logger.info(f"   Intent: {detected_intent}")
        logger.info(f"   Tools: {tools_used}")
        logger.info(f"   Agent time: {agent_response_time}ms")
        
        # ============================================
        # END LANGGRAPH INTEGRATION
        # ============================================
        
        # Save AI response to database
        ai_msg = Message.objects.create(
            session=conversation,
            role='assistant',
            content=ai_response,
            metadata={
                'response_length': len(ai_response),
                'intent': detected_intent,
                'tools_used': tools_used,
                'agent_response_time_ms': agent_response_time,
                'placeholder': False  # Real AI response!
            }
        )
        
        # Calculate total response time
        end_time = time.time()
        response_time_ms = int((end_time - start_time) * 1000)
        
        logger.info(f"✅ Chat response sent in {response_time_ms}ms total for session {session_id}")
        
        return Response({
            'reply': ai_response,
            'session_id': str(conversation.session_id),
            'response_time_ms': response_time_ms
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ Error in chat_endpoint: {str(e)}", exc_info=True)
        
        # Fallback error response
        return Response({
            'error': 'Internal server error',
            'message': 'I apologize, but I encountered an error processing your message. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@throttle_classes([ChatRateThrottle])
def feedback_endpoint(request):
    """
    Feedback endpoint - receives user feedback (thumbs up/down)
    
    Frontend expects:
    Request: { "session_id": "...", "rating": 1 or -1 }
    Response: { "success": true }
    """
    try:
        logger.info(f"Feedback request from {request.META.get('REMOTE_ADDR')}")
        
        # Validate request
        serializer = FeedbackSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Invalid feedback data: {serializer.errors}")
            return Response({
                'error': 'Invalid feedback data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        session_id = serializer.validated_data['session_id']
        rating = serializer.validated_data['rating']
        comment = serializer.validated_data.get('comment', '')
        message_id = serializer.validated_data.get('message_id')
        
        # Get conversation
        try:
            conversation = Conversation.objects.get(session_id=session_id)
        except Conversation.DoesNotExist:
            logger.warning(f"Feedback for non-existent session: {session_id}")
            return Response({
                'error': 'Session not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get message if provided
        message = None
        if message_id:
            try:
                message = Message.objects.get(message_id=message_id)
            except Message.DoesNotExist:
                pass  # Message ID is optional
        
        # Create feedback
        feedback = Feedback.objects.create(
            session=conversation,
            message=message,
            rating=rating,
            comment=comment
        )
        
        rating_emoji = '👍' if rating == 1 else '👎'
        logger.info(f"Feedback {rating_emoji} received for session {session_id}")
        
        return Response({
            'success': True,
            'message': 'Feedback received. Thank you!'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in feedback_endpoint: {str(e)}", exc_info=True)
        return Response({
            'error': 'Internal server error',
            'message': 'Failed to submit feedback.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint
    
    Frontend expects:
    Response: { "status": "healthy", "timestamp": "...", "database": "connected" }
    """
    try:
        # Test database connection
        conversation_count = Conversation.objects.count()
        message_count = Message.objects.count()
        db_status = 'connected'
        overall_status = 'healthy'
        
        logger.info("Health check passed")
        
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = 'disconnected'
        overall_status = 'degraded'
        conversation_count = 0
        message_count = 0
    
    response_data = {
        'status': overall_status,
        'timestamp': timezone.now().isoformat(),
        'database': db_status,
        'service': 'Chakancha AI Chatbot',
        'version': '1.0.0',
        'agent': 'LangGraph + Claude Sonnet 4',
        'features': ['FAQ Retrieval', 'DHL Tracking', 'Conversation Memory'],
        'stats': {
            'conversations': conversation_count,
            'messages': message_count
        }
    }
    
    return Response(
        response_data,
        status=status.HTTP_200_OK if overall_status == 'healthy' else status.HTTP_503_SERVICE_UNAVAILABLE
    )


# Optional: Get conversation history
@api_view(['GET'])
def conversation_history(request, session_id):
    """
    Get full conversation history for a session
    Optional endpoint - can be used by frontend for debugging
    """
    try:
        conversation = Conversation.objects.get(session_id=session_id)
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Conversation.DoesNotExist:
        return Response({
            'error': 'Conversation not found'
        }, status=status.HTTP_404_NOT_FOUND)