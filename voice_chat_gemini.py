# full_duplex_agent.py
import asyncio
import threading
from audio.tts import speak, stop_speaking
from audio.stt import start_streaming_transcription
from llm import llm

# A lock to protect TTS calls and allow safe interruption
tts_lock = threading.Lock()
current_tts_thread = None

async def on_final_transcript(text: str):
    global current_tts_thread

    print(f"🗣️ Recognized: {text}")

    # Stop any ongoing TTS before speaking new response
    with tts_lock:
        if current_tts_thread and current_tts_thread.is_alive():
            print("⏹️ Stopping ongoing speech...")
            stop_speaking()
            current_tts_thread.join()
        #llm
        response=llm.invoke(text)

        # Start new TTS thread to speak response asynchronously
        current_tts_thread = speak(f"You said: {response}")

async def main():
    # Run the Deepgram streaming transcription with the callback
    await start_streaming_transcription(on_final_transcript_callback=on_final_transcript)

if __name__ == "__main__":
    try:
        print("🚀 Starting full duplex voice agent...")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Voice agent stopped by user.")
