"""
Seed test data for development
Creates sample conversations, messages, and feedback
"""

import os
import sys
import django
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chakancha.settings.development')
django.setup()

from chatbot.models import Conversation, Message, Feedback
from django.utils import timezone
import uuid


def clear_existing_data():
    """Clear all existing test data"""
    print("🗑️  Clearing existing data...")
    Feedback.objects.all().delete()
    Message.objects.all().delete()
    Conversation.objects.all().delete()
    print("✅ Cleared!")


def create_test_conversations():
    """Create sample conversations"""
    print("\n📝 Creating test conversations...")
    
    # Conversation 1: Active - Tea inquiry
    conv1 = Conversation.objects.create(
        language='en',
        status='active',
        user_metadata={
            'browser': 'Chrome 120',
            'location': 'Nairobi, Kenya',
            'device': 'Desktop'
        }
    )
    
    Message.objects.create(
        session=conv1,
        role='user',
        content="Hello! What types of tea do you sell?",
        metadata={'input_length': 37}
    )
    
    Message.objects.create(
        session=conv1,
        role='assistant',
        content="Welcome to Chakancha Global! We specialize in premium Kenyan black tea from the highlands of Nandi County. Our tea is 100% organic, fair trade, and hand-picked for the highest quality.",
        metadata={'response_time_ms': 1234, 'tokens_used': 45}
    )
    
    Message.objects.create(
        session=conv1,
        role='user',
        content="That sounds great! How do I place an order?",
        metadata={'input_length': 46}
    )
    
    Message.objects.create(
        session=conv1,
        role='assistant',
        content="You can place an order through our website or by contacting our sales team. We offer various package sizes from 100g to 1kg. Would you like me to guide you through the ordering process?",
        metadata={'response_time_ms': 1567, 'tokens_used': 52}
    )
    
    # Add positive feedback
    Feedback.objects.create(
        session=conv1,
        rating=1,
        comment="Very helpful information!"
    )
    
    print(f"✅ Created conversation 1: {conv1.session_id}")
    
    # Conversation 2: Completed - DHL tracking
    conv2 = Conversation.objects.create(
        language='en',
        status='completed',
        user_metadata={
            'browser': 'Safari 17',
            'location': 'New York, USA',
            'device': 'iPhone'
        }
    )
    
    Message.objects.create(
        session=conv2,
        role='user',
        content="Can you help me track my order? Tracking number: DHL123456789",
        metadata={'input_length': 67}
    )
    
    Message.objects.create(
        session=conv2,
        role='assistant',
        content="I'll help you track that order. Let me check the status for tracking number DHL123456789... Your package is currently in transit and expected to arrive on March 5th, 2026. It's currently at the sorting facility in Frankfurt.",
        metadata={'response_time_ms': 2345, 'tokens_used': 68, 'tool_used': 'dhl_tracker'}
    )
    
    Message.objects.create(
        session=conv2,
        role='user',
        content="Thank you so much!",
        metadata={'input_length': 18}
    )
    
    Message.objects.create(
        session=conv2,
        role='assistant',
        content="You're welcome! Is there anything else I can help you with today?",
        metadata={'response_time_ms': 892, 'tokens_used': 18}
    )
    
    # Add positive feedback
    Feedback.objects.create(
        session=conv2,
        rating=1
    )
    
    conv2.mark_as_completed()
    print(f"✅ Created conversation 2: {conv2.session_id}")
    
    # Conversation 3: Active - Chakan Tree inquiry
    conv3 = Conversation.objects.create(
        language='en',
        status='active',
        user_metadata={
            'browser': 'Firefox 122',
            'location': 'London, UK',
            'device': 'Desktop'
        }
    )
    
    Message.objects.create(
        session=conv3,
        role='user',
        content="What is the Chakan Tree referral system?",
        metadata={'input_length': 43}
    )
    
    Message.objects.create(
        session=conv3,
        role='assistant',
        content="The Chakan Tree is our referral program! When you refer friends to Chakancha Global, you earn rewards. For every person who makes a purchase using your referral code, you get 10% commission. Plus, your referrals get a 5% discount on their first order!",
        metadata={'response_time_ms': 1678, 'tokens_used': 62}
    )
    
    # Add positive feedback
    Feedback.objects.create(
        session=conv3,
        rating=1
    )
    
    print(f"✅ Created conversation 3: {conv3.session_id}")
    
    # Conversation 4: Active - Negative feedback
    conv4 = Conversation.objects.create(
        language='en',
        status='active',
        user_metadata={
            'browser': 'Edge 120',
            'location': 'Toronto, Canada',
            'device': 'Desktop'
        }
    )
    
    Message.objects.create(
        session=conv4,
        role='user',
        content="Is your tea gluten-free?",
        metadata={'input_length': 25}
    )
    
    Message.objects.create(
        session=conv4,
        role='assistant',
        content="I apologize, but I don't have specific information about gluten content. However, pure tea leaves are naturally gluten-free. I recommend contacting our customer service team for detailed allergen information.",
        metadata={'response_time_ms': 1234, 'tokens_used': 42}
    )
    
    # Add negative feedback
    Feedback.objects.create(
        session=conv4,
        rating=-1,
        comment="Expected more detailed information"
    )
    
    print(f"✅ Created conversation 4: {conv4.session_id}")
    
    # Conversation 5: Short conversation
    conv5 = Conversation.objects.create(
        language='en',
        status='active',
        user_metadata={
            'browser': 'Chrome 120',
            'location': 'Mombasa, Kenya',
            'device': 'Mobile'
        }
    )
    
    Message.objects.create(
        session=conv5,
        role='user',
        content="Hi",
        metadata={'input_length': 2}
    )
    
    Message.objects.create(
        session=conv5,
        role='assistant',
        content="Hello! Welcome to Chakancha Global. I'm your AI tea assistant. How can I help you today?",
        metadata={'response_time_ms': 756, 'tokens_used': 24}
    )
    
    print(f"✅ Created conversation 5: {conv5.session_id}")


def print_summary():
    """Print summary of created data"""
    print("\n" + "="*60)
    print("📊 TEST DATA SUMMARY")
    print("="*60)
    print(f"✅ Total Conversations: {Conversation.objects.count()}")
    print(f"✅ Total Messages: {Message.objects.count()}")
    print(f"✅ Total Feedback: {Feedback.objects.count()}")
    print(f"👍 Positive Feedback: {Feedback.objects.filter(rating=1).count()}")
    print(f"👎 Negative Feedback: {Feedback.objects.filter(rating=-1).count()}")
    print("\n📍 Conversation Details:")
    for conv in Conversation.objects.all().order_by('-created_at'):
        print(f"  - {str(conv.session_id)[:8]}... | {conv.message_count} msgs | {conv.status}")
    print("="*60)


def main():
    """Main execution"""
    print("\n🌱 CHAKANCHA TEST DATA SEEDER")
    print("="*60)
    
    clear_existing_data()
    create_test_conversations()
    print_summary()
    
    print("\n✅ Test data seeding complete!")
    print("🔗 Access Django admin: http://127.0.0.1:8000/admin/")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()