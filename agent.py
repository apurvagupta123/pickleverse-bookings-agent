"""LiveKit Voice Agent for Pickleball Court Bookings with Google Sheets Integration"""

import os
import sys
import logging
from typing import Optional
from dotenv import load_dotenv
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

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", "12QrXIz_mHbkjq-UY_IpUwKh9xY7kaUnUgo9CovQBbx4")
SHEET_NAME = "Sheet1"

# Initialize Google Sheets Manager
sheets_manager = GoogleSheetsManager(SPREADSHEET_ID, SHEET_NAME)


# Define system prompt for the agent
SYSTEM_PROMPT = """You are a helpful voice assistant for Pickleverse, a pickleball court booking service.
Your role is to help customers book pickleball courts in their preferred location.

When helping customers book courts:
1. Ask for their name and phone number
2. Ask for their preferred date and time
3. Ask how many courts they need
4. Ask for their preferred location
5. Ask if they have any special requests
6. Confirm the booking details before submitting

Key information:
- Price per court: 800 Rs
- Available locations: Multiple venues (ask customer for their preferred location)
- Booking confirmation will be sent via SMS

Once you have all the information, confirm the booking and let them know it will be confirmed shortly.

Always be friendly, professional, and helpful. If you encounter any issues, politely let them know and offer to help in another way."""


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

    # Set up conversation callbacks for Google Sheets integration
    async def on_message_received(message: llm.ChatMessage):
              """Process incoming messages"""
              if message.role == "user":
                            logger.info(f"User message: {message.content}")

          async def on_message_sent(message: llm.ChatMessage):
                    """Process outgoing messages"""
                    if message.role == "assistant":
                                  logger.info(f"Assistant response: {message.content}")

                assistant.on_message_received(on_message_received)
    assistant.on_message_sent(on_message_sent)

    await assistant.start(ctx)


if __name__ == "__main__":
      WorkerOptions(
                entrypoint=entrypoint,
                prewarm_fnc=prewarm,
                auto_subscribe=AutoSubscribe.AUDIO_ONLY,
      ).run()
