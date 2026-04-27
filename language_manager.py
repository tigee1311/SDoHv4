"""Language helpers for the bilingual SDoH questionnaire."""

LANGUAGE_OPTIONS = {"English": "en", "Español": "es"}

LANGUAGE_NAMES = {"en": "English", "es": "Español"}

SPEECH_LOCALES = {"en": "en-US", "es": "es-US"}

TTS_LOCALES = {"en": "en", "es": "es"}


UI_TEXT = {
    "voice_settings": {"en": "Voice settings", "es": "Opciones de voz"},
    "auto_read_next": {"en": "Auto-read next question", "es": "Leer automáticamente la siguiente pregunta"},
    "voice_help": {
        "en": "Use the microphone control under a question to record an answer, then click Transcribe.",
        "es": "Use el control de micrófono debajo de una pregunta para grabar una respuesta y luego pulse Transcribir.",
    },
    "speak": {"en": "Speak", "es": "Leer"},
    "record": {"en": "Mic", "es": "Mic"},
    "transcribe": {"en": "Transcribe", "es": "Transcribir"},
    "record_answer": {"en": "Record answer", "es": "Grabar respuesta"},
    "transcribing": {"en": "Transcribing audio...", "es": "Transcribiendo audio..."},
    "tts_loading": {"en": "Preparing audio...", "es": "Preparando audio..."},
    "empty_transcript": {"en": "No speech was detected.", "es": "No se detectó voz."},
    "voice_unavailable": {
        "en": "Voice input is unavailable. Check microphone access or API configuration.",
        "es": "La entrada de voz no está disponible. Revise el micrófono o la configuración de API.",
    },
    "tts_unavailable": {
        "en": "Voice output is unavailable.",
        "es": "La salida de voz no está disponible.",
    },
    "confidence": {"en": "Confidence", "es": "Confianza"},
    "why_question": {"en": "Why this question?", "es": "¿Por qué esta pregunta?"},
    "source": {"en": "Source", "es": "Fuente"},
}


def selected_language(label):
    """Return the internal language code for a visible language label."""
    return LANGUAGE_OPTIONS.get(label, "en")


def t(key, lang):
    """Translate a small UI string."""
    return UI_TEXT.get(key, {}).get(lang, UI_TEXT.get(key, {}).get("en", key))


def speech_locale(lang):
    return SPEECH_LOCALES.get(lang, "en-US")


def tts_locale(lang):
    return TTS_LOCALES.get(lang, "en")
