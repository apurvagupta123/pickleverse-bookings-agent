"""LiveKit Voice Agent for Pickleball Court Bookings with Google Sheets Integration"""

import os
import logging
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.voice_assistant import VoiceAssistant
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

After collecting all info, confirm the booking by saying the details back.
When customer confirms, save the booking to the database.
Be friendly and professional."""


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

    await assistant.start(ctx)


if __name__ == "__main__":
        WorkerOptions(
                    entrypoint=entrypoint,
                    prewarm_fnc=prewarm,
                    auto_subscribe=AutoSubscribe.AUDIO_ONLY,
        ).run()
