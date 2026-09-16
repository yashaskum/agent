# J.A.R.V.I.S. // Stark Industries Mark VII Tactical HUD & Talking Model

A high-tech, voice-enabled **J.A.R.V.I.S. (Just A Rather Very Intelligent System)** clone featuring an interactive **Iron Man Arc Reactor 3D audio-reactive visualizer**, real-time British neural speech synthesis, speech recognition, Windows hardware telemetry, and automated system commands.

---

## 🌟 Key Features

1. **60 FPS Arc Reactor Talking Model**:
   - Audio-reactive concentric rings, tech gears, and glowing core.
   - Distinct visualizer states: `STANDBY`, `LISTENING` (amber glow), `THINKING` (fast rotation), `SPEAKING` (audio waveform bars).
   - Driven directly by the real-time audio frequency spectrum via the Web Audio API.

2. **Authentic British Neural Voice**:
   - Powered by Microsoft's `en-GB-RyanNeural` voice (closest match to Paul Bettany's JARVIS).
   - Zero API key required, zero subscription cost.
   - Built-in audio caching for instantaneous responses.

3. **Voice & Text Interaction**:
   - Real-time speech recognition via browser Web Speech API.
   - Spacebar shortcut: Press or hold `[SPACE]` to trigger speech input.
   - Text console fallback for silent typing commands.

4. **Live Hardware Diagnostics**:
   - Real-time CPU load, multi-thread core count.
   - RAM allocation and utilization gauges.
   - Primary disk (C:) storage monitoring.
   - Battery level, charging/AC power state, and system uptime.

5. **Built-in System Automation & Skills**:
   - **Launch Apps**: "Open Chrome", "Open Notepad", "Open Calculator", "Open VS Code", "Launch Terminal".
   - **Volume Control**: "Volume up", "Volume down", "Mute".
   - **Live Weather**: "What is the weather like in New York / London / Tokyo?"
   - **System Specs**: "What are my system specs?", "Check diagnostics".
   - **Web Search & Knowledge**: "Search Google for quantum computing", "Who is Tony Stark?".
   - **Math Calculations**: "What is 452 multiplied by 18?".
   - **Process Control**: "List running processes" and confirmation-gated exact process termination.
   - **File & Folder Control**: "Open C:\\Users\\Name\\Downloads" or another existing local path.
   - **Session Identity**: "Who am I?" or "What computer am I using?".
   - **Power Controls**: Shutdown, restart, and logoff requests require a second `confirm` command.

   App launching is restricted to registered shortcuts or executables discoverable on the system PATH;
   arbitrary shell strings are not executed. Destructive operations such as power actions, process
   termination, and recycle-bin clearing should be treated as privileged commands.

---

## 🚀 Quick Start

### 1. Launch J.A.R.V.I.S.
Double-click `run_jarvis.bat` or run:
```bash
python start.py
```
This will start the local server and automatically open the holographic HUD in your default browser at:
```
http://localhost:8000
```

### 2. Voice Commands to Try:
- *"Hello Jarvis"*
- *"Run system diagnostics"*
- *"What is the time and date?"*
- *"What is the weather today?"*
- *"Open Google Chrome"*
- *"Open Notepad"*
- *"Volume up"*
- *"Who is Tony Stark?"*
- *"Calculate 125 times 40"*
- *"List running processes"*
- *"Open C:\\Users\\Public"*
- *"Restart"*, then *"Confirm"* if you really mean it
- *"Good night Jarvis"*

---

## ⚙️ Optional LLM Cloud Brain Setup

JARVIS functions out-of-the-box with built-in intent parsing and Wikipedia summaries. If you'd like JARVIS to also answer open-ended questions using Gemini or OpenAI:

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```
2. Add your `GEMINI_API_KEY` or `OPENAI_API_KEY`.
3. Restart `start.py`.

---

## 📁 Project Architecture
```
c:\jarvis\
├── server.py             # FastAPI backend with WebSockets & REST API
├── jarvis_brain.py       # Conversational persona & intent routing engine
├── tts_engine.py         # British Neural Voice synthesis (Edge-TTS)
├── system_control.py     # Hardware telemetry, Windows automation, and apps
├── requirements.txt      # Python dependencies
├── start.py              # Self-verifying launcher script
├── run_jarvis.bat        # Windows one-click batch launcher
├── .env.example          # Environment variable template
└── static/
    ├── index.html        # Holographic HUD interface
    ├── style.css         # Cyber glassmorphism & Stark styling
    ├── reactor.js        # 60FPS Arc Reactor canvas & audio visualizer
    └── app.js            # Web Audio API, WebSockets, & Speech recognition
```
