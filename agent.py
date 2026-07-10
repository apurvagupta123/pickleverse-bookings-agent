"""LiveKit Voice Agent - Pickleball Court Booking"""
import logging
from livekit import agents
from livekit.agents import llm
from livekit.plugins import openai, silero

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = "You are a friendly pickleball court booking assistant. Help customers book courts."

async def prewarm(proc: agents.JobContext):
    """Download required models"""
    await proc.download_files(
        silero.VAD.model_fqn,
        openai.STT.model_fqn,
        openai.LLM.model_fqn,
        openai.TTS.model_fqn,
    )

async def entrypoint(ctx: agents.JobContext):
    """Main agent entry point"""
    initial_ctx = llm.ChatContext().add(
        role="system",
        text=SYSTEM_PROMPT,
    )
    
    await ctx.agentic(
        model="gpt-4o",
        chat_ctx=initial_ctx,
        tts=openai.TTS(),
        stt=openai.STT(),
        vad=silero.VAD.create(),
    ).start()

if __name__ == "__main__":
    agents.run_app(prewarm=prewarm, entrypoint=entrypoint)
