"""Lovable API Manager for LiveKit Pickleball Booking Agent"""

import os
import requests
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class LovableManager:
    """Manages all interactions with Lovable API for pickleball court bookings"""

    def __init__(self):
        """Initialize Lovable API manager with credentials from environment"""
        self.api_key = os.getenv("LOVABLE_API_KEY")
        self.base_url = os.getenv("LOVABLE_API_BASE_URL", "https://courtb.lovable.app")
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }

        if not self.api_key:
            raise ValueError("LOVABLE_API_KEY environment variable not set")
        if not self.base_url:
            raise ValueError("LOVABLE_API_BASE_URL environment variable not set")

    def get_or_create_customer(self, name: str, phone: str, email: str = "") -> Dict:
        """Get existing customer by phone or create new customer if not found"""
        try:
            customer = self.get_customer_by_phone(phone)
            if customer:
                logger.info(f"Found existing customer: {customer['id']}")
                return customer
            else:
                logger.info(f"Creating new customer: {name}")
                return self.create_customer(name, phone, email)
        except Exception as e:
            logger.error(f"Error getting or creating customer: {str(e)}")
            return None

    def create_customer(self, name: str, phone: str, email: str = "") -> Dict:
        """Create a new customer in Lovable"""
        try:
            url = f"{self.base_url}/api/public/customers"
            payload = {"name": name, "phone": phone}
            if email:
                payload["email"] = email

            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            customer_data = response.json()
            logger.info(f"Customer created successfully: {customer_data}")
            return customer_data.get("customer")
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            return None

    def get_customer_by_phone(self, phone: str) -> Optional[Dict]:
        """Get customer by phone number"""
        try:
            url = f"{self.base_url}/api/public/customers"
            params = {"phone": phone}
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 404:
                logger.info(f"Customer not found for phone: {phone}")
                return None
            
            response.raise_for_status()
            customer_data = response.json()
            logger.info(f"Customer found: {customer_data}")
            return customer_data.get("customer")
        except Exception as e:
            logger.error(f"Error getting customer by phone: {str(e)}")
            return None

    def check_availability(self, booking_date: str) -> List[Dict]:
        """Check availability for all courts on a given date"""
        try:
            url = f"{self.base_url}/api/public/availability"
            params = {"date": booking_date}
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            availability_data = response.json()
            logger.info(f"Availability check for {booking_date}: {availability_data}")
            return availability_data.get("courts", [])
        except Exception as e:
            logger.error(f"Error checking availability: {str(e)}")
            return []

    def create_booking(self, court_id: str, customer_phone: str, booking_date: str, 
                      start_time: str, end_time: str, customer_id: str = None) -> Dict:
        """Create a new booking"""
        try:
            url = f"{self.base_url}/api/public/bookings"
            payload = {
                "court_id": court_id,
                "date": booking_date,
                "start_time": start_time,
                "end_time": end_time
            }
            
            if customer_id:
                payload["customer_id"] = customer_id
            else:
                payload["customer_phone"] = customer_phone

            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code == 409:
                logger.warning(f"Slot already booked for {booking_date} {start_time}-{end_time}")
                return None
            
            response.raise_for_status()
            booking_data = response.json()
            logger.info(f"Booking created successfully: {booking_data}")
            return booking_data.get("booking")
        except Exception as e:
            logger.error(f"Error creating booking: {str(e)}")
            return None

    def get_bookings_for_customer(self, phone_number: str) -> List[Dict]:
        """Get all bookings for a customer by phone"""
        try:
            customer = self.get_customer_by_phone(phone_number)
            if not customer:
                logger.info(f"No customer found for phone: {phone_number}")
                return []
            return []
        except Exception as e:
            logger.error(f"Error getting bookings for customer: {str(e)}")
            return []

    def validate_time_slot(self, courts: List[Dict], start_time: str, end_time: str) -> bool:
        """Validate if a time slot is available on any court"""
        try:
            for court in courts:
                available_slots = court.get("available_slots", [])
                for slot in available_slots:
                    if slot["start"] == start_time and slot["end"] == end_time:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error validating time slot: {str(e)}")
            return False
