"""LiveKit Voice Agent"""
import logging
from datetime import datetime, timedelta

from livekit.agents import (
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents import VoiceAssistant
from livekit.plugins import silero, openai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a pickleball court booking assistant for Pickleverse.
Help customers book courts. Price: 800 Rs per court.
Always confirm: name, phone, date, time before booking."""

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
    
    # Start the assistant WITHOUT tools
    await assistant.start(ctx)

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint=entrypoint,
            prewarm_duration=30,
        )
    )
