"""
Django admin configuration for chatbot models
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Conversation, Message, Feedback


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """
    Admin interface for Conversations
    """
    list_display = [
        'session_id_short',
        'message_count',
        'language',
        'status',
        'created_at_formatted',
        'updated_at_formatted',
    ]
    
    list_filter = [
        'status',
        'language',
        'created_at',
        'updated_at',
    ]
    
    search_fields = [
        'session_id',
    ]
    
    readonly_fields = [
        'session_id',
        'created_at',
        'updated_at',
        'message_count',
        'formatted_metadata',
    ]
    
    fieldsets = (
        ('Session Info', {
            'fields': ('session_id', 'status', 'language')
        }),
        ('Statistics', {
            'fields': ('message_count', 'created_at', 'updated_at')
        }),
        ('Metadata', {
            'fields': ('formatted_metadata',),
            'classes': ('collapse',),
        }),
    )
    
    def session_id_short(self, obj):
        """Display first 8 characters of UUID"""
        return str(obj.session_id)[:8]
    session_id_short.short_description = 'Session ID'
    
    def created_at_formatted(self, obj):
        """Format created timestamp"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
    created_at_formatted.short_description = 'Created'
    created_at_formatted.admin_order_field = 'created_at'
    
    def updated_at_formatted(self, obj):
        """Format updated timestamp"""
        return obj.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    updated_at_formatted.short_description = 'Last Updated'
    updated_at_formatted.admin_order_field = 'updated_at'
    
    def formatted_metadata(self, obj):
        """Display metadata as formatted JSON"""
        import json
        return format_html(
            '<pre>{}</pre>',
            json.dumps(obj.user_metadata, indent=2)
        )
    formatted_metadata.short_description = 'User Metadata'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Admin interface for Messages
    """
    list_display = [
        'message_id_short',
        'session_id_short',
        'role_badge',
        'content_preview',
        'timestamp_formatted',
    ]
    
    list_filter = [
        'role',
        'timestamp',
    ]
    
    search_fields = [
        'message_id',
        'session__session_id',
        'content',
    ]
    
    readonly_fields = [
        'message_id',
        'session',
        'timestamp',
        'formatted_metadata',
    ]
    
    fieldsets = (
        ('Message Info', {
            'fields': ('message_id', 'session', 'role', 'timestamp')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Metadata', {
            'fields': ('formatted_metadata',),
            'classes': ('collapse',),
        }),
    )
    
    def message_id_short(self, obj):
        """Display first 8 characters of UUID"""
        return str(obj.message_id)[:8]
    message_id_short.short_description = 'Message ID'
    
    def session_id_short(self, obj):
        """Display first 8 characters of session UUID"""
        return str(obj.session.session_id)[:8]
    session_id_short.short_description = 'Session'
    
    def role_badge(self, obj):
        """Display role with color coding"""
        colors = {
            'user': '#2196F3',      # Blue
            'assistant': '#4CAF50',  # Green
            'system': '#FF9800',     # Orange
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.role, '#666'),
            obj.role.upper()
        )
    role_badge.short_description = 'Role'
    
    def content_preview(self, obj):
        """Display first 100 characters of content"""
        preview = obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
        return preview
    content_preview.short_description = 'Content'
    
    def timestamp_formatted(self, obj):
        """Format timestamp"""
        return obj.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    timestamp_formatted.short_description = 'Timestamp'
    timestamp_formatted.admin_order_field = 'timestamp'
    
    def formatted_metadata(self, obj):
        """Display metadata as formatted JSON"""
        import json
        return format_html(
            '<pre>{}</pre>',
            json.dumps(obj.metadata, indent=2)
        )
    formatted_metadata.short_description = 'Metadata'


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """
    Admin interface for Feedback
    """
    list_display = [
        'feedback_id_short',
        'session_id_short',
        'rating_badge',
        'comment_preview',
        'timestamp_formatted',
    ]
    
    list_filter = [
        'rating',
        'timestamp',
    ]
    
    search_fields = [
        'feedback_id',
        'session__session_id',
        'comment',
    ]
    
    readonly_fields = [
        'feedback_id',
        'session',
        'message',
        'timestamp',
    ]
    
    fieldsets = (
        ('Feedback Info', {
            'fields': ('feedback_id', 'session', 'message', 'rating', 'timestamp')
        }),
        ('Comment', {
            'fields': ('comment',)
        }),
    )
    
    def feedback_id_short(self, obj):
        """Display first 8 characters of UUID"""
        return str(obj.feedback_id)[:8]
    feedback_id_short.short_description = 'Feedback ID'
    
    def session_id_short(self, obj):
        """Display first 8 characters of session UUID"""
        return str(obj.session.session_id)[:8]
    session_id_short.short_description = 'Session'
    
    def rating_badge(self, obj):
        """Display rating with emoji"""
        if obj.rating == 1:
            return format_html(
                '<span style="background-color: #4CAF50; color: white; padding: 3px 10px; border-radius: 3px;">👍 Positive</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #F44336; color: white; padding: 3px 10px; border-radius: 3px;">👎 Negative</span>'
            )
    rating_badge.short_description = 'Rating'
    
    def comment_preview(self, obj):
        """Display first 80 characters of comment"""
        if obj.comment:
            preview = obj.comment[:80] + '...' if len(obj.comment) > 80 else obj.comment
            return preview
        return '(no comment)'
    comment_preview.short_description = 'Comment'
    
    def timestamp_formatted(self, obj):
        """Format timestamp"""
        return obj.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    timestamp_formatted.short_description = 'Timestamp'
    timestamp_formatted.admin_order_field = 'timestamp'


# Customize admin site header and title
admin.site.site_header = "Chakancha AI Chatbot Admin"
admin.site.site_title = "Chakancha Admin"
admin.site.index_title = "Chatbot Management"