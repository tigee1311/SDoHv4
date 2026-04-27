"""Language helpers for the bilingual SDoH questionnaire."""

LANGUAGE_OPTIONS = {"English": "en", "Español": "es"}

LANGUAGE_NAMES = {"en": "English", "es": "Español"}

SPEECH_LOCALES = {"en": "en-US", "es": "es-US"}

TTS_LOCALES = {"en": "en", "es": "es"}


UI_TEXT = {
    "voice_settings": {"en": "Voice settings", "es": "Opciones de voz"},
    "tts_provider": {"en": "Voice output", "es": "Salida de voz"},
    "tts_gtts": {"en": "gTTS", "es": "gTTS"},
    "tts_elevenlabs": {"en": "ElevenLabs", "es": "ElevenLabs"},
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
}


QUESTION_EXPLANATIONS = {
    "Access to Health Services": {
        "en": "This section asks about access to routine and urgent health care.",
        "es": "Esta sección pregunta sobre el acceso a atención médica rutinaria y urgente.",
    },
    "Food Insecurity": {
        "en": "These questions help identify whether food needs are being met consistently.",
        "es": "Estas preguntas ayudan a identificar si las necesidades de comida se cubren de manera constante.",
    },
    "Health Literacy": {
        "en": "These questions ask how easy or difficult it is to use health information and forms.",
        "es": "Estas preguntas tratan sobre qué tan fácil o difícil es usar información y formularios de salud.",
    },
    "Housing": {
        "en": "This section asks about housing stability and safety.",
        "es": "Esta sección pregunta sobre estabilidad y seguridad de vivienda.",
    },
    "Transportation": {
        "en": "These questions ask whether transportation affects access to care and essentials.",
        "es": "Estas preguntas tratan sobre si el transporte afecta el acceso a atención y necesidades básicas.",
    },
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


def question_with_explanation(question, lang):
    """Build speech text for a question plus a short optional explanation."""
    text = question["text"][lang]
    explanation = QUESTION_EXPLANATIONS.get(question["section"], {}).get(lang)
    if explanation:
        return f"{text} {explanation}"
    return text
