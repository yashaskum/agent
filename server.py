"""
JARVIS FastAPI Server
Main entry point coordinating WebSocket real-time telemetry,
REST endpoints for commands and speech synthesis, and static HUD hosting.
"""

import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List

import system_control
from tts_engine import tts_instance
from jarvis_brain import brain_instance

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "audio"), exist_ok=True)

app = FastAPI(title="J.A.R.V.I.S. Core", description="Stark Industries AI Command Center")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_private_network_headers(request, call_next):
    """Support W3C Private Network Access so HTTPS cloud apps can talk to localhost."""
    response = await call_next(request)
    response.headers["Access-Control-Allow-Private-Network"] = "true"
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

# Mount static folder
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/api/bridge/ping")
async def ping_bridge():
    """Endpoint for Vercel app to verify local hardware bridge is online."""
    return {"status": "online", "system": "JARVIS Local Hardware Bridge", "version": "Mark VII"}

class CommandRequest(BaseModel):
    text: str

class SpeakRequest(BaseModel):
    text: str
    voice: Optional[str] = None

@app.get("/")
async def get_index():
    """Serve HUD interface."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"status": "JARVIS Core Online", "docs": "/docs"})

@app.get("/api/telemetry")
async def get_telemetry():
    """Real-time system diagnostics."""
    return system_control.get_system_telemetry()

@app.post("/api/speak")
async def speak_text(req: SpeakRequest):
    """Generate TTS audio and return audio URL."""
    audio_url, _ = await tts_instance.generate_speech(req.text)
    return {"audio_url": audio_url, "text": req.text}

@app.post("/api/command")
async def process_command(req: CommandRequest):
    """Process natural language command and synthesize JARVIS voice response."""
    result = await brain_instance.process_input(req.text)
    audio_url, _ = await tts_instance.generate_speech(result["response_text"])
    
    return {
        "user_text": req.text,
        "response_text": result["response_text"],
        "audio_url": audio_url,
        "action": result["action"],
        "data": result["data"],
        "status": result["status"]
    }

# Active WebSocket connections
active_connections: List[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    print("[WebSocket] Client connected to JARVIS HUD.")
    
    # Broadcast welcome status
    welcome_telemetry = system_control.get_system_telemetry()
    await websocket.send_json({
        "type": "init",
        "message": "MARK VII INTERFACE SYNCHRONIZED",
        "telemetry": welcome_telemetry
    })

    try:
        # Background task for periodic telemetry stream
        async def telemetry_loop():
            while True:
                await asyncio.sleep(2.0)
                try:
                    telemetry = system_control.get_system_telemetry()
                    await websocket.send_json({
                        "type": "telemetry",
                        "data": telemetry
                    })
                except Exception:
                    break

        telemetry_task = asyncio.create_task(telemetry_loop())

        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "command")
            
            if msg_type == "command":
                user_text = data.get("text", "")
                # Notify client that JARVIS is analyzing
                await websocket.send_json({"type": "status", "state": "THINKING"})
                
                result = await brain_instance.process_input(user_text)
                audio_url, _ = await tts_instance.generate_speech(result["response_text"])
                
                await websocket.send_json({
                    "type": "response",
                    "user_text": user_text,
                    "response_text": result["response_text"],
                    "audio_url": audio_url,
                    "action": result["action"],
                    "data": result["data"],
                    "status": result["status"]
                })

    except WebSocketDisconnect:
        print("[WebSocket] Client disconnected.")
    except Exception as e:
        print(f"[WebSocket Error] {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)
        telemetry_task.cancel()

if __name__ == "__main__":
    import uvicorn
    print("\n==========================================")
    print("      J.A.R.V.I.S. SYSTEM ONLINE          ")
    print("   MARK VII TACTICAL HUD INITIALIZED     ")
    print("==========================================")
    print("  URL: http://localhost:8000\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
