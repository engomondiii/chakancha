"""
Django Management Command: Ingest FAQs into Pinecone
Usage: python manage.py ingest_faq --file path/to/faq.json
"""

from django.core.management.base import BaseCommand, CommandError
from rag.ingest import FAQIngestor
import os


class Command(BaseCommand):
    help = 'Ingest FAQ data into Pinecone vector database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Path to FAQ JSON file',
            default='data/faq/faq_en.json'
        )
        
        parser.add_argument(
            '--namespace',
            type=str,
            help='Pinecone namespace (default: default)',
            default='default'
        )
        
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before ingestion'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        namespace = options['namespace']
        clear_first = options['clear']
        
        # Validate file exists
        if not os.path.exists(file_path):
            raise CommandError(f"File not found: {file_path}")
        
        self.stdout.write(self.style.SUCCESS(f"\n{'='*60}"))
        self.stdout.write(self.style.SUCCESS("🚀 CHAKANCHA FAQ INGESTION"))
        self.stdout.write(self.style.SUCCESS(f"{'='*60}\n"))
        
        self.stdout.write(f"📄 File: {file_path}")
        self.stdout.write(f"📦 Namespace: {namespace}")
        self.stdout.write(f"🗑️  Clear first: {clear_first}\n")
        
        # Initialize ingestor
        self.stdout.write("Initializing FAQ ingestor...")
        ingestor = FAQIngestor()
        
        # Run ingestion
        self.stdout.write("Starting ingestion process...\n")
        result = ingestor.ingest_faqs(
            filepath=file_path,
            namespace=namespace,
            clear_first=clear_first
        )
        
        # Display results
        if result['status'] == 'success':
            self.stdout.write(self.style.SUCCESS(f"\n✅ INGESTION SUCCESSFUL!\n"))
            self.stdout.write(f"📊 FAQs loaded from file: {result['faqs_loaded']}")
            self.stdout.write(f"🔢 Vectors created: {result['vectors_created']}")
            self.stdout.write(f"☁️  Vectors upserted to Pinecone: {result['vectors_upserted']}")
            
            if 'index_stats' in result:
                stats = result['index_stats']
                self.stdout.write(f"\n📈 Index Statistics:")
                self.stdout.write(f"   Total vectors: {stats.get('total_vector_count', 'N/A')}")
                self.stdout.write(f"   Dimension: {stats.get('dimension', 'N/A')}")
            
            self.stdout.write(self.style.SUCCESS(f"\n{'='*60}"))
            self.stdout.write(self.style.SUCCESS("✅ FAQ knowledge base is ready!"))
            self.stdout.write(self.style.SUCCESS(f"{'='*60}\n"))
        else:
            self.stdout.write(self.style.ERROR(f"\n❌ INGESTION FAILED"))
            self.stdout.write(self.style.ERROR(f"Error: {result.get('message', 'Unknown error')}"))