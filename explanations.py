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
    "healthcare_access": {
        "source": "NIH / AMA",
        "en": "Access to timely, affordable health care affects prevention, diagnosis, treatment, and management of ongoing health conditions.",
        "es": "El acceso oportuno y asequible a la atención médica afecta la prevención, el diagnóstico, el tratamiento y el manejo de condiciones de salud.",
    },
    "demographics": {
        "source": "NIH / AMA",
        "en": "Demographic information helps researchers understand whether health needs and access to care differ across populations.",
        "es": "La información demográfica ayuda a entender si las necesidades de salud y el acceso a la atención difieren entre poblaciones.",
    },
    "location_context": {
        "source": "NIH / AMA",
        "en": "Where a person lives can shape access to clinics, pharmacies, transportation, healthy food, safe spaces, and community resources.",
        "es": "El lugar donde vive una persona puede influir en el acceso a clínicas, farmacias, transporte, alimentos saludables, espacios seguros y recursos comunitarios.",
    },
    "education": {
        "source": "NIH / AMA",
        "en": "Education can affect employment, income, health literacy, and the ability to navigate health systems and health information.",
        "es": "La educación puede afectar el empleo, los ingresos, la alfabetización en salud y la capacidad de usar sistemas e información de salud.",
    },
    "language_access": {
        "source": "NIH / AMA",
        "en": "Language access affects communication with care teams, understanding of instructions, and the ability to use health services.",
        "es": "El acceso lingüístico afecta la comunicación con los equipos de atención, la comprensión de instrucciones y el uso de servicios de salud.",
    },
    "race_ethnicity": {
        "source": "NIH / AMA",
        "en": "Race and ethnicity data help identify inequities in health outcomes, access, quality of care, and exposure to social risk factors.",
        "es": "Los datos de raza y etnicidad ayudan a identificar inequidades en resultados de salud, acceso, calidad de atención y exposición a riesgos sociales.",
    },
    "insurance": {
        "source": "NIH / AMA",
        "en": "Health insurance coverage affects affordability of care, medications, preventive services, and follow-up treatment.",
        "es": "La cobertura de seguro médico afecta la asequibilidad de la atención, los medicamentos, los servicios preventivos y el seguimiento del tratamiento.",
    },
    "health_literacy": {
        "source": "NIH / AMA",
        "en": "Health literacy affects how people find, understand, and use health information to make care decisions.",
        "es": "La alfabetización en salud afecta cómo las personas encuentran, entienden y usan información de salud para tomar decisiones de atención.",
    },
    "general_health": {
        "source": "NIH / AMA",
        "en": "Self-rated health is a broad measure that helps identify overall health needs and possible barriers affecting daily well-being.",
        "es": "La salud autopercibida es una medida amplia que ayuda a identificar necesidades generales de salud y posibles barreras al bienestar diario.",
    },
    "identity": {
        "source": "NIH / AMA",
        "en": "Inclusive identity questions can help identify differences in access, experiences of care, and health outcomes across communities.",
        "es": "Las preguntas inclusivas sobre identidad pueden ayudar a identificar diferencias en acceso, experiencias de atención y resultados de salud entre comunidades.",
    },
    "discrimination": {
        "source": "NIH / AMA",
        "en": "Experiences of discrimination can affect stress, trust in health systems, access to care, and long-term health outcomes.",
        "es": "Las experiencias de discriminación pueden afectar el estrés, la confianza en los sistemas de salud, el acceso a la atención y los resultados de salud a largo plazo.",
    },
    "neighborhood": {
        "source": "NIH / AMA",
        "en": "Neighborhood safety and resources can influence physical activity, stress, injury risk, and access to daily necessities.",
        "es": "La seguridad y los recursos del vecindario pueden influir en la actividad física, el estrés, el riesgo de lesiones y el acceso a necesidades diarias.",
    },
    "civic_engagement": {
        "source": "NIH / AMA",
        "en": "Civic and community participation can reflect social connection, access to local resources, and ability to influence conditions that affect health.",
        "es": "La participación cívica y comunitaria puede reflejar conexión social, acceso a recursos locales y capacidad de influir en condiciones que afectan la salud.",
    },
    "environment": {
        "source": "NIH / AMA",
        "en": "Environmental conditions such as air, water, pollution, and safe outdoor spaces can affect respiratory health, chronic disease, and daily well-being.",
        "es": "Las condiciones ambientales como aire, agua, contaminación y espacios exteriores seguros pueden afectar la salud respiratoria, enfermedades crónicas y bienestar diario.",
    },
    "community_resilience": {
        "source": "NIH / AMA",
        "en": "Emergency preparedness and community resources affect whether people can stay safe, get information, and recover after disasters.",
        "es": "La preparación para emergencias y los recursos comunitarios afectan si las personas pueden mantenerse seguras, obtener información y recuperarse después de desastres.",
    },
    "tobacco": {
        "source": "NIH / AMA",
        "en": "Tobacco use is a major health risk and is also shaped by stress, environment, access to cessation support, and community conditions.",
        "es": "El consumo de tabaco es un riesgo importante para la salud y también está influido por el estrés, el entorno, el acceso a apoyo para dejarlo y las condiciones comunitarias.",
    },
    "alcohol": {
        "source": "NIH / AMA",
        "en": "Alcohol use can affect physical and mental health, safety, medications, and chronic disease management.",
        "es": "El consumo de alcohol puede afectar la salud física y mental, la seguridad, los medicamentos y el manejo de enfermedades crónicas.",
    },
    "digital_access": {
        "source": "NIH / AMA",
        "en": "Digital access affects the ability to use patient portals, telehealth, online health information, and electronic communication with care teams.",
        "es": "El acceso digital afecta la capacidad de usar portales del paciente, telesalud, información de salud en línea y comunicación electrónica con equipos de atención.",
    },
}


SECTION_EXPLANATION_KEYS = {
    "Access to Health Services": "healthcare_access",
    "Housing": "housing_instability",
    "Address": "location_context",
    "Birthplace": "demographics",
    "Age": "demographics",
    "Marital Status": "demographics",
    "Education": "education",
    "English Proficiency": "language_access",
    "Ethnicity & Race": "race_ethnicity",
    "Health Insurance": "insurance",
    "Health Literacy": "health_literacy",
    "General Health": "general_health",
    "Sexual Orientation": "identity",
    "Discrimination (Major)": "discrimination",
    "Discrimination (Everyday)": "discrimination",
    "Neighborhood": "neighborhood",
    "Food Insecurity": "food_insecurity",
    "Transportation": "transportation_access",
    "Income": "employment_income",
    "Employment": "employment_income",
    "Financial Strain": "employment_income",
    "Work & Labor": "employment_income",
    "Social Support": "social_support",
    "Civic Engagement": "civic_engagement",
    "Environment": "environment",
    "Community Resilience": "community_resilience",
    "Tobacco Use": "tobacco",
    "Alcohol Use": "alcohol",
    "Digital Access": "digital_access",
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
