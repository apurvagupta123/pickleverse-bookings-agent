"""LiveKit Voice Agent - Lovable Integration"""
import os, logging
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm, function_tool
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import silero, openai
from lovable_manager import LovableManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
lovable_manager = LovableManager()

SYSTEM_PROMPT = """You are a pickleball court booking assistant for Pickleverse.
Collect: name, phone, date (YYYY-MM-DD), time (HH:MM), number of courts.
Price: 800 Rs per court. Check availability, create customer, save booking."""

@function_tool()
def check_availability_func(booking_date: str) -> str:
    courts = lovable_manager.check_availability(booking_date)
    if not courts: return f"No courts available on {booking_date}"
    return f"Available courts on {booking_date}: {len(courts)} courts with slots"

@function_tool()
def save_booking_func(customer_name: str, phone_number: str, booking_date: str, booking_time: str) -> str:
    customer = lovable_manager.get_or_create_customer(customer_name, phone_number)
    if not customer: return "Failed to create customer"
    courts = lovable_manager.check_availability(booking_date)
    if not courts: return f"No courts available on {booking_date}"
    booking = lovable_manager.create_booking(courts[0]['id'], phone_number, booking_date, booking_time, booking_time)
    return f"Booking confirmed! ID: {booking.get('id')}" if booking else "Failed to create booking"

async def prewarm(proc: JobContext):
    await proc.download_files(silero.VAD.model_fqn, openai.STT.model_fqn, openai.LLM.model_fqn)

async def entrypoint(ctx: JobContext):
    assistant = VoiceAssistant(
        vad=silero.VAD.create(),
        stt=openai.STT(),
        llm=openai.LLM(),
        tts=openai.TTS(),
        ctx=llm.ChatContext().add(role="system", text=SYSTEM_PROMPT),
    )
    assistant.add_tool(check_availability_func, auto_execute=True)
    assistant.add_tool(save_booking_func)
    await assistant.start(ctx)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint=entrypoint, prewarm_duration=15))
