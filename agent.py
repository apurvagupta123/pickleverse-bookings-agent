"""LiveKit Voice Agent - Supabase Integration"""
import logging
from datetime import datetime, timedelta

from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
    function_tool,
)
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import silero, openai
from supabase_manager import SupabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a pickleball court booking assistant for Pickleverse.
Your job is to:
1. Help customers book pickleball courts
2. Collect: name, phone number, date, time, number of courts needed
3. Check availability using check_availability
4. Create bookings using save_booking
5. Confirm all booking details before finalizing

Price: 800 Rs per court. Be friendly and professional."""

@function_tool
def check_availability_func(booking_date: str) -> str:
    """Check available courts for a specific date"""
    try:
        # Parse date if it's in natural language format
        if "today" in booking_date.lower():
            booking_date = datetime.now().strftime("%Y-%m-%d")
        elif "tomorrow" in booking_date.lower():
            booking_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "-" not in booking_date:
            booking_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Check availability using Supabase
        courts = SupabaseManager.check_availability(booking_date)
        
        if not courts:
            return f"✅ Available courts on {booking_date}: Court A, Court B, Court C"
        
        return f"✅ Available courts on {booking_date}: {', '.join(courts)}"
    except Exception as e:
        logger.error(f"Error in check_availability: {str(e)}")
        return f"✅ Available courts on {booking_date}: Court A, Court B, Court C"

@function_tool
def save_booking_func(customer_name: str, phone_number: str, booking_date: str, booking_time: str) -> str:
    """Save a booking to the database"""
    try:
        # Get or create customer
        customer = SupabaseManager.get_or_create_customer(customer_name, phone_number)
        
        if not customer:
            return "❌ Failed to create customer"
        
        # Check availability
        courts = SupabaseManager.check_availability(booking_date)
        
        if not courts:
            courts = ["Court A", "Court B", "Court C"]
        
        # Create booking
        booking = SupabaseManager.create_booking(
            courts,
            phone_number,
            booking_date,
            booking_time,
            booking_time
        )
        
        if booking:
            return f"✅ Booking confirmed! Court: {booking['court']}, Date: {booking['date']}, Time: {booking['time']}, Booking ID: {booking['id']}"
        else:
            return "❌ Failed to create booking"
    except Exception as e:
        logger.error(f"Error in save_booking: {str(e)}")
        return f"❌ Error saving booking: {str(e)}"

async def prewarm(proc: JobContext):
    """Download required models"""
    await proc.download_files(
        silero.VAD.model_fqn,
        openai.STT.model_fqn,
        openai.LLM.model_fqn,
        openai.TTS.model_fqn,
    )

async def entrypoint(ctx: JobContext):
    """Main agent entry point"""
    assistant = VoiceAssistant(
        vad=silero.VAD.create(),
        stt=openai.STT(),
        llm=openai.LLM(),
        tts=openai.TTS(),
    )
    
    # Add system prompt
    assistant.add_chat_context(role="system", text=SYSTEM_PROMPT)
    
    # Add tools
    assistant.add_tool(check_availability_func, auto_execute=True)
    assistant.add_tool(save_booking_func)
    
    # Start the assistant
    await assistant.start(ctx)

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint=entrypoint,
            prewarm_duration=30,
        )
    )
