"""
============================================================
voice.py  –  Optional Voice Input / Output Module
============================================================
Uses SpeechRecognition for STT and pyttsx3 for TTS.

Both libraries are OPTIONAL.  If they are not installed or if
the microphone / API is unavailable, the module gracefully
falls back and returns None so the app can switch to text.
============================================================
"""

# ── Try importing optional libraries ──────────────────────
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False


def listen_from_mic(timeout: int = 5, phrase_limit: int = 10) -> str | None:
    """
    Capture audio from the microphone and convert to text.

    Returns the recognized text, or None if:
      • SpeechRecognition is not installed
      • No microphone detected
      • Google Speech API is unreachable
      • Recognition fails

    Parameters
    ----------
    timeout       : seconds to wait for speech to start
    phrase_limit  : max seconds of speech to capture
    """
    if not SR_AVAILABLE:
        return None

    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            # Adjust for ambient noise briefly
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_limit,
            )
        # Use Google Web Speech API (free, no key needed)
        text = recognizer.recognize_google(audio)
        return text

    except sr.WaitTimeoutError:
        return None
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        # API unreachable – fall back to text input
        return None
    except OSError:
        # No microphone hardware
        return None
    except Exception:
        # Catch-all for any other error
        return None


import re

def speak(text: str) -> bool:
    """
    Speak the given text aloud using pyttsx3.

    Returns True if successful, False otherwise.
    """
    if not TTS_AVAILABLE:
        return False

    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 160)     # slightly slower for clarity
        engine.setProperty("volume", 0.9)
        # Remove emojis and non-speech symbols before speaking
        clean_text = re.sub(r'[^\w\s,\.\?!-]', '', text)
        engine.say(clean_text)
        engine.runAndWait()
        return True
    except Exception:
        return False


def is_voice_available() -> dict:
    """
    Check which voice features are available.

    Returns a dict:
        stt : bool – speech-to-text available
        tts : bool – text-to-speech available
    """
    return {
        "stt": SR_AVAILABLE,
        "tts": TTS_AVAILABLE,
    }
