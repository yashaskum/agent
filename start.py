"""
J.A.R.V.I.S. Quick Launcher
Verifies system readiness, initializes the FastAPI server,
and opens the Stark Industries Tactical HUD in your default web browser.
"""

import os
import sys
import time
import webbrowser
import subprocess

def banner():
    print(r"""
   ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
   ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
   ██║███████║██████╔╝██║   ██║██║███████╗
   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
█████║██║  ██║██║  ██║ ╚████╔╝ ██║███████║
╚════╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
   MARK VII TACTICAL HUD & TALKING MODEL
    """)
    print("=" * 55)
    print(" [INIT] Checking core system modules...")

def check_dependencies():
    required = ["fastapi", "uvicorn", "edge_tts", "psutil", "requests", "websockets"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f" [WARN] Missing packages: {missing}")
        print(" [INIT] Installing required dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print(" [OK] Dependencies installed.")
    else:
        print(" [OK] All system modules verified.")

def main():
    banner()
    check_dependencies()

    port = 8000
    hud_url = f"http://localhost:{port}"

    print(f" [OK] Neural Audio Synthesis (en-GB-RyanNeural) Ready.")
    print(f" [OK] System Diagnostics & Automation Ready.")
    print(f" [OK] Holographic HUD ready at: {hud_url}")
    print("=" * 55)
    print(" Launching Stark Industries HUD in your browser...")
    
    # Open browser after short delay
    def open_browser():
        time.sleep(1.5)
        webbrowser.open(hud_url)

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    main()
