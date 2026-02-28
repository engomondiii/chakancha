"""
URL configuration for chatbot app
Matches frontend api.js endpoints exactly
"""

from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # Main endpoints - match frontend api.js
    path('chat/', views.chat_endpoint, name='chat'),
    path('feedback/', views.feedback_endpoint, name='feedback'),
    path('health/', views.health_check, name='health'),
    
    # Optional: Get conversation history (for debugging)
    path('conversation/<uuid:session_id>/', views.conversation_history, name='conversation_history'),
]