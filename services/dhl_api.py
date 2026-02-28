"""
DHL Tracking API Client
Provides shipment tracking functionality with real API and mock mode
"""

import requests
import logging
from datetime import datetime
from typing import Dict, Optional, List
from django.conf import settings

logger = logging.getLogger('chatbot')


class DHLTrackingClient:
    """
    DHL Shipment Tracking API Client
    Supports both real DHL API and mock mode for testing
    """
    
    # DHL API endpoints
    BASE_URL = "https://api-eu.dhl.com/track/shipments"
    
    def __init__(self):
        """Initialize DHL client with API key from settings"""
        self.api_key = settings.DHL_API_KEY
        self.mock_mode = not bool(self.api_key)  # Use mock if no API key
        
        if self.mock_mode:
            logger.warning("⚠️  DHL API key not set - using MOCK MODE")
        else:
            logger.info("✅ DHL API client initialized with real credentials")
    
    def track_shipment(self, tracking_number: str) -> Dict:
        """
        Track a DHL shipment by tracking number
        
        Args:
            tracking_number (str): DHL tracking number
        
        Returns:
            Dict: Shipment tracking information
        """
        try:
            # Validate tracking number format
            if not self._validate_tracking_number(tracking_number):
                return {
                    'success': False,
                    'error': 'Invalid tracking number format',
                    'tracking_number': tracking_number
                }
            
            # Use mock data if no API key
            if self.mock_mode:
                logger.info(f"Using MOCK data for tracking: {tracking_number}")
                return self._get_mock_tracking_data(tracking_number)
            
            # Make real API call
            logger.info(f"Fetching real DHL data for: {tracking_number}")
            return self._fetch_real_tracking_data(tracking_number)
            
        except Exception as e:
            logger.error(f"Error tracking shipment: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f'Tracking service error: {str(e)}',
                'tracking_number': tracking_number
            }
    
    def _fetch_real_tracking_data(self, tracking_number: str) -> Dict:
        """
        Fetch tracking data from real DHL API
        
        Args:
            tracking_number (str): DHL tracking number
        
        Returns:
            Dict: Parsed tracking information
        """
        try:
            # DHL API request
            headers = {
                'DHL-API-Key': self.api_key,
                'Accept': 'application/json'
            }
            
            params = {
                'trackingNumber': tracking_number
            }
            
            response = requests.get(
                self.BASE_URL,
                headers=headers,
                params=params,
                timeout=10
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Parse DHL API response
            return self._parse_dhl_response(data, tracking_number)
            
        except requests.exceptions.Timeout:
            logger.error(f"DHL API timeout for {tracking_number}")
            return {
                'success': False,
                'error': 'DHL API request timeout',
                'tracking_number': tracking_number
            }
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return {
                    'success': False,
                    'error': 'Tracking number not found',
                    'tracking_number': tracking_number
                }
            else:
                logger.error(f"DHL API HTTP error: {e.response.status_code}")
                return {
                    'success': False,
                    'error': f'DHL API error: {e.response.status_code}',
                    'tracking_number': tracking_number
                }
        
        except Exception as e:
            logger.error(f"Unexpected error with DHL API: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to fetch tracking information',
                'tracking_number': tracking_number
            }
    
    def _parse_dhl_response(self, data: Dict, tracking_number: str) -> Dict:
        """
        Parse DHL API response into standardized format
        
        Args:
            data (Dict): Raw DHL API response
            tracking_number (str): Tracking number
        
        Returns:
            Dict: Standardized tracking information
        """
        try:
            # Extract shipment data
            shipments = data.get('shipments', [])
            
            if not shipments:
                return {
                    'success': False,
                    'error': 'No shipment data found',
                    'tracking_number': tracking_number
                }
            
            shipment = shipments[0]
            
            # Extract status
            status = shipment.get('status', {})
            current_status = status.get('statusCode', 'unknown')
            status_description = status.get('description', 'Status unknown')
            
            # Extract events (tracking history)
            events = shipment.get('events', [])
            latest_event = events[0] if events else {}
            
            # Extract delivery info
            estimated_delivery = shipment.get('estimatedTimeOfDelivery')
            delivery_date = shipment.get('estimatedDeliveryTimeFrame', {}).get('estimatedFrom')
            
            # Extract origin and destination
            origin = shipment.get('origin', {}).get('address', {})
            destination = shipment.get('destination', {}).get('address', {})
            
            return {
                'success': True,
                'tracking_number': tracking_number,
                'status': current_status,
                'status_description': status_description,
                'current_location': latest_event.get('location', {}).get('address', {}).get('addressLocality', 'Unknown'),
                'estimated_delivery': estimated_delivery or delivery_date,
                'origin': {
                    'city': origin.get('addressLocality', ''),
                    'country': origin.get('countryCode', '')
                },
                'destination': {
                    'city': destination.get('addressLocality', ''),
                    'country': destination.get('countryCode', '')
                },
                'events': [
                    {
                        'timestamp': event.get('timestamp'),
                        'description': event.get('description'),
                        'location': event.get('location', {}).get('address', {}).get('addressLocality', '')
                    }
                    for event in events[:5]  # Last 5 events
                ],
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing DHL response: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to parse tracking data',
                'tracking_number': tracking_number
            }
    
    def _get_mock_tracking_data(self, tracking_number: str) -> Dict:
        """
        Generate realistic mock tracking data for testing
        
        Args:
            tracking_number (str): Tracking number
        
        Returns:
            Dict: Mock tracking information
        """
        # Different mock scenarios based on tracking number
        mock_scenarios = {
            'TEST123': {
                'success': True,
                'tracking_number': tracking_number,
                'status': 'transit',
                'status_description': 'Shipment in transit',
                'current_location': 'Nairobi Sorting Facility',
                'estimated_delivery': '2026-03-05',
                'origin': {
                    'city': 'Nandi Hills',
                    'country': 'KE'
                },
                'destination': {
                    'city': 'New York',
                    'country': 'US'
                },
                'events': [
                    {
                        'timestamp': '2026-02-28T14:30:00Z',
                        'description': 'Shipment picked up',
                        'location': 'Nandi Hills'
                    },
                    {
                        'timestamp': '2026-02-28T18:45:00Z',
                        'description': 'Arrived at sorting facility',
                        'location': 'Nairobi'
                    },
                    {
                        'timestamp': '2026-02-28T20:15:00Z',
                        'description': 'Departed sorting facility',
                        'location': 'Nairobi'
                    }
                ],
                'last_updated': datetime.now().isoformat()
            },
            'DELIVERED456': {
                'success': True,
                'tracking_number': tracking_number,
                'status': 'delivered',
                'status_description': 'Shipment delivered',
                'current_location': 'New York, NY',
                'estimated_delivery': '2026-02-25',
                'origin': {
                    'city': 'Nandi Hills',
                    'country': 'KE'
                },
                'destination': {
                    'city': 'New York',
                    'country': 'US'
                },
                'events': [
                    {
                        'timestamp': '2026-02-25T10:30:00Z',
                        'description': 'Delivered',
                        'location': 'New York, NY'
                    },
                    {
                        'timestamp': '2026-02-25T08:15:00Z',
                        'description': 'Out for delivery',
                        'location': 'New York, NY'
                    }
                ],
                'last_updated': datetime.now().isoformat()
            }
        }
        
        # Return specific mock scenario or generic one
        if tracking_number.upper() in mock_scenarios:
            return mock_scenarios[tracking_number.upper()]
        
        # Generic mock response
        return {
            'success': True,
            'tracking_number': tracking_number,
            'status': 'transit',
            'status_description': 'Shipment in transit to destination',
            'current_location': 'Frankfurt Sorting Facility',
            'estimated_delivery': '2026-03-10',
            'origin': {
                'city': 'Nairobi',
                'country': 'KE'
            },
            'destination': {
                'city': 'London',
                'country': 'GB'
            },
            'events': [
                {
                    'timestamp': datetime.now().isoformat(),
                    'description': 'Package in transit',
                    'location': 'Frankfurt'
                }
            ],
            'last_updated': datetime.now().isoformat()
        }
    
    def _validate_tracking_number(self, tracking_number: str) -> bool:
        """
        Validate DHL tracking number format
        
        Args:
            tracking_number (str): Tracking number to validate
        
        Returns:
            bool: True if valid format
        """
        if not tracking_number:
            return False
        
        # Remove whitespace
        tracking_number = tracking_number.strip()
        
        # DHL tracking numbers are typically:
        # - 10 digits
        # - Start with specific prefixes
        # - May contain letters and numbers
        
        # Basic validation: between 8 and 39 characters
        if len(tracking_number) < 8 or len(tracking_number) > 39:
            return False
        
        return True
    
    def format_tracking_response(self, tracking_data: Dict) -> str:
        """
        Format tracking data into human-readable text
        
        Args:
            tracking_data (Dict): Tracking information
        
        Returns:
            str: Formatted tracking message
        """
        if not tracking_data.get('success'):
            error = tracking_data.get('error', 'Unknown error')
            return f"❌ Tracking Error: {error}"
        
        tracking_number = tracking_data['tracking_number']
        status = tracking_data['status_description']
        location = tracking_data['current_location']
        estimated_delivery = tracking_data.get('estimated_delivery', 'Not available')
        
        # Format message
        message = f"📦 **Tracking Number:** {tracking_number}\n\n"
        message += f"**Status:** {status}\n"
        message += f"**Current Location:** {location}\n"
        message += f"**Estimated Delivery:** {estimated_delivery}\n"
        
        # Add origin and destination
        origin = tracking_data.get('origin', {})
        destination = tracking_data.get('destination', {})
        
        if origin.get('city'):
            message += f"\n**From:** {origin['city']}, {origin.get('country', '')}"
        
        if destination.get('city'):
            message += f"\n**To:** {destination['city']}, {destination.get('country', '')}"
        
        # Add latest events
        events = tracking_data.get('events', [])
        if events:
            message += "\n\n**Recent Activity:**\n"
            for event in events[:3]:  # Show last 3 events
                timestamp = event.get('timestamp', '')
                description = event.get('description', '')
                event_location = event.get('location', '')
                
                # Format timestamp
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_time = dt.strftime('%b %d, %I:%M %p')
                except:
                    formatted_time = timestamp
                
                message += f"• {formatted_time} - {description}"
                if event_location:
                    message += f" ({event_location})"
                message += "\n"
        
        return message