import asyncio
import os
from dotenv import load_dotenv
from deepgram import DeepgramClient, DeepgramClientOptions, LiveTranscriptionEvents, LiveOptions, Microphone
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

load_dotenv()

class TranscriptCollector:
    def __init__(self):
        self.reset()

    def reset(self):
        self.transcript_parts = []

    def add_part(self, part):
        if part:
            self.transcript_parts.append(part)

    def get_full_transcript(self):
        return ' '.join(self.transcript_parts)

async def stream_transcripts(queue):
    transcript_collector = TranscriptCollector()

    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        raise ValueError("Missing DEEPGRAM_API_KEY")

    try:
        config = DeepgramClientOptions(options={"keepalive": "true"})
        deepgram = DeepgramClient(api_key, config)
        dg_connection = deepgram.listen.asyncwebsocket.v("1")

        async def on_message(self, result, **kwargs):
            try:
                if hasattr(result, 'channel') and result.channel.alternatives:
                    sentence = result.channel.alternatives[0].transcript
                    if sentence:
                        transcript_collector.add_part(sentence)
                        if result.speech_final:
                            full = transcript_collector.get_full_transcript()
                            await queue.put(full)
                            transcript_collector.reset()
            except Exception as e:
                logging.error(f"STT message error: {e}")

        async def on_error(error, **kwargs):
            logging.error(f"Deepgram error: {error}")

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)

        options = LiveOptions(
            model="nova-2",
            punctuate=True,
            language="en-US",
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            endpointing=True
        )

        await dg_connection.start(options)
        mic = Microphone(dg_connection.send)
        mic.start()
        logging.info("🎙️ Listening...")
        return mic, dg_connection

    except Exception as e:
        logging.error(f"STT setup error: {e}")
        raise