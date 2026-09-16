"""
JARVIS System Control Module
Provides hardware telemetry, process execution, application launching,
media control, notes management, news feed, and system utilities on Windows.
"""

import os
import sys
import json
import psutil
import datetime
import subprocess
import webbrowser
import requests
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, List

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
NOTES_FILE = os.path.join(DATA_DIR, "notes.json")

APP_SHORTCUTS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "edge": "msedge.exe",
    "microsoft edge": "msedge.exe",
    "terminal": "wt.exe",
    "powershell": "powershell.exe",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "task manager": "taskmgr.exe",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "files": "explorer.exe",
    "vscode": "code",
    "code": "code",
    "paint": "mspaint.exe",
    "settings": "ms-settings:",
    "spotify": "spotify.exe",
}

def get_system_telemetry() -> Dict[str, Any]:
    """Gather real-time CPU, RAM, Disk, and Battery diagnostics."""
    cpu_usage = psutil.cpu_percent(interval=None)
    cpu_count = psutil.cpu_count(logical=True)
    
    mem = psutil.virtual_memory()
    ram_usage = mem.percent
    ram_total_gb = round(mem.total / (1024 ** 3), 1)
    ram_used_gb = round(mem.used / (1024 ** 3), 1)
    ram_free_gb = round(mem.available / (1024 ** 3), 1)
    
    disk = psutil.disk_usage("C:\\")
    disk_usage = disk.percent
    disk_total_gb = round(disk.total / (1024 ** 3), 1)
    disk_free_gb = round(disk.free / (1024 ** 3), 1)
    
    battery = psutil.sensors_battery()
    battery_info = {
        "percent": battery.percent if battery else 100,
        "power_plugged": battery.power_plugged if battery else True,
        "has_battery": battery is not None
    }
    
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = str(datetime.datetime.now() - boot_time).split('.')[0]
    
    return {
        "cpu_percent": cpu_usage,
        "cpu_count": cpu_count,
        "ram_percent": ram_usage,
        "ram_total_gb": ram_total_gb,
        "ram_used_gb": ram_used_gb,
        "ram_free_gb": ram_free_gb,
        "disk_percent": disk_usage,
        "disk_total_gb": disk_total_gb,
        "disk_free_gb": disk_free_gb,
        "battery": battery_info,
        "uptime": uptime,
        "active_processes": len(psutil.pids()),
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }

def launch_application(app_name: str) -> Dict[str, Any]:
    """Launch recognized desktop application or executable."""
    cleaned = app_name.lower().strip()
    target = APP_SHORTCUTS.get(cleaned)
    
    try:
        if target:
            if target.startswith("ms-"):
                os.system(f"start {target}")
            else:
                subprocess.Popen(target, shell=True)
            return {"success": True, "message": f"Launching {app_name.capitalize()}, Sir."}
        else:
            subprocess.Popen(cleaned, shell=True)
            return {"success": True, "message": f"Executing command for {app_name}, Sir."}
    except Exception as e:
        return {"success": False, "message": f"I was unable to launch {app_name}. Error: {str(e)}"}

def open_url_or_search(query: str, search: bool = True) -> Dict[str, Any]:
    """Open URL or search via browser."""
    try:
        if search:
            url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
            webbrowser.open(url)
            return {"success": True, "message": f"Searching Google for '{query}', Sir."}
        else:
            if not query.startswith(("http://", "https://")):
                query = "https://" + query
            webbrowser.open(query)
            return {"success": True, "message": f"Opening {query}, Sir."}
    except Exception as e:
        return {"success": False, "message": f"Browser navigation failed: {str(e)}"}

def adjust_volume(action: str) -> Dict[str, Any]:
    """Adjust system master volume via Windows PowerShell audio key emulation."""
    steps = 5 if action.lower() in ("up", "down") else 1
    
    ps_cmd = f"""
    $wsh = New-Object -ComObject WScript.Shell
    1..{steps} | ForEach-Object {{ $wsh.SendKeys([char]175) }}
    """ if action.lower() == "up" else f"""
    $wsh = New-Object -ComObject WScript.Shell
    1..{steps} | ForEach-Object {{ $wsh.SendKeys([char]174) }}
    """ if action.lower() == "down" else """
    $wsh = New-Object -ComObject WScript.Shell
    $wsh.SendKeys([char]173)
    """
    
    try:
        subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, timeout=3)
        return {"success": True, "message": f"Volume adjusted: {action}, Sir."}
    except Exception as e:
        return {"success": False, "message": f"Volume adjustment failed: {str(e)}"}

def control_media(action: str) -> Dict[str, Any]:
    """Control media playback (play/pause, next track, previous track)."""
    key_codes = {
        "play": 179,     # VK_MEDIA_PLAY_PAUSE
        "pause": 179,
        "toggle": 179,
        "next": 176,     # VK_MEDIA_NEXT_TRACK
        "previous": 177, # VK_MEDIA_PREV_TRACK
        "stop": 178      # VK_MEDIA_STOP
    }
    code = key_codes.get(action.lower(), 179)
    ps_cmd = f"""
    $wsh = New-Object -ComObject WScript.Shell
    $wsh.SendKeys([char]{code})
    """
    try:
        subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, timeout=3)
        return {"success": True, "message": f"Media command '{action}' transmitted, Sir."}
    except Exception as e:
        return {"success": False, "message": f"Media control error: {str(e)}"}

def lock_workstation() -> Dict[str, Any]:
    """Lock the Windows desktop session."""
    try:
        subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
        return {"success": True, "message": "Securing workstation and locking terminal, Sir."}
    except Exception as e:
        return {"success": False, "message": f"Unable to lock system: {str(e)}"}

def empty_recycle_bin() -> Dict[str, Any]:
    """Purge the Windows Recycle Bin."""
    try:
        subprocess.run(["powershell", "-Command", "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"], capture_output=True, timeout=5)
        return {"success": True, "message": "Recycle bin has been completely purged, Sir."}
    except Exception as e:
        return {"success": False, "message": f"Unable to clear recycle bin: {str(e)}"}

def get_weather(city: str = "") -> Dict[str, Any]:
    """Get live weather information using wttr.in."""
    try:
        loc = city.strip() if city else ""
        url = f"https://wttr.in/{loc}?format=j1"
        resp = requests.get(url, timeout=4)
        if resp.status_code == 200:
            data = resp.json()
            current = data.get("current_condition", [{}])[0]
            temp_c = current.get("temp_C", "N/A")
            desc = current.get("weatherDesc", [{}])[0].get("value", "Clear")
            humidity = current.get("humidity", "N/A")
            wind_speed = current.get("windspeedKmph", "N/A")
            location_name = city.capitalize() if city else "Current Location"
            summary = f"The weather in {location_name} is currently {desc} at {temp_c}° Celsius with {humidity}% humidity and wind speeds of {wind_speed} km/h."
            return {"success": True, "summary": summary, "data": current}
    except Exception:
        pass
    return {"success": False, "summary": "Sensors are unable to acquire localized meteorological data at this moment, Sir."}

def get_quick_info(topic: str) -> Optional[str]:
    """Fetch a concise Wikipedia summary for a topic."""
    try:
        endpoint = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(topic)}"
        resp = requests.get(endpoint, headers={"User-Agent": "JarvisAI/1.0"}, timeout=4)
        if resp.status_code == 200:
            data = resp.json()
            extract = data.get("extract")
            if extract:
                sentences = extract.split(". ")
                short_summary = ". ".join(sentences[:2])
                if not short_summary.endswith("."):
                    short_summary += "."
                return short_summary
    except Exception:
        pass
    return None

def get_news_headlines(count: int = 3) -> Dict[str, Any]:
    """Retrieve top global news headlines from RSS feed."""
    try:
        url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            root = ET.fromstring(resp.content)
            items = root.findall(".//item")[:count]
            headlines = []
            for item in items:
                title = item.find("title").text
                # Clean publisher suffix like "- BBC"
                clean_title = title.split(" - ")[0]
                headlines.append(clean_title)
            
            if headlines:
                summary = "Here are the top headlines from intelligence feeds, Sir: " + "; ".join(f"{i+1}. {h}" for i, h in enumerate(headlines)) + "."
                return {"success": True, "summary": summary, "headlines": headlines}
    except Exception as e:
        pass
    return {"success": False, "summary": "Intelligence news feeds are temporarily unavailable, Sir."}

# Notes & Reminders
def save_note(note_text: str) -> Dict[str, Any]:
    """Append a note with timestamp to notes.json."""
    try:
        notes = []
        if os.path.exists(NOTES_FILE):
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                notes = json.load(f)
        
        entry = {
            "id": len(notes) + 1,
            "text": note_text.strip(),
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        notes.append(entry)
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(notes, f, indent=2)
        return {"success": True, "message": f"Note recorded: '{note_text}', Sir."}
    except Exception as e:
        return {"success": False, "message": f"Failed to record note: {str(e)}"}

def get_notes() -> Dict[str, Any]:
    """Retrieve all recorded notes."""
    try:
        if not os.path.exists(NOTES_FILE):
            return {"success": True, "summary": "You have no recorded notes in memory, Sir.", "notes": []}
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            notes = json.load(f)
        if not notes:
            return {"success": True, "summary": "You have no recorded notes in memory, Sir.", "notes": []}
        
        summary = f"You have {len(notes)} note{'s' if len(notes) > 1 else ''} on file, Sir: " + "; ".join(f"{n['id']}: {n['text']}" for n in notes[-4:])
        return {"success": True, "summary": summary, "notes": notes}
    except Exception as e:
        return {"success": False, "summary": f"Could not access notes log, Sir."}

def clear_notes() -> Dict[str, Any]:
    """Clear all recorded notes."""
    try:
        if os.path.exists(NOTES_FILE):
            os.remove(NOTES_FILE)
        return {"success": True, "message": "All notes have been cleared from memory, Sir."}
    except Exception as e:
        return {"success": False, "message": f"Could not clear notes: {str(e)}"}
