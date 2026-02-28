"""
Django Management Command: Test DHL Tracking
Usage: python manage.py test_dhl [--tracking-number NUMBER]
"""

from django.core.management.base import BaseCommand
from services.dhl_api import DHLTrackingClient


class Command(BaseCommand):
    help = 'Test DHL tracking API with sample tracking numbers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tracking-number',
            type=str,
            help='Specific tracking number to test',
            default=None
        )

    def handle(self, *args, **options):
        tracking_number = options['tracking_number']
        
        self.stdout.write(self.style.SUCCESS(f"\n{'='*70}"))
        self.stdout.write(self.style.SUCCESS("📦 DHL TRACKING TEST"))
        self.stdout.write(self.style.SUCCESS(f"{'='*70}\n"))
        
        # Initialize DHL client
        dhl_client = DHLTrackingClient()
        
        if dhl_client.mock_mode:
            self.stdout.write(self.style.WARNING("⚠️  Running in MOCK MODE (no API key set)"))
            self.stdout.write("💡 Set DHL_API_KEY in .env to use real API\n")
        else:
            self.stdout.write(self.style.SUCCESS("✅ Using REAL DHL API\n"))
        
        # Test tracking numbers
        test_numbers = [tracking_number] if tracking_number else [
            'TEST123',
            'DELIVERED456',
            'GENERIC789'
        ]
        
        for i, number in enumerate(test_numbers, 1):
            self.stdout.write(f"\n{'-'*70}")
            self.stdout.write(f"Test #{i}: Tracking {number}")
            self.stdout.write(f"{'-'*70}\n")
            
            # Track shipment
            result = dhl_client.track_shipment(number)
            
            # Format and display result
            formatted_message = dhl_client.format_tracking_response(result)
            self.stdout.write(formatted_message)
            
            # Show raw data
            if result.get('success'):
                self.stdout.write(f"\n✅ Tracking successful")
                self.stdout.write(f"Status: {result['status']}")
                self.stdout.write(f"Location: {result['current_location']}")
            else:
                self.stdout.write(self.style.ERROR(f"\n❌ Tracking failed: {result.get('error')}"))
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f"\n{'='*70}"))
        self.stdout.write(self.style.SUCCESS("✅ DHL TRACKING TEST COMPLETE"))
        self.stdout.write(self.style.SUCCESS(f"{'='*70}"))
        
        if dhl_client.mock_mode:
            self.stdout.write(self.style.WARNING("\n💡 TIP: Get your DHL API key from:"))
            self.stdout.write("   https://developer.dhl.com/api-reference/shipment-tracking")
            self.stdout.write("   Then add it to your .env file as DHL_API_KEY\n")