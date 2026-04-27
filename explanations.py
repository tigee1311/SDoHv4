"""Authoritative SDoH explanation text used by the questionnaire UI.

These are concise research-prototype summaries based on NIH's SDOH framing and
AMA guidance that social needs and structural conditions affect health outcomes.
"""

EXPLANATIONS = {
    "general_sdoh": {
        "source": "NIH / AMA",
        "en": (
            "Social determinants of health are the conditions where people are born, grow, "
            "work, live, and age. Asking this question helps identify social or practical "
            "needs that may affect health, access to care, or a patient's ability to follow a care plan."
        ),
        "es": (
            "Los determinantes sociales de la salud son las condiciones donde las personas nacen, "
            "crecen, trabajan, viven y envejecen. Esta pregunta ayuda a identificar necesidades "
            "sociales o prácticas que pueden afectar la salud, el acceso a la atención o la capacidad "
            "de seguir un plan de cuidado."
        ),
    },
    "housing_instability": {
        "source": "NIH / AMA",
        "en": (
            "Stable, safe housing supports health by making it easier to store medications, "
            "sleep, prepare food, keep appointments, and manage chronic conditions. Housing "
            "instability can create stress and make access to care less consistent."
        ),
        "es": (
            "Una vivienda estable y segura apoya la salud porque facilita guardar medicamentos, "
            "dormir, preparar alimentos, asistir a citas y manejar condiciones crónicas. La "
            "inestabilidad de vivienda puede generar estrés y dificultar el acceso constante a la atención."
        ),
    },
    "food_insecurity": {
        "source": "NIH / AMA",
        "en": (
            "Reliable access to enough nutritious food is closely connected to health. Food "
            "insecurity can affect energy, medication use, chronic disease management, and the "
            "ability to follow a care plan."
        ),
        "es": (
            "El acceso confiable a suficientes alimentos nutritivos está estrechamente relacionado "
            "con la salud. La inseguridad alimentaria puede afectar la energía, el uso de medicamentos, "
            "el manejo de enfermedades crónicas y la capacidad de seguir un plan de atención."
        ),
    },
    "transportation_access": {
        "source": "NIH / AMA",
        "en": (
            "Transportation is part of the conditions that shape access to health care, work, food, "
            "and other daily needs. Transportation barriers can lead to missed appointments, delayed "
            "care, and difficulty obtaining medications or essentials."
        ),
        "es": (
            "El transporte forma parte de las condiciones que influyen en el acceso a la atención médica, "
            "el trabajo, los alimentos y otras necesidades diarias. Las barreras de transporte pueden causar "
            "citas perdidas, atención retrasada y dificultad para obtener medicamentos o artículos esenciales."
        ),
    },
    "employment_income": {
        "source": "NIH / AMA",
        "en": (
            "Employment and income affect health through access to housing, food, transportation, "
            "insurance, and the resources needed for daily life. Financial strain can increase stress "
            "and make it harder to follow recommended care."
        ),
        "es": (
            "El empleo y los ingresos afectan la salud mediante el acceso a vivienda, alimentos, transporte, "
            "seguro médico y recursos para la vida diaria. Las dificultades económicas pueden aumentar el estrés "
            "y hacer más difícil seguir las recomendaciones de atención."
        ),
    },
    "social_support": {
        "source": "NIH / AMA",
        "en": (
            "Social support is part of the social environment that can protect health. Having people "
            "available for emotional support, advice, or practical help can reduce isolation and help "
            "patients manage health needs."
        ),
        "es": (
            "El apoyo social forma parte del entorno social que puede proteger la salud. Contar con personas "
            "disponibles para apoyo emocional, consejos o ayuda práctica puede reducir el aislamiento y ayudar "
            "a manejar necesidades de salud."
        ),
    },
}


SECTION_EXPLANATION_KEYS = {
    "Housing": "housing_instability",
    "Neighborhood": "housing_instability",
    "Food Insecurity": "food_insecurity",
    "Transportation": "transportation_access",
    "Income": "employment_income",
    "Employment": "employment_income",
    "Financial Strain": "employment_income",
    "Work & Labor": "employment_income",
    "Social Support": "social_support",
}


def explanation_for_question(question, lang):
    """Return explanation text and source label for a question's SDoH category."""
    key = SECTION_EXPLANATION_KEYS.get(question["section"], "general_sdoh")
    item = EXPLANATIONS[key]
    return item.get(lang, item["en"]), item["source"]


def question_with_explanation(question, lang):
    """Build speech text for a question plus its curated explanation when available."""
    text = question["text"][lang]
    explanation, _source = explanation_for_question(question, lang)
    if explanation:
        return f"{text} {explanation}"
    return text
