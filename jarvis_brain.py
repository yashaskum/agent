"""
JARVIS Conversational Brain & Intent Routing Engine
Combines built-in neural intent parsing, system control, Wikipedia intelligence,
notes & reminders, global news feeds, media keys, and optional LLM fallback (Gemini / OpenAI).
"""

import re
import os
import random
import datetime
from typing import Dict, Any, Tuple
import system_control

# System prompt for LLM fallback
JARVIS_SYSTEM_PROMPT = """
You are J.A.R.V.I.S. (Just A Rather Very Intelligent System), the sophisticated, loyal, and witty AI created by Tony Stark.
Key guidelines:
1. Address the user respectfully as "Sir" (or Master Stark).
2. Speak in polished, articulate British English with subtle wit, calm confidence, and supreme competence.
3. Keep spoken replies concise, punchy, and natural (1 to 3 sentences usually), as your responses are synthesized into voice audio.
4. When reporting system diagnostics or data, sound crisp and analytical.
"""

# Quick responses for common conversational prompts
GREETINGS = [
    "At your service, Sir.",
    "Good day, Sir. All systems are operating within optimal parameters.",
    "Online and ready, Sir. How may I be of assistance?",
    "Always a pleasure, Sir. What are we working on today?",
    "Greetings, Sir. Diagnostics are green across the board."
]

FAREWELLS = [
    "Powering down auxiliary systems. Have a pleasant day, Sir.",
    "Standing by in low-power mode, Sir. Call if you need anything.",
    "Shutting down speech interfaces. Farewell, Sir.",
    "Good night, Sir. I will monitor telemetry in the background."
]

AFFIRMATIONS = [
    "Right away, Sir.",
    "Consider it done, Sir.",
    "Executing now, Sir.",
    "Initiating protocol immediately, Sir.",
    "Working on that for you, Sir."
]

STATUS_PHRASES = [
    "Mark Seven protocols active. Power grid stable.",
    "Core telemetry is nominal. CPU and memory are well within safety thresholds.",
    "Arc reactor simulation operating at peak efficiency, Sir."
]

def calculate_expression(expr: str) -> str:
    """Safely calculate simple mathematical queries."""
    clean = re.sub(r"[^0-9\+\-\*\/\.\(\)\%\^ ]", "", expr).replace("^", "**")
    try:
        if any(c in clean for c in "+-*/%"):
            result = eval(clean, {"__builtins__": None}, {})
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return f"The result is {result}, Sir."
    except Exception:
        pass
    return ""

class JarvisBrain:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self.pending_confirmation = None

    async def process_input(self, user_text: str) -> Dict[str, Any]:
        """
        Processes text command or speech transcript.
        Returns:
            {
                "response_text": str,
                "action": str or None,
                "data": dict or None,
                "status": str
            }
        """
        raw_text = user_text.strip()
        text = raw_text.lower()
        
        # Remove common introductory words
        text_clean = re.sub(r"^(jarvis|hey jarvis|ok jarvis|hello jarvis|yo jarvis)[,\s]*", "", text).strip()
        if not text_clean:
            return {
                "response_text": random.choice(GREETINGS),
                "action": "greeting",
                "data": None,
                "status": "ready"
            }

        # Explicit confirmation is required for actions that end a session or process.
        if self.pending_confirmation:
            if re.search(r"\b(confirm|yes|proceed|do it|approved)\b", text_clean):
                pending = self.pending_confirmation
                self.pending_confirmation = None
                res = pending["handler"]()
                return {
                    "response_text": res["message"],
                    "action": pending["action"],
                    "data": res,
                    "status": "executed" if res.get("success") else "error"
                }
            if re.search(r"\b(no|cancel|abort|stop)\b", text_clean):
                self.pending_confirmation = None
                return {
                    "response_text": "The pending operation has been cancelled, Sir.",
                    "action": "confirmation_cancelled",
                    "data": None,
                    "status": "ready"
                }

        # 1. Greetings
        if re.search(r"\b(hello|hi|hey|good morning|good afternoon|good evening|wake up)\b", text_clean):
            telemetry = system_control.get_system_telemetry()
            return {
                "response_text": f"{random.choice(GREETINGS)} Time is {telemetry['timestamp']}.",
                "action": "greeting",
                "data": telemetry,
                "status": "ready"
            }

        # 2. Farewells & Sleep
        if re.search(r"\b(goodbye|bye|go to sleep|exit|quit|stand down)\b", text_clean):
            return {
                "response_text": random.choice(FAREWELLS),
                "action": "shutdown",
                "data": None,
                "status": "standby"
            }

        power_match = re.search(r"\b(shut down|shutdown|restart|reboot|log off|logoff)\b", text_clean)
        if power_match:
            action_text = power_match.group(1).replace(" ", "")
            action = "restart" if action_text == "reboot" else action_text
            self.pending_confirmation = {
                "action": f"power_{action}",
                "handler": lambda action=action: system_control.power_action(action),
            }
            return {
                "response_text": f"{action.capitalize()} will affect your Windows session. Say confirm to proceed or cancel to abort, Sir.",
                "action": "confirmation_required",
                "data": {"pending_action": action},
                "status": "awaiting_confirmation"
            }

        # 3. Who are you / Identity
        if re.search(r"\b(who are you|what is your name|your identity|introduce yourself)\b", text_clean):
            return {
                "response_text": "I am J.A.R.V.I.S., Just A Rather Very Intelligent System. Your personal automated assistant, designed to manage your hardware, execute tasks, and streamline your operations, Sir.",
                "action": "identity",
                "data": None,
                "status": "ready"
            }

        # 4. System Status / Diagnostics
        if re.search(r"\b(system status|diagnostics|specs|battery|cpu|ram|memory|storage|disk|hardware|telemetry)\b", text_clean):
            telemetry = system_control.get_system_telemetry()
            battery_text = f"Battery is at {telemetry['battery']['percent']} percent." if telemetry['battery']['has_battery'] else "Running on constant AC power."
            diag_speech = (
                f"CPU load is currently {telemetry['cpu_percent']} percent across {telemetry['cpu_count']} cores. "
                f"Memory utilization is at {telemetry['ram_percent']} percent, with {telemetry['ram_free_gb']} gigabytes free. "
                f"{battery_text} System uptime is {telemetry['uptime']}."
            )
            return {
                "response_text": diag_speech,
                "action": "telemetry",
                "data": telemetry,
                "status": "analyzed"
            }

        if re.search(r"\b(help|what can you do|capabilities|commands)\b", text_clean):
            return {
                "response_text": "I can control approved desktop applications, open files and folders, inspect processes, manage media and volume, report diagnostics, search the web, manage notes, and prepare power actions with confirmation, Sir.",
                "action": "help",
                "data": None,
                "status": "ready"
            }

        if re.search(r"\b(who am i|current user|logged in user|computer name)\b", text_clean):
            identity = system_control.get_windows_user()
            return {
                "response_text": f"You are logged in as {identity['user']} on {identity['computer']}, Sir.",
                "action": "user_info",
                "data": identity,
                "status": "ready"
            }

        if re.search(r"\b(list processes|running processes|task list|what is running|show processes)\b", text_clean):
            processes = system_control.list_processes()
            return {
                "response_text": processes["summary"],
                "action": "process_list",
                "data": processes["processes"],
                "status": "ready"
            }

        kill_match = re.search(r"\b(?:close|stop|terminate|kill)\s+(?:the\s+)?(?:process\s+)?([a-zA-Z0-9_.-]+)\b", text_clean)
        if kill_match:
            identifier = kill_match.group(1)
            self.pending_confirmation = {
                "action": "process_terminate",
                "handler": lambda identifier=identifier: system_control.terminate_process(identifier),
            }
            return {
                "response_text": f"This will terminate the exact process '{identifier}'. Say confirm to proceed or cancel to abort, Sir.",
                "action": "confirmation_required",
                "data": {"pending_action": "process_terminate", "identifier": identifier},
                "status": "awaiting_confirmation"
            }

        # 5. Time & Date
        if re.search(r"\b(time|what time is it|clock)\b", text_clean) and not "weather" in text_clean:
            now = datetime.datetime.now()
            time_str = now.strftime("%I:%M %p")
            return {
                "response_text": f"The current time is {time_str}, Sir.",
                "action": "time",
                "data": {"time": time_str},
                "status": "ready"
            }

        if re.search(r"\b(date|what day is it|today's date)\b", text_clean):
            now = datetime.datetime.now()
            date_str = now.strftime("%A, %B %d, %Y")
            return {
                "response_text": f"Today is {date_str}, Sir.",
                "action": "date",
                "data": {"date": date_str},
                "status": "ready"
            }

        # 6. Weather
        if "weather" in text_clean or "temperature" in text_clean:
            city_match = re.search(r"(?:in|for|at)\s+([a-zA-Z\s]+)", text_clean)
            city = city_match.group(1).strip() if city_match else ""
            weather_res = system_control.get_weather(city)
            return {
                "response_text": weather_res["summary"],
                "action": "weather",
                "data": weather_res.get("data"),
                "status": "ready"
            }

        # 7. News Briefing
        if re.search(r"\b(news|headlines|briefing|intel update|current events)\b", text_clean):
            news_res = system_control.get_news_headlines(count=3)
            return {
                "response_text": news_res["summary"],
                "action": "news",
                "data": news_res.get("headlines"),
                "status": "ready"
            }

        # 8. Notes & Reminders
        note_take_match = re.search(r"\b(?:take a note|add note|remember that|note that|remind me to)[:\s]+(.*)", text_clean)
        if note_take_match:
            note_content = note_take_match.group(1).strip()
            res = system_control.save_note(note_content)
            return {
                "response_text": res["message"],
                "action": "note_save",
                "data": {"note": note_content},
                "status": "ready"
            }

        if re.search(r"\b(read my notes|get notes|show notes|list notes|what are my notes)\b", text_clean):
            notes_res = system_control.get_notes()
            return {
                "response_text": notes_res["summary"],
                "action": "note_read",
                "data": notes_res.get("notes"),
                "status": "ready"
            }

        if re.search(r"\b(clear notes|delete notes|purge notes)\b", text_clean):
            clear_res = system_control.clear_notes()
            return {
                "response_text": clear_res["message"],
                "action": "note_clear",
                "data": None,
                "status": "ready"
            }

        # 9. Media Playback Control
        if re.search(r"\b(play music|resume music|pause music|stop music|next song|next track|previous song|previous track)\b", text_clean):
            if "pause" in text_clean or "stop" in text_clean:
                res = system_control.control_media("pause")
            elif "next" in text_clean:
                res = system_control.control_media("next")
            elif "previous" in text_clean:
                res = system_control.control_media("previous")
            else:
                res = system_control.control_media("play")
            return {
                "response_text": res["message"],
                "action": "media_control",
                "data": None,
                "status": "ready"
            }

        # 10. System Locking & Recycling
        if re.search(r"\b(lock workstation|lock computer|lock screen|lock pc)\b", text_clean):
            res = system_control.lock_workstation()
            return {
                "response_text": res["message"],
                "action": "lock",
                "data": None,
                "status": "ready"
            }

        if re.search(r"\b(empty recycle bin|clear recycle bin|purge trash)\b", text_clean):
            self.pending_confirmation = {
                "action": "empty_recycle",
                "handler": system_control.empty_recycle_bin,
            }
            return {
                "response_text": "Emptying the recycle bin permanently removes its contents. Say confirm to proceed or cancel to abort, Sir.",
                "action": "confirmation_required",
                "data": {"pending_action": "empty_recycle"},
                "status": "awaiting_confirmation"
            }

        # 11. Math & Calculation
        if re.search(r"\b(calculate|what is|compute|solve)\b\s*([\d\+\-\*\/\.\(\)\s\^%]+)", text_clean):
            math_match = re.search(r"\b(?:calculate|what is|compute|solve)\s+(.*)", text_clean)
            if math_match:
                calc_res = calculate_expression(math_match.group(1))
                if calc_res:
                    return {
                        "response_text": calc_res,
                        "action": "calculation",
                        "data": None,
                        "status": "ready"
                    }

        # 12. Volume Control
        if "volume" in text_clean:
            if re.search(r"\b(up|increase|raise|higher|loud|louder)\b", text_clean):
                res = system_control.adjust_volume("up")
                return {"response_text": res["message"], "action": "volume_up", "data": None, "status": "ready"}
            elif re.search(r"\b(down|decrease|lower|softer|quiet|quieter)\b", text_clean):
                res = system_control.adjust_volume("down")
                return {"response_text": res["message"], "action": "volume_down", "data": None, "status": "ready"}
            elif re.search(r"\b(mute|silence|unmute)\b", text_clean):
                res = system_control.adjust_volume("mute")
                return {"response_text": res["message"], "action": "volume_mute", "data": None, "status": "ready"}

        # 13. App Launching
        path_match = re.search(r"\b(?:open|show|browse to)\s+(?:folder|file|path)?\s*([a-zA-Z]:[\\/][^?]*)$", raw_text, re.IGNORECASE)
        if path_match:
            path = path_match.group(1).strip().rstrip(" .,!?")
            res = system_control.open_path(path)
            return {
                "response_text": res["message"],
                "action": "open_path",
                "data": {"path": path},
                "status": "ready" if res.get("success") else "error"
            }

        open_match = re.search(r"\b(?:open|launch|start|run)\s+([a-zA-Z0-9\s]+)", text_clean)
        if open_match:
            target = open_match.group(1).strip()
            if target not in ("the weather", "diagnostics", "system status", "camera", "news"):
                res = system_control.launch_application(target)
                return {
                    "response_text": res["message"],
                    "action": "app_launch",
                    "data": {"app": target},
                    "status": "ready" if res.get("success") else "error"
                }

        # 14. Web Search
        search_match = re.search(r"\b(?:search|google|look up|find info on)\s+(.*)", text_clean)
        if search_match:
            query = search_match.group(1).strip()
            wiki_summary = system_control.get_quick_info(query)
            system_control.open_url_or_search(query, search=True)
            if wiki_summary:
                return {
                    "response_text": f"According to Wikipedia: {wiki_summary} I have also opened web results for you, Sir.",
                    "action": "web_search",
                    "data": {"query": query},
                    "status": "ready"
                }
            return {
                "response_text": f"Opening search results for '{query}', Sir.",
                "action": "web_search",
                "data": {"query": query},
                "status": "ready"
            }

        # 15. Quick Info / Who is / What is
        info_match = re.search(r"\b(?:who is|what is|tell me about|explain)\s+([a-zA-Z0-9\s]+)", text_clean)
        if info_match:
            topic = info_match.group(1).strip()
            wiki_summary = system_control.get_quick_info(topic)
            if wiki_summary:
                return {
                    "response_text": f"{wiki_summary}",
                    "action": "info",
                    "data": {"topic": topic},
                    "status": "ready"
                }

        # 16. Fallback / LLM or Intelligent conversational response
        llm_response = await self._query_llm_if_available(raw_text)
        if llm_response:
            return {
                "response_text": llm_response,
                "action": "conversational",
                "data": None,
                "status": "ready"
            }

        # Default witty Jarvis fallback
        generic_fallbacks = [
            f"I have processed your statement regarding '{raw_text}', Sir. Standing by for your specific directive.",
            f"Sensors and analytical routines are processing '{raw_text}'. How would you like me to proceed with this, Sir?",
            f"Affirmative, Sir. All systems remain aligned and awaiting your command."
        ]
        return {
            "response_text": random.choice(generic_fallbacks),
            "action": "conversational",
            "data": None,
            "status": "ready"
        }

    async def _query_llm_if_available(self, prompt: str) -> str:
        """Query Gemini or OpenAI if API keys exist."""
        try:
            if self.gemini_key:
                import requests
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
                body = {
                    "contents": [{"parts": [{"text": f"{JARVIS_SYSTEM_PROMPT}\nUser query: {prompt}"}]}]
                }
                resp = requests.post(url, json=body, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        return text.strip()
        except Exception:
            pass
        return ""

brain_instance = JarvisBrain()
