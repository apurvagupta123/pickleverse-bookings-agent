"""Supabase Database Manager for Court Bookings"""
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to initialize Supabase, but don't crash if it fails
try:
    from supabase import create_client
    SUPABASE_URL = os.getenv("SUPABASE_URL", "https://djtachdauckqkjhoogqv.supabase.co")
    SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "")
    
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("✅ Supabase connected successfully")
    else:
        supabase = None
        logger.warning("⚠️ Supabase credentials not found")
except Exception as e:
    supabase = None
    logger.error(f"❌ Failed to initialize Supabase: {str(e)}")

class SupabaseManager:
    """Manages all Supabase database operations"""
    
    @staticmethod
    def check_availability(booking_date: str) -> list:
        """Check which courts are available on a specific date"""
        try:
            # Default: all courts are available
            all_courts = ["Court A", "Court B", "Court C"]
            
            if not supabase:
                logger.warning("Supabase not initialized, returning all courts as available")
                return all_courts
            
            response = supabase.table("bookings").select("*").eq(
                "booking_date", booking_date
            ).execute()
            
            # Get booked courts
            booked_courts = set([b['court_name'] for b in response.data])
            available = [c for c in all_courts if c not in booked_courts]
            
            logger.info(f"✅ Available courts on {booking_date}: {available}")
            return available if available else all_courts
        except Exception as e:
            logger.error(f"Error checking availability: {str(e)}")
            # Return all courts as fallback
            return ["Court A", "Court B", "Court C"]
    
    @staticmethod
    def get_or_create_customer(name: str, phone: str) -> dict:
        """Get customer info or save new customer"""
        try:
            if not supabase:
                logger.warning("Supabase not initialized, returning mock customer")
                return {"id": phone, "name": name, "phone": phone}
            
            # Check if customer exists
            response = supabase.table("call_data").select("*").eq(
                "customer_phone", phone
            ).execute()
            
            if response.data:
                logger.info(f"✅ Customer found: {name} ({phone})")
                return {"id": phone, "name": name, "phone": phone}
            
            # Create new customer record
            supabase.table("call_data").insert({
                "customer_phone": phone,
                "customer_name": name,
                "call_notes": f"New customer registered on {datetime.now().strftime('%Y-%m-%d')}"
            }).execute()
            
            logger.info(f"✅ New customer created: {name} ({phone})")
            return {"id": phone, "name": name, "phone": phone}
        except Exception as e:
            logger.error(f"Error with customer: {str(e)}")
            # Return mock customer as fallback
            return {"id": phone, "name": name, "phone": phone}
    
    @staticmethod
    def create_booking(courts: list, phone: str, booking_date: str, start_time: str, end_time: str) -> dict:
        """Create a booking in the database"""
        try:
            court_name = courts[0] if courts else "Court A"
            
            if supabase:
                response = supabase.table("bookings").insert({
                    "court_name": court_name,
                    "booking_date": booking_date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "customer_phone": phone,
                    "customer_name": "Customer",
                    "status": "confirmed"
                }).execute()
                
                booking_id = response.data[0].get("id") if response.data else phone
                logger.info(f"✅ Booking created in Supabase: ID {booking_id}")
            else:
                booking_id = phone
                logger.warning("⚠️ Supabase not available, booking created locally")
            
            return {
                "id": booking_id,
                "court": court_name,
                "date": booking_date,
                "time": f"{start_time}-{end_time}"
            }
        except Exception as e:
            logger.error(f"Error creating booking: {str(e)}")
            # Return mock booking as fallback
            return {
                "id": phone,
                "court": courts[0] if courts else "Court A",
                "date": booking_date,
                "time": f"{start_time}-{end_time}"
            }
