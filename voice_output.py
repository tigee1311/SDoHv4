"""Text-to-speech helpers for Streamlit voice playback."""

from io import BytesIO

import streamlit as st
from gtts import gTTS

from language_manager import tts_locale


@st.cache_data(show_spinner=False)
def synthesize_gtts(text, lang):
    """Generate MP3 bytes with gTTS and cache identical prompts."""
    buffer = BytesIO()
    gTTS(text=text, lang=tts_locale(lang)).write_to_fp(buffer)
    return buffer.getvalue()


def synthesize_speech(text, lang):
    """Return MP3 bytes for Streamlit audio playback."""
    return synthesize_gtts(text, lang)
