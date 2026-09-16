"""
JARVIS Text-to-Speech Engine
Generates British Neural Voice Audio using Edge-TTS (en-GB-RyanNeural)
with intelligent file caching for near-zero latency.
"""

import os
import hashlib
import asyncio
import edge_tts
from typing import Tuple

AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

# RyanNeural is the quintessential British assistant tone matching Paul Bettany's JARVIS
DEFAULT_VOICE = "en-GB-RyanNeural"
DEFAULT_RATE = "+2%"      # Crisp, analytical cadence
DEFAULT_PITCH = "-2Hz"    # Slightly deeper, authoritative resonance

class TTSEngine:
    def __init__(self, voice: str = DEFAULT_VOICE, rate: str = DEFAULT_RATE, pitch: str = DEFAULT_PITCH):
        self.voice = voice
        self.rate = rate
        self.pitch = pitch
        self.audio_dir = AUDIO_DIR
        os.makedirs(self.audio_dir, exist_ok=True)

    def _get_filename(self, text: str) -> str:
        """Create a stable hash key for caching."""
        clean_text = text.strip()
        text_hash = hashlib.md5(f"{clean_text}_{self.voice}_{self.rate}_{self.pitch}".encode("utf-8")).hexdigest()
        return f"jarvis_{text_hash}.mp3"

    async def generate_speech(self, text: str) -> Tuple[str, str]:
        """
        Synthesizes speech for the provided text.
        Returns (relative_url, absolute_path).
        """
        if not text or not text.strip():
            return "", ""

        filename = self._get_filename(text)
        filepath = os.path.join(self.audio_dir, filename)
        relative_url = f"/static/audio/{filename}"

        # If already cached, return immediately
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            return relative_url, filepath

        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=self.voice,
                rate=self.rate,
                pitch=self.pitch
            )
            await communicate.save(filepath)
            return relative_url, filepath
        except Exception as e:
            print(f"[TTS Error] Speech generation failed: {e}")
            return "", ""

# Singleton instance
tts_instance = TTSEngine()
