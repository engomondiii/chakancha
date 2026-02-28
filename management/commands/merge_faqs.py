"""
Django Management Command: Merge FAQ Files and Auto-Ingest
Usage: python manage.py merge_faqs [--new-file path] [--auto-ingest]
"""

from django.core.management.base import BaseCommand, CommandError
from utils.faq_merger import FAQMerger
from utils.faq_validator import FAQValidator
from rag.ingest import FAQIngestor
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Merge new FAQ file with existing FAQs and optionally ingest to Pinecone'

    def add_arguments(self, parser):
        parser.add_argument(
            '--new-file',
            type=str,
            help='Path to new FAQ file to merge (default: data/faq/faq_new.json)',
            default='data/faq/faq_new.json'
        )
        
        parser.add_argument(
            '--base-file',
            type=str,
            help='Path to base FAQ file (default: data/faq/faq_en.json)',
            default='data/faq/faq_en.json'
        )
        
        parser.add_argument(
            '--output-file',
            type=str,
            help='Path to save merged file (default: overwrites base file)',
            default=None
        )
        
        parser.add_argument(
            '--no-backup',
            action='store_true',
            help='Do not create backup of base file'
        )
        
        parser.add_argument(
            '--auto-ingest',
            action='store_true',
            help='Automatically ingest merged FAQs to Pinecone'
        )
        
        parser.add_argument(
            '--validate-only',
            action='store_true',
            help='Only validate files without merging'
        )

    def handle(self, *args, **options):
        new_file = options['new_file']
        base_file = options['base_file']
        output_file = options['output_file'] or base_file
        create_backup = not options['no_backup']
        auto_ingest = options['auto_ingest']
        validate_only = options['validate_only']
        
        self.stdout.write(self.style.SUCCESS(f"\n{'='*70}"))
        self.stdout.write(self.style.SUCCESS("🔀 CHAKANCHA FAQ MERGER"))
        self.stdout.write(self.style.SUCCESS(f"{'='*70}\n"))
        
        # Validate files exist
        if not os.path.exists(base_file):
            raise CommandError(f"Base file not found: {base_file}")
        
        if not os.path.exists(new_file):
            raise CommandError(f"New file not found: {new_file}")
        
        # Initialize tools
        validator = FAQValidator()
        merger = FAQMerger()
        
        # Step 1: Validate files
        self.stdout.write("📋 Step 1: Validating FAQ files...\n")
        
        self.stdout.write(f"Validating base file: {base_file}")
        base_valid, base_errors, base_warnings = validator.validate_file(base_file)
        
        if base_valid:
            base_count = validator.get_faq_count(base_file)
            self.stdout.write(self.style.SUCCESS(f"✅ Base file valid ({base_count} FAQs)"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ Base file invalid"))
            for error in base_errors:
                self.stdout.write(self.style.ERROR(f"   • {error}"))
            return
        
        if base_warnings:
            for warning in base_warnings:
                self.stdout.write(self.style.WARNING(f"   ⚠️  {warning}"))
        
        self.stdout.write(f"\nValidating new file: {new_file}")
        new_valid, new_errors, new_warnings = validator.validate_file(new_file)
        
        if new_valid:
            new_count = validator.get_faq_count(new_file)
            self.stdout.write(self.style.SUCCESS(f"✅ New file valid ({new_count} FAQs)"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ New file invalid"))
            for error in new_errors:
                self.stdout.write(self.style.ERROR(f"   • {error}"))
            return
        
        if new_warnings:
            for warning in new_warnings:
                self.stdout.write(self.style.WARNING(f"   ⚠️  {warning}"))
        
        # If validate-only mode, stop here
        if validate_only:
            self.stdout.write(self.style.SUCCESS(f"\n✅ Validation complete!"))
            return
        
        # Step 2: Merge files
        self.stdout.write(f"\n📋 Step 2: Merging FAQ files...\n")
        self.stdout.write(f"Base file: {base_file} ({base_count} FAQs)")
        self.stdout.write(f"New file: {new_file} ({new_count} FAQs)")
        self.stdout.write(f"Output: {output_file}")
        self.stdout.write(f"Backup: {'Yes' if create_backup else 'No'}\n")
        
        result = merger.merge_files(
            base_file=base_file,
            new_file=new_file,
            output_file=output_file,
            create_backup=create_backup,
            auto_resolve=True
        )
        
        if not result['success']:
            self.stdout.write(self.style.ERROR(f"\n❌ Merge failed: {result.get('error')}"))
            return
        
        # Display merge statistics
        self.stdout.write(self.style.SUCCESS(f"\n✅ MERGE SUCCESSFUL!\n"))
        self.stdout.write(f"📊 Merge Statistics:")
        self.stdout.write(f"   Base FAQs: {result['base_faqs']}")
        self.stdout.write(f"   New FAQs: {result['new_faqs']}")
        self.stdout.write(f"   ➕ Added: {result['added']}")
        self.stdout.write(f"   🔄 Updated: {result['updated']}")
        self.stdout.write(f"   ⏭️  Duplicates skipped: {result['duplicates_skipped']}")
        self.stdout.write(self.style.SUCCESS(f"   📝 Total FAQs: {result['total_faqs']}"))
        
        # Step 3: Validate merged result
        self.stdout.write(f"\n📋 Step 3: Validating merged file...\n")
        
        if merger.validate_merge_result(output_file):
            self.stdout.write(self.style.SUCCESS(f"✅ Merged file is valid"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ Merged file has errors"))
            return
        
        # Step 4: Auto-ingest if requested
        if auto_ingest:
            self.stdout.write(f"\n📋 Step 4: Ingesting to Pinecone...\n")
            
            try:
                ingestor = FAQIngestor()
                ingest_result = ingestor.ingest_faqs(
                    filepath=output_file,
                    namespace='default',
                    clear_first=True
                )
                
                if ingest_result['status'] == 'success':
                    self.stdout.write(self.style.SUCCESS(f"✅ Ingestion successful!"))
                    self.stdout.write(f"   Vectors upserted: {ingest_result['vectors_upserted']}")
                else:
                    self.stdout.write(self.style.ERROR(f"❌ Ingestion failed: {ingest_result.get('message')}"))
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Ingestion error: {str(e)}"))
        else:
            self.stdout.write(f"\n💡 To ingest merged FAQs to Pinecone, run:")
            self.stdout.write(f"   python manage.py ingest_faq --file {output_file} --clear")
        
        # Final summary
        self.stdout.write(self.style.SUCCESS(f"\n{'='*70}"))
        self.stdout.write(self.style.SUCCESS("✅ FAQ MERGE COMPLETE!"))
        self.stdout.write(self.style.SUCCESS(f"{'='*70}"))
        self.stdout.write(f"\n📂 Merged file: {output_file}")
        self.stdout.write(f"📊 Total FAQs: {result['total_faqs']}")
        
        if create_backup:
            self.stdout.write(f"💾 Backup created: Look for *_backup_* files in data/faq/")
        
        self.stdout.write(self.style.SUCCESS(f"\n{'='*70}\n"))