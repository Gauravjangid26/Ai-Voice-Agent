from elevenlabs import ElevenLabs
from dotenv import load_dotenv
import os
import asyncio
import pyaudio
import pydub
import io
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise ValueError("Missing ELEVENLABS_API_KEY")

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
playback_active = False
audio_stream = None
pyaudio_instance = None

async def speak(text, voice_id="JBFqnCBsd6RMkjVDRZzb"):
    global playback_active, audio_stream, pyaudio_instance
    try:
        logging.info(f"Generating audio for text: {text[:50]}...")
        audio_chunks = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        playback_active = True
        pyaudio_instance = pyaudio.PyAudio()
        audio_stream = pyaudio_instance.open(
            format=pyaudio.paInt16,
            channels=2,  # MP3 is typically stereo
            rate=44100,
            output=True
        )
        logging.info("Playing audio...")
        # Buffer to collect MP3 chunks
        mp3_buffer = io.BytesIO()
        for chunk in audio_chunks:
            mp3_buffer.write(chunk)
        mp3_buffer.seek(0)
        # Decode MP3 to PCM using pydub
        audio_segment = pydub.AudioSegment.from_file(mp3_buffer, format="mp3")
        raw_data = audio_segment.raw_data
        # Play PCM data
        chunk_size = 4096
        for i in range(0, len(raw_data), chunk_size):
            if not playback_active:
                break
            audio_stream.write(raw_data[i:i + chunk_size])
        logging.info("Audio playback completed.")
    except Exception as e:
        logging.error(f"TTS error: {e}")
    finally:
        if audio_stream:
            audio_stream.stop_stream()
            audio_stream.close()
            audio_stream = None
        if pyaudio_instance:
            pyaudio_instance.terminate()
            pyaudio_instance = None
        playback_active = False

def stop_speech():
    global playback_active, audio_stream, pyaudio_instance
    playback_active = False
    if audio_stream:
        audio_stream.stop_stream()
        audio_stream.close()
        audio_stream = None
    if pyaudio_instance:
        pyaudio_instance.terminate()
        pyaudio_instance = None
    logging.info("TTS interrupted")