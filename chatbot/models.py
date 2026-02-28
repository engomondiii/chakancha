"""
Database models for Chakancha chatbot
- Conversation: Chat sessions
- Message: Individual messages (user & AI)
- Feedback: User feedback (thumbs up/down)
"""

import uuid
from django.db import models
from django.utils import timezone


class Conversation(models.Model):
    """
    Represents a complete chat session with a user
    """
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('ko', 'Korean'),  # For future Phase 2
    ]
    
    # Primary key - UUID for security
    session_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique session identifier"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the conversation started"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last message timestamp"
    )
    
    # Metadata
    user_metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Browser info, location, etc. (JSON)"
    )
    
    # Stats
    message_count = models.IntegerField(
        default=0,
        help_text="Total number of messages in this conversation"
    )
    
    # Configuration
    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default='en',
        help_text="Conversation language"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text="Current conversation status"
    )
    
    class Meta:
        db_table = 'conversations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['language']),
        ]
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
    
    def __str__(self):
        return f"Session {str(self.session_id)[:8]} - {self.message_count} messages"
    
    def increment_message_count(self):
        """Increment message count and save"""
        self.message_count += 1
        self.save(update_fields=['message_count', 'updated_at'])
    
    def mark_as_completed(self):
        """Mark conversation as completed"""
        self.status = 'completed'
        self.save(update_fields=['status', 'updated_at'])


class Message(models.Model):
    """
    Individual message in a conversation (user or assistant)
    """
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'AI Assistant'),
        ('system', 'System'),
    ]
    
    # Primary key - UUID
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique message identifier"
    )
    
    # Foreign key to conversation
    session = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        db_column='session_id',
        help_text="Which conversation this message belongs to"
    )
    
    # Message details
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        help_text="Who sent the message"
    )
    
    content = models.TextField(
        help_text="Message text content"
    )
    
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="When the message was sent"
    )
    
    # Metadata (tokens used, latency, tool calls, etc.)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional data (tokens, response time, tool usage)"
    )
    
    class Meta:
        db_table = 'messages'
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['session', 'timestamp']),
            models.Index(fields=['-timestamp']),
            models.Index(fields=['role']),
        ]
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
    
    def __str__(self):
        preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"{self.role}: {preview}"
    
    def save(self, *args, **kwargs):
        """Override save to increment conversation message count"""
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        # Increment conversation message count if this is a new message
        if is_new:
            self.session.increment_message_count()


class Feedback(models.Model):
    """
    User feedback on AI responses (thumbs up/down)
    """
    
    RATING_CHOICES = [
        (1, 'Thumbs Up'),
        (-1, 'Thumbs Down'),
    ]
    
    # Primary key - UUID
    feedback_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique feedback identifier"
    )
    
    # Foreign keys
    session = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        db_column='session_id',
        help_text="Which conversation this feedback is for"
    )
    
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        db_column='message_id',
        null=True,
        blank=True,
        help_text="Specific message being rated (optional)"
    )
    
    # Feedback data
    rating = models.SmallIntegerField(
        choices=RATING_CHOICES,
        help_text="1 = thumbs up, -1 = thumbs down"
    )
    
    comment = models.TextField(
        blank=True,
        null=True,
        help_text="Optional text feedback from user"
    )
    
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="When feedback was submitted"
    )
    
    class Meta:
        db_table = 'feedback'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['session', '-timestamp']),
            models.Index(fields=['rating']),
            models.Index(fields=['-timestamp']),
        ]
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedback'
    
    def __str__(self):
        rating_text = "👍" if self.rating == 1 else "👎"
        return f"{rating_text} on Session {str(self.session.session_id)[:8]}"