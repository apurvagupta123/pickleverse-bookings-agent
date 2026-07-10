"""Supabase Database Manager for Court Bookings"""
from supabase import create_client
import logging

logger = logging.getLogger(__name__)

# Initialize Supabase connection
SUPABASE_URL = "https://djtachdauckqkjhoogqv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRqdGFjaGRhdWNrcWtqaG9vZ3F2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM2OTY4MDEsImV4cCI6MjA5OTI3MjgwMX0.PhyCHrB4thHdvFGj4fuFme9mjonx2ELYvdcuAqhkEjE"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class SupabaseManager:
    """Manages all Supabase database operations"""
    
    @staticmethod
    def check_availability(booking_date: str) -> list:
        """Check which courts are available on a specific date"""
        try:
            response = supabase.table("bookings").select("*").eq(
                "booking_date", booking_date
            ).execute()
            
            # Get booked courts
            booked_courts = set([b['court_name'] for b in response.data])
            
            # All available courts
            all_courts = ["Court A", "Court B", "Court C"]
            available = [c for c in all_courts if c not in booked_courts]
            
            logger.info(f"Available courts on {booking_date}: {available}")
            return available
        except Exception as e:
            logger.error(f"Error checking availability: {str(e)}")
            return []
    
    @staticmethod
    def get_or_create_customer(name: str, phone: str) -> dict:
        """Get customer info or save new customer"""
        try:
            # Check if customer exists
            response = supabase.table("call_data").select("*").eq(
                "customer_phone", phone
            ).execute()
            
            if response.data:
                logger.info(f"Customer found: {name} ({phone})")
                return {"id": phone, "name": name, "phone": phone}
            
            # Create new customer record
            supabase.table("call_data").insert({
                "customer_phone": phone,
                "customer_name": name,
                "call_notes": f"New customer registered"
            }).execute()
            
            logger.info(f"New customer created: {name} ({phone})")
            return {"id": phone, "name": name, "phone": phone}
        except Exception as e:
            logger.error(f"Error with customer: {str(e)}")
            return None
    
    @staticmethod
    def create_booking(courts: list, phone: str, booking_date: str, start_time: str, end_time: str) -> dict:
        """Create a booking in the database"""
        try:
            court_name = courts[0] if courts else "Court A"
            
            response = supabase.table("bookings").insert({
                "court_name": court_name,
                "booking_date": booking_date,
                "start_time": start_time,
                "end_time": end_time,
                "customer_phone": phone,
                "customer_name": "Customer",
                "status": "confirmed"
            }).execute()
            
            booking_id = response.data[0].get("id") if response.data else "12345"
            logger.info(f"Booking created: ID {booking_id}")
            
            return {
                "id": booking_id,
                "court": court_name,
                "date": booking_date,
                "time": f"{start_time}-{end_time}"
            }
        except Exception as e:
            logger.error(f"Error creating booking: {str(e)}")
            return None
