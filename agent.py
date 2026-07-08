"""LiveKit Voice Agent for Pickleball Court Bookings with Google Sheets Integration"""

import os
import logging
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
    function_tool,
# Function tools for the agent


@function_tool()
def save_booking_func(customer_name: str, phone_number: str, booking_date: str, 
                                            booking_time: str, number_of_courts: int, location_preference: str, 
                                            special_requests: str = "", price_per_court: float = 800.0) -> str:
                                                    """Save a booking to Google Sheets"""
                                                    try:
                                                                booking_data = {
                                                                                'customer_name': customer_name,
                                                                                'phone_number': phone_number,
                                                                                'booking_date': booking_date,
                                                                                'booking_time': booking_time,
                                                                                'number_of_courts': number_of_courts,
                                                                                'location': location_preference,
                                                                                'preference': location_preference,
                                                                                'special_requests': special_requests,
                                                                                'price_per_court': price_per_court,
                                                                                'total_price': price_per_court * number_of_courts,
                                                                                'booking_status': 'Confirmed'
                                                                }

        if sheets_manager.add_booking(booking_data):
                        return f"Booking saved for {customer_name} on {booking_date} at {booking_time}"
        else:
                        return "Failed to save booking"
except Exception as e:
        logger.error(f"Error saving booking: {str(e)}")
        return f"Error: {str(e)}"


@function_tool()
def check_availability_func(booking_date: str, booking_time: str, location_preference: str) -> str:
        """Check if courts are available"""
        try:
                    is_available = sheets_manager.check_availability(booking_date, booking_time, location_preference)
                    if is_available:
                                    return f"Courts available on {booking_date} at {booking_time}"
                    else:
                                    return f"Courts not available on {booking_date} at {booking_time}"
        except Exception as e:
                    return f"Error: {str(e)}"


@function_tool()
def get_booking_history_func(phone_number: str) -> str:
        """Retrieve customer booking history"""
        try:
                    bookings = sheets_manager.get_bookings(filters={'phone_number': phone_number})
                    if bookings:
                                    booking_list = "\n".join([f"- {b['booking_date']} at {b['booking_time']}: {b['number_of_courts']} courts" for b in bookings])
                                    return f"Previous bookings:\n{booking_list}"
                    else:
                                    return "No previous bookings found"
        except Exception as e:
                    return f"Error: {str(e)}"


async def prewarm
await assistant.start(ctx)from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import silero, openai
from sheets_manager import GoogleSheetsManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", "12QrXIz_mHbkjq-UY_IpUwKh9xY7kaUnUgo9CovQBbx4")
SHEET_NAME = "Sheet1"

# Initialize Google Sheets Manager
sheets_manager = GoogleSheetsManager(SPREADSHEET_ID, SHEET_NAME)

# System prompt for the agent
SYSTEM_PROMPT = """You are a helpful voice assistant for Pickleverse, a pickleball court booking service.
You help customers book pickleball courts. Always collect:
1. Customer name
2. Phone number
3. Booking date
4. Booking time
5. Number of courts needed
6. Location preference
7. Any special requests
Price per court: 800 Rs, Total will be calculated as 800 Rs x number of courts.

After collecting all info, confirm the booking by saying the details back.
When customer confirms, save the booking to the database.
Be friendly and professional."""
Always try to call the save_booking function after confirming all details with the customer. Always present the total price clearly (price per court × number of courts).


async def prewarm(proc: JobContext):
        """Prewarm the agent by loading models"""
        await proc.download_files(
            silero.VAD.model_fqn, openai.STT.model_fqn, openai.LLM.model_fqn
        )


async def entrypoint(ctx: JobContext):
        """Main entry point for the agent"""

    initial_ctx = llm.ChatContext().add(
                role="system",
                text=SYSTEM_PROMPT,
    )

    assistant = VoiceAssistant(
                vad=silero.VAD.create(),
                stt=openai.STT(),
                llm=openai.LLM(),
                tts=openai.TTS(),
                ctx=initial_ctx,
    )

    # Register function tools with the assistant
    assistant.register_function_tool(save_booking_func)
    assistant.register_function_tool(check_availability_func)
    assistant.register_function_tool(get_booking_history_func)

    await assistant.start(ctx)


if __name__ == "__main__":
        WorkerOptions(
                    entrypoint=entrypoint,
                    prewarm_fnc=prewarm,
                    auto_subscribe=AutoSubscribe.AUDIO_ONLY,
        ).run()
