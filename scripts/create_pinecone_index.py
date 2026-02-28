"""
Create Pinecone Index
Run this script once to set up the Pinecone index for FAQ storage
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

from rag.pinecone_client import PineconeClient


def main():
    print("\n" + "="*60)
    print("🔧 PINECONE INDEX SETUP")
    print("="*60 + "\n")
    
    try:
        # Initialize Pinecone client
        print("Initializing Pinecone client...")
        pc_client = PineconeClient()
        
        # Create index
        print(f"Creating index: {pc_client.index_name}")
        print(f"Environment: {pc_client.environment}")
        print(f"Dimension: 1536 (OpenAI text-embedding-3-small)")
        print(f"Metric: cosine\n")
        
        pc_client.create_index(dimension=1536, metric='cosine')
        
        # Get stats
        print("\nGetting index statistics...")
        stats = pc_client.get_stats()
        
        print("\n" + "="*60)
        print("✅ PINECONE INDEX READY!")
        print("="*60)
        print(f"\nIndex Name: {pc_client.index_name}")
        print(f"Total Vectors: {stats.get('total_vector_count', 0)}")
        print(f"Dimension: {stats.get('dimension', 1536)}")
        print("\nNext step: Run 'python manage.py ingest_faq' to load FAQs")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error creating index: {str(e)}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()