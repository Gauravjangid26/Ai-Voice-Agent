import asyncio
import os
import logging
from dotenv import load_dotenv
from audio.stt import stream_transcripts
from audio.tts import speak, stop_speech
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY")

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GOOGLE_API_KEY)

# State tracking
playback_task = None
conversation_history = []

async def conversation_loop():
    global playback_task, conversation_history
    queue = asyncio.Queue()
    mic = None
    dg_connection = None

    try:
        mic, dg_connection = await stream_transcripts(queue)
        
        while True:
            sentence = await queue.get()
            logging.info(f"🧍 You said: {sentence}")

            # Handle exit commands
            if sentence.lower().strip() in ["quit", "exit", "stop"]:
                logging.info("👋 Exiting.")
                break

            # Interrupt TTS if user speaks, with a small delay to allow short responses
            if playback_task:
                await asyncio.sleep(0.1)  # Brief delay to avoid immediate interruption
                if not queue.empty():  # Check if new input is waiting
                    stop_speech()
                    playback_task.cancel()
                    playback_task = None

            # Process with Gemini
            logging.info("🤖 Gemini is thinking...")
            try:
                conversation_history.append(HumanMessage(content=sentence))
                response = await llm.ainvoke(conversation_history)
                reply = response.content
                logging.info(f"🧠 Gemini: {reply}")
                conversation_history.append(AIMessage(content=reply))
                # Limit history to avoid excessive memory use
                if len(conversation_history) > 10:
                    conversation_history = conversation_history[-10:]
            except Exception as e:
                logging.error(f"Gemini error: {e}")
                reply = "Sorry, I couldn't process that."
                logging.info(f"🧠 Gemini: {reply}")
                conversation_history.append(AIMessage(content=reply))

            # Speak response
            if reply.strip():
                playback_task = asyncio.create_task(speak(reply))

    except asyncio.CancelledError:
        pass
    except Exception as e:
        logging.error(f"Main error: {e}")
    finally:
        if mic:
            mic.finish()
        if dg_connection:
            await dg_connection.finish()
        logging.info("🛑 Microphone stopped.")
        stop_speech()
        if playback_task:
            playback_task.cancel()

async def main():
    try:
        await conversation_loop()
    except KeyboardInterrupt:
        logging.info("Shutting down...")
    except Exception as e:
        logging.error(f"Main error: {e}")

if __name__ == "__main__":
    asyncio.run(main())