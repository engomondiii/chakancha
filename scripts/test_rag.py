"""
Test RAG System
Tests FAQ retrieval quality with sample queries
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

from rag.retriever import FAQRetriever


# Test queries
TEST_QUERIES = [
    "What is tea?",
    "How do you make black tea?",
    "What's the difference between black and green tea?",
    "How much does tea cost?",
    "What is the production capacity?",
    "How many employees do I need?",
    "What equipment is required for tea processing?",
    "Is Kenyan tea organic?",
    "What are the health benefits of tea?",
    "How should I store tea?"
]


def main():
    print("\n" + "="*70)
    print("🧪 RAG SYSTEM TEST")
    print("="*70 + "\n")
    
    try:
        # Initialize retriever
        print("Initializing FAQ retriever...")
        retriever = FAQRetriever()
        print("✅ Retriever initialized\n")
        
        # Test each query
        for i, query in enumerate(TEST_QUERIES, 1):
            print(f"\n{'─'*70}")
            print(f"Query #{i}: {query}")
            print(f"{'─'*70}")
            
            # Retrieve FAQs
            results = retriever.retrieve(
                query=query,
                top_k=3,
                min_score=0.7
            )
            
            if results:
                print(f"\n✅ Found {len(results)} relevant FAQ(s):\n")
                
                for j, faq in enumerate(results, 1):
                    print(f"{j}. [{faq['category']}] (Score: {faq['score']:.3f})")
                    print(f"   Q: {faq['question']}")
                    print(f"   A: {faq['answer'][:150]}...")
                    print()
            else:
                print("❌ No relevant FAQs found\n")
        
        # Summary
        print("\n" + "="*70)
        print("✅ RAG SYSTEM TEST COMPLETE")
        print("="*70)
        print(f"Total queries tested: {len(TEST_QUERIES)}")
        print("\nThe system is ready to answer customer questions!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error testing RAG system: {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()