"""
DRF Serializers for Chatbot API
Validates incoming data and formats outgoing data
"""

from rest_framework import serializers
from .models import Conversation, Message, Feedback
import uuid


class ChatMessageSerializer(serializers.Serializer):
    """
    Serializer for incoming chat messages from frontend
    Matches frontend api.js sendMessage() function
    """
    message = serializers.CharField(
        max_length=2000,
        required=True,
        trim_whitespace=True,
        help_text="User message content"
    )
    session_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text="Session UUID (auto-generated if not provided)"
    )
    
    def validate_message(self, value):
        """Validate message is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        return value.strip()
    
    def validate(self, data):
        """Generate session ID if not provided"""
        if not data.get('session_id'):
            data['session_id'] = uuid.uuid4()
        return data


class FeedbackSerializer(serializers.Serializer):
    """
    Serializer for user feedback (thumbs up/down)
    Matches frontend api.js submitFeedback() function
    """
    session_id = serializers.UUIDField(
        required=True,
        help_text="Session UUID"
    )
    message_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text="Specific message ID (optional)"
    )
    rating = serializers.IntegerField(
        required=True,
        help_text="Rating: 1 for thumbs up, -1 for thumbs down"
    )
    comment = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=500,
        help_text="Optional feedback comment"
    )
    
    def validate_rating(self, value):
        """Ensure rating is 1 or -1"""
        if value not in [1, -1]:
            raise serializers.ValidationError(
                "Rating must be 1 (thumbs up) or -1 (thumbs down)"
            )
        return value


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model
    Used for returning message history
    """
    session_id = serializers.UUIDField(source='session.session_id', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'message_id',
            'session_id',
            'role',
            'content',
            'timestamp',
            'metadata'
        ]
        read_only_fields = ['message_id', 'timestamp']


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model with messages
    Used for returning full conversation history
    """
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'session_id',
            'created_at',
            'updated_at',
            'message_count',
            'language',
            'status',
            'user_metadata',
            'messages'
        ]
        read_only_fields = [
            'session_id',
            'created_at',
            'updated_at',
            'message_count'
        ]


class HealthCheckSerializer(serializers.Serializer):
    """
    Serializer for health check response
    """
    status = serializers.CharField()
    timestamp = serializers.DateTimeField()
    database = serializers.CharField()
    service = serializers.CharField()
    version = serializers.CharField()