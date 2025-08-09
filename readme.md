# Full-Duplex AI Voice Agent with Deepgram STT, Google Gemini LLM, and pyttsx3 TTS


This project is a real-time full-duplex voice assistant built in Python. It continuously listens to your voice using **Deepgram streaming Speech-to-Text (STT)**, sends your speech transcripts to **Google Gemini 2.5 Flash Lite** LLM for natural language understanding and response generation, and then speaks the response back to you using **offline pyttsx3 Text-to-Speech (TTS)**. The system supports interruption, allowing it to stop speaking and respond immediately to new user input.

---

## Features

- **Full-duplex voice interaction:** Simultaneous listening and speaking without blocking each other.  
- **Streaming real-time transcription:** Using Deepgram’s powerful streaming STT API.  
- **Conversational AI powered by Google Gemini 2.5 Flash Lite:** Natural, context-aware replies via Langchain’s Google Generative AI integration.  
- **Offline Text-to-Speech with pyttsx3:** Fast, low-latency speech synthesis without internet dependency.  
- **Speech interruption handling:** Stops ongoing speech when new user input is detected.  

---

## Getting Started

### Prerequisites

- Python 3.8 or higher  
- Deepgram API key  
- Google Cloud API key with access to Gemini model  
- Virtual environment (recommended)

### Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/voice-agent.git
   cd voice-agent
````

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with the following variables:

   ```env
   DEEPGRAM_API_KEY=your_deepgram_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   ```

---

## Usage

Run the voice agent with:

```bash
python3 -m voice.voice_agent
```

Speak into your microphone. The assistant will transcribe your speech, send it to Google Gemini for a response, and speak the reply aloud.

Press `Ctrl+C` to stop the agent gracefully.

---

## Project Structure

```
voice-agent/
│
├── voice/
│   ├── __init__.py
│   ├── tts.py           # pyttsx3 Text-to-Speech wrapper with threading and interruption
│   ├── stt.py           # Deepgram streaming Speech-to-Text async client
│
├── llm.py               # Google Gemini 2.5 Flash Lite LLM integration using Langchain
├── requirements.txt     # Python dependencies
├── voice_agent.py   # Main integration script running the full-duplex voice agent
└── README.md            # This file
```

---

## Notes

* Ensure your microphone is correctly configured and accessible to the application.
* pyttsx3 voice options and rates can be customized in `tts.py`.
* Google Gemini access requires enabling Vertex AI and generative AI API on Google Cloud Console.
* For best performance, use a good quality microphone and quiet environment.

---

## License

MIT License © Your Name

---

## Acknowledgments

* [Deepgram](https://deepgram.com) for their real-time speech-to-text API
* [Google Vertex AI](https://cloud.google.com/vertex-ai) for Gemini generative models
* [pyttsx3](https://pyttsx3.readthedocs.io/) for offline TTS in Python
* [Langchain](https://python.langchain.com/en/latest/) for simplifying LLM integration

---

If you want me to add example commands, troubleshooting tips, or contribution guidelines, just ask!

