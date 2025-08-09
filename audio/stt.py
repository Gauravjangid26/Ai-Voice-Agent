#stt.py
import asyncio
import os
from dotenv import load_dotenv
from deepgram import DeepgramClient, DeepgramClientOptions, LiveTranscriptionEvents, LiveOptions, Microphone

load_dotenv()

# Flag to detect interruption
user_interrupted = asyncio.Event()

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

transcript_collector = TranscriptCollector()


async def start_streaming_transcription(on_final_transcript_callback=None):
    try:
        api_key = os.getenv("DEEPGRAM_API_KEY")
        if not api_key:
            raise ValueError("DEEPGRAM_API_KEY environment variable not set")

        config = DeepgramClientOptions(options={"keepalive": "true"})
        deepgram = DeepgramClient(api_key, config)

        dg_connection = deepgram.listen.asyncwebsocket.v("1")

        async def on_message(self, result, **kwargs):
            try:
                if hasattr(result, 'channel') and result.channel.alternatives:
                    sentence = result.channel.alternatives[0].transcript
                    if sentence:
                        if not result.speech_final:
                            user_interrupted.set()  # 🔥 USER SPOKE (even partial)
                            transcript_collector.add_part(sentence)
                        else:
                            transcript_collector.add_part(sentence)
                            full_sentence = transcript_collector.get_full_transcript()
                            print(f"🗣️ User: {full_sentence}")
                            transcript_collector.reset()

                            if on_final_transcript_callback:
                                await on_final_transcript_callback(full_sentence)
            except Exception as e:
                print(f"❌ Error processing message: {e}")

        async def on_error(error, **kwargs):
            print(f"❌ Deepgram error: {error}")

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

        try:
            microphone = Microphone(dg_connection.send)
            microphone.start()
            print("🎤 Listening... Speak now.")
        except Exception as e:
            print(f"❌ Failed to initialize microphone: {e}")
            await dg_connection.finish()
            return

        try:
            while microphone.is_active():
                await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            print("🛑 Stopping transcription...")
        finally:
            microphone.finish()
            await dg_connection.finish()
            print("✅ Transcription finished.")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")


async def wait_for_user_input():
    global user_interrupted
    user_interrupted.clear()

    print("🕒 Waiting for user to speak...")

    while not user_interrupted.is_set():
        await asyncio.sleep(0.1)

    print("✅ User started speaking!")


if __name__ == "__main__":
    asyncio.run(start_streaming_transcription())
