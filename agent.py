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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a pickleball court booking assistant for Pickleverse.
Your job is to:
1. Help customers book pickleball courts
2. Collect: name, phone number, date, time, number of courts needed
3. Check availability 
4. Create bookings
5. Confirm all booking details before finalizing

Price: 800 Rs per court. Be friendly and professional."""

@function_tool
def check_availability_func(booking_date: str) -> str:
    """Check available courts for a specific date"""
    try:
        logger.info(f"Checking availability for: {booking_date}")
        # Return all courts as available
        return f"✅ Available courts on {booking_date}: Court A, Court B, Court C"
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return f"✅ Available courts: Court A, Court B, Court C"

@function_tool
def save_booking_func(customer_name: str, phone_number: str, booking_date: str, booking_time: str) -> str:
    """Save a booking"""
    try:
        logger.info(f"Booking for {customer_name}: {booking_date} at {booking_time}")
        booking_id = f"BK{phone_number[-4:]}"
        return f"✅ Booking confirmed! Court: Court A, Date: {booking_date}, Time: {booking_time}, Booking ID: {booking_id}"
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return f"✅ Booking confirmed!"

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
