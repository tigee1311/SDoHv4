"""Speech-to-text helpers for Streamlit audio answers."""

from io import BytesIO
import os
import tempfile
import wave

import speech_recognition as sr
import streamlit as st

from language_manager import speech_locale


def _read_audio_bytes(audio_file):
    if audio_file is None:
        return b""
    if hasattr(audio_file, "getvalue"):
        return audio_file.getvalue()
    return audio_file.read()


def _looks_like_wav(audio_bytes):
    return audio_bytes[:4] == b"RIFF" and audio_bytes[8:12] == b"WAVE"


def _wav_duration_seconds(audio_bytes):
    try:
        with wave.open(BytesIO(audio_bytes), "rb") as wav_file:
            return wav_file.getnframes() / float(wav_file.getframerate())
    except Exception:
        return None


def transcribe_with_openai(audio_bytes, lang):
    """Transcribe browser-recorded audio with OpenAI Whisper."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    from openai import OpenAI

    suffix = ".wav" if _looks_like_wav(audio_bytes) else ".webm"
    with tempfile.NamedTemporaryFile(suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        with open(tmp.name, "rb") as audio_file:
            transcript = OpenAI(api_key=api_key).audio.transcriptions.create(
                model=os.getenv("OPENAI_TRANSCRIPTION_MODEL", "whisper-1"),
                file=audio_file,
                language=lang,
            )
    return getattr(transcript, "text", "").strip(), None


def transcribe_with_speech_recognition(audio_bytes, lang):
    """Fallback transcription using the local speech_recognition package."""
    if not _looks_like_wav(audio_bytes):
        raise RuntimeError("Local speech_recognition fallback requires WAV audio.")

    recognizer = sr.Recognizer()
    with sr.AudioFile(BytesIO(audio_bytes)) as source:
        audio = recognizer.record(source)
    text = recognizer.recognize_google(audio, language=speech_locale(lang))
    return text.strip(), None


def transcribe_audio(audio_file, lang, prefer_openai=True):
    """Transcribe a Streamlit audio_input object and return text plus metadata."""
    audio_bytes = _read_audio_bytes(audio_file)
    if not audio_bytes:
        return "", {"engine": None, "confidence": None, "duration": None}

    duration = _wav_duration_seconds(audio_bytes)
    if prefer_openai and os.getenv("OPENAI_API_KEY"):
        text, confidence = transcribe_with_openai(audio_bytes, lang)
        return text, {"engine": "openai_whisper", "confidence": confidence, "duration": duration}

    text, confidence = transcribe_with_speech_recognition(audio_bytes, lang)
    return text, {"engine": "speech_recognition_google", "confidence": confidence, "duration": duration}


def streamlit_audio_input(label, key):
    """Compatibility wrapper for Streamlit versions that include audio_input."""
    if not hasattr(st, "audio_input"):
        st.info("Upgrade Streamlit to use browser microphone recording: pip install --upgrade streamlit")
        return None
    return st.audio_input(label, key=key)
