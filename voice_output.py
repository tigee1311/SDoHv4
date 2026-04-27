"""Text-to-speech helpers for Streamlit voice playback."""

from io import BytesIO
import os

import streamlit as st
from gtts import gTTS

from language_manager import tts_locale


@st.cache_data(show_spinner=False)
def synthesize_gtts(text, lang):
    """Generate MP3 bytes with gTTS and cache identical prompts."""
    buffer = BytesIO()
    gTTS(text=text, lang=tts_locale(lang)).write_to_fp(buffer)
    return buffer.getvalue()


@st.cache_data(show_spinner=False)
def synthesize_elevenlabs(text, lang):
    """Generate MP3 bytes with ElevenLabs when API credentials are configured."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY is not set.")

    try:
        from elevenlabs.client import ElevenLabs
    except ImportError as exc:
        raise RuntimeError("Install elevenlabs to use the ElevenLabs voice option.") from exc

    client = ElevenLabs(api_key=api_key)
    audio = client.text_to_speech.convert(
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        text=text,
        output_format="mp3_44100_128",
    )
    return b"".join(audio)


def synthesize_speech(text, lang, provider="gTTS"):
    """Return MP3 bytes for Streamlit audio playback."""
    if provider == "ElevenLabs":
        return synthesize_elevenlabs(text, lang)
    return synthesize_gtts(text, lang)
