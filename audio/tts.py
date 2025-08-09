# voice/tts.py
import pyttsx3
import threading
import time

# Initialize the engine
engine = pyttsx3.init()

# Lock for thread safety
lock = threading.Lock()

# Flag to stop speaking
stop_flag = False

def speak(text: str, rate: int = 200, volume: float = 1.0, voice_index: int = 2):
    """
    Convert text to speech using pyttsx3 (offline) with interruption support.
    """
    global stop_flag
    stop_flag = False

    def _run():
        global stop_flag
        with lock:
            try:
                # Set speaking rate
                engine.setProperty('rate', rate)
                # Set volume
                engine.setProperty('volume', volume)
                # Set voice
                voices = engine.getProperty('voices')
                if 0 <= voice_index < len(voices):
                    engine.setProperty('voice', voices[voice_index].id)

                # Speak text
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"[TTS Error] {e}")

    t = threading.Thread(target=_run)
    t.start()
    return t

def stop_speaking():
    """
    Stop the speech immediately.
    """
    global stop_flag
    with lock:
        try:
            engine.stop()
            stop_flag = True
        except Exception as e:
            print(f"[TTS Error] {e}")

if __name__ == "__main__":
    # Example usage
    t = speak("Hello Gaurav, this is offline text to speech with interruption feature.")
    time.sleep(2)  # Let it speak for 2 seconds
    print("Stopping mid-sentence...")
    stop_speaking()
