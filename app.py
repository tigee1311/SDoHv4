# app.py
import datetime
import json
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# =========================
# App Config & Theme
# =========================
st.set_page_config(
    page_title="SDoH Survey (Bilingual)",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Subtle global style
st.markdown(
    """
    <style>
      .block-container {max-width: 980px;}
      h1, h2, h3 { font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; }
      .sdoh-title { text-align:center; font-size: 30px; margin: 0 0 10px 0;}
      .sdoh-subtitle { text-align:center; color:#444; margin: 0 0 18px 0; }
      .sdoh-langwrap { display:flex; justify-content:center; gap:12px; margin-bottom:8px; }
      .sdoh-card { background: #fff; border-radius: 18px; padding: 16px 20px; box-shadow: 0 4px 18px rgba(0,0,0,0.09); }
      .sdoh-section-title { font-size: 24px; margin: 0; }
      .sdoh-submit { margin-top: 10px; }
      .sdoh-pill {
          display:inline-block; padding:10px 18px; border-radius:999px;
          border:1px solid #d2d7df; cursor:pointer; font-weight:600;
          background:#f7f9fc; color:#1e4fb8;
      }
      .sdoh-pill.active {
          background:#e7f0ff; border-color:#b7cef2;
      }
      .sdoh-caption { color:#5f6b7a; font-size: 13px; }
      .sdoh-divider { height: 1px; background: #eceff4; margin: 8px 0 16px 0; }
      /* Make Streamlit radios start unselected spacing nicer */
      div[role="radiogroup"] label { padding: 2px 0; }
      /* Make expander labels boldish */
      .streamlit-expanderHeader p { font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# Google Sheets Connectors
# =========================
@st.cache_resource(show_spinner=False)
def get_worksheet():
    """Authorize gspread with service-account secrets and return the worksheet."""
    creds_info = st.secrets["gcp_service_account"]
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
    client = gspread.authorize(creds)

    sheet_key = st.secrets["gsheet"]["sheet_key"]
    worksheet_name = st.secrets["gsheet"].get("worksheet", "responses")

    sh = client.open_by_key(sheet_key)
    try:
        ws = sh.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=worksheet_name, rows="1000", cols="200")
    return ws

def ensure_headers(ws, headers: List[str]):
    """Ensure header row exists and matches expected headers (add missing)."""
    try:
        current = ws.row_values(1)
    except Exception:
        current = []

    if not current:
        # First time: write all headers
        ws.update([headers], "A1")
        return

    # Add missing headers to end if needed
    if headers != current:
        merged = current[:]
        for h in headers:
            if h not in merged:
                merged.append(h)
        ws.resize(rows=ws.row_count, cols=len(merged))
        ws.update([merged], "A1")

def append_flat_record(ws, record: Dict[str, Any], headers: List[str]):
    """Append a single row dict that may not contain all headers."""
    row = []
    for h in headers:
        row.append(record.get(h, ""))
    ws.append_row(row, value_input_option="USER_ENTERED")

# =========================
# Localization & Options
# =========================
def L(en: str, es: str) -> Dict[str, str]:
    return {"en": en, "es": es}

SECTIONS = [
    ("Access to Health Services", L("Access to Health Services", "Acceso a servicios de salud")),
    ("Income", L("Income", "Ingresos")),
    ("Birthplace", L("Birthplace", "Lugar de nacimiento")),
    ("Address", L("Current Address (optional)", "Dirección actual (opcional)")),
    ("Age", L("Age", "Edad")),
    ("Employment", L("Employment", "Empleo")),
    ("Marital Status", L("Marital Status", "Estado civil")),
    ("Education", L("Education", "Educación")),
    ("English Proficiency", L("English Proficiency", "Dominio del inglés")),
    ("Ethnicity & Race", L("Ethnicity & Race", "Origen étnico y raza")),
    ("Food Insecurity", L("Food Insecurity", "Inseguridad alimentaria")),
    ("Health Insurance", L("Health Insurance Coverage", "Cobertura de seguro de salud")),
    ("Health Literacy", L("Health Literacy", "Conocimientos de salud")),
    ("General Health", L("General Health", "Salud general")),
    ("Sexual Orientation", L("Sexual Orientation", "Orientación sexual")),
    ("Discrimination (Major)", L("Discrimination (Major)", "Discriminación (Mayor)")),
    ("Discrimination (Everyday)", L("Discrimination (Everyday)", "Discriminación (Cotidiana)")),
    ("Neighborhood", L("Neighborhood", "Vecindario")),
    ("Housing", L("Housing", "Vivienda")),
    ("Transportation", L("Transportation", "Transporte")),
    ("Financial Strain", L("Financial Strain", "Dificultad financiera")),
    ("Social Support", L("Social Support", "Apoyo social")),
    ("Civic Engagement", L("Civic Engagement", "Participación cívica")),
    ("Work & Labor", L("Work & Labor", "Trabajo y beneficios")),
    ("Environment", L("Environment", "Medio ambiente")),
    ("Community Resilience", L("Community Resilience", "Resiliencia comunitaria")),
    ("Tobacco Use", L("Tobacco Use", "Uso de tabaco")),
    ("Alcohol Use", L("Alcohol Use", "Uso de alcohol")),
    ("Digital Access", L("Digital Access", "Acceso digital")),
]

# Option helpers
def opt(en, es, code=None):
    return {"en": en, "es": es, "code": code}

YN = [opt("Yes", "Sí", 1), opt("No", "No", 2)]
YN_DK = [
    opt("Yes", "Sí", 1),
    opt("No", "No", 2),
    opt("Don't know", "No sabe", 9),
    opt("Prefer not to answer", "Prefiere no responder", 7),
]
FREQ5 = [
    opt("Always", "Siempre", 1),
    opt("Often", "A menudo", 2),
    opt("Sometimes", "A veces", 3),
    opt("Rarely", "Rara vez", 4),
    opt("Never", "Nunca", 5),
]
HL_CONF = [
    opt("Extremely", "Extremadamente", 1),
    opt("Quite a bit", "Bastante", 2),
    opt("Somewhat", "Algo", 3),
    opt("A little bit", "Un poco", 4),
    opt("Not at all", "Nada", 5),
]
GEN_HEALTH = [
    opt("Excellent", "Excelente", 1),
    opt("Very good", "Muy buena", 2),
    opt("Good", "Buena", 3),
    opt("Fair", "Regular", 4),
    opt("Poor", "Mala", 5),
]
ENG = [
    opt("Very well", "Muy bien", 1),
    opt("Well", "Bien", 2),
    opt("Not well", "No muy bien", 3),
    opt("Not at all", "Nada", 4),
]
INCOME = [
    opt("< $10,000", "< $10,000", 1),
    opt("$10,000–$24,999", "$10,000–$24,999", 2),
    opt("$25,000–$34,999", "$25,000–$34,999", 3),
    opt("$35,000–$49,999", "$35,000–$49,999", 4),
    opt("$50,000–$74,999", "$50,000–$74,999", 5),
    opt("$75,000–$99,999", "$75,000–$99,999", 6),
    opt("$100,000–$149,999", "$100,000–$149,999", 7),
    opt("$150,000–$199,999", "$150,000–$199,999", 8),
    opt("$200,000 or more", "$200,000 o más", 9),
    opt("Prefer not to answer", "Prefiere no responder", 10),
]
EDU = [
    opt("Less than high school", "Menos que secundaria", 1),
    opt("High school or GED", "Secundaria o GED", 2),
    opt("Some college, no degree", "Algo de universidad, sin título", 3),
    opt("Associate degree", "Técnico/Asociado", 4),
    opt("Bachelor’s degree", "Licenciatura", 5),
    opt("Master’s degree", "Maestría", 6),
    opt("Professional/Doctoral degree", "Profesional/Doctorado", 7),
]
EMP = [
    opt("Working now", "Trabajando actualmente", 1),
    opt("Temporary leave", "Permiso temporal", 2),
    opt("Looking for work / Unemployed", "Buscando trabajo / Desempleado(a)", 3),
    opt("Retired", "Jubilado(a)", 4),
    opt("Disabled", "Con discapacidad", 5),
    opt("Keeping house", "Labores del hogar", 6),
    opt("Student", "Estudiante", 7),
    opt("Other", "Otro", 8),
]
MAR = [
    opt("Married", "Casado(a)", 1),
    opt("Divorced", "Divorciado(a)", 2),
    opt("Widowed", "Viudo(a)", 3),
    opt("Separated", "Separado(a)", 4),
    opt("Never married", "Nunca casado(a)", 5),
    opt("Member of an unmarried couple", "Pareja no casada", 6),
]
SO1 = [
    opt("Gay", "Gay", 1),
    opt("Lesbian", "Lesbiana", 2),
    opt("Straight (not gay/lesbian)", "Heterosexual (no gay/lesbiana)", 3),
    opt("Bisexual", "Bisexual", 4),
    opt("None of these — show more options", "Ninguna de estas — ver más opciones", 5),
]
SO2 = [
    opt("Queer", "Queer", 1),
    opt("Poly/omni/sapio/pansexual", "Poli/omni/sapio/pansexual", 2),
    opt("Asexual", "Asexual", 3),
    opt("Two-spirit", "Dos espíritus", 4),
    opt("Figuring it out", "En proceso de definir", 5),
    opt("Mostly straight", "Mayormente heterosexual", 6),
    opt("No sexuality", "No se considera con sexualidad", 7),
    opt("No labels", "No usa etiquetas", 8),
    opt("Don't know", "No sabe", 9),
    opt("Something else (specify)", "Otra cosa (especifique)", 10),
    opt("Prefer not to answer", "Prefiere no responder", 11),
]
FS_OSN = [
    opt("Often true", "A menudo cierto", 1),
    opt("Sometimes true", "A veces cierto", 2),
    opt("Never true", "Nunca cierto", 3),
]
FS_YN = [opt("Yes", "Sí", 1), opt("No", "No", 2)]
FS_3A = [
    opt("Almost every month", "Casi todos los meses", 1),
    opt("Some months but not every month", "Algunos meses pero no todos", 2),
    opt("Only 1 or 2 months", "Solo 1 o 2 meses", 3),
]
AGREE5 = [
    opt("Strongly agree", "Totalmente de acuerdo", 1),
    opt("Agree", "De acuerdo", 2),
    opt("Neutral", "Neutral", 3),
    opt("Disagree", "En desacuerdo", 4),
    opt("Strongly disagree", "Totalmente en desacuerdo", 5),
]

# =========================
# Question Registry
# =========================
# Each question: {id, section, text:{en,es}, type in {"radio","int","text"}, options, branch callable}
QUESTIONS: List[Dict[str, Any]] = []

def add_q(section, _id, en, es, qtype, options=None, branch=None):
    QUESTIONS.append({
        "id": _id,
        "section": section,
        "text": {"en": en, "es": es},
        "type": qtype,
        "options": options or [],
        "branch": branch,
    })

# --- Access to Health Services (10) ---
add_q("Access to Health Services", "q1_last_visit_any",
      "How long has it been since you last saw a doctor or other health professional about your health?",
      "¿Cuánto tiempo ha pasado desde la última vez que vio a un médico u otro profesional de la salud por su salud?",
      "radio",
      options=[
          opt("Within the past year (<12 months)", "Dentro del último año (<12 meses)", 1),
          opt("Within the last 2 years", "En los últimos 2 años", 2),
          opt("Within the last 3 years", "En los últimos 3 años", 3),
          opt("Within the last 5 years", "En los últimos 5 años", 4),
          opt("Within the last 10 years", "En los últimos 10 años", 5),
          opt("10 years ago or more", "Hace 10 años o más", 6),
          opt("Never", "Nunca", 0),
          opt("Prefer not to answer", "Prefiere no responder", 7),
          opt("Don't know", "No sabe", 9),
      ])
add_q("Access to Health Services", "q2_last_visit_wellness",
      "Was that visit a wellness/physical/general check-up?",
      "¿Esa visita fue un examen de bienestar/físico/revisión general?",
      "radio",
      options=YN_DK,
      branch=lambda a: a.get("q1_last_visit_any", {}).get("code") in (1,2,3,4,5,6))
add_q("Access to Health Services", "q3_last_wellness",
      "How long has it been since your last wellness/physical/general check-up?",
      "¿Cuánto tiempo ha pasado desde su último examen de bienestar/físico/revisión general?",
      "radio",
      options=[
          opt("Within the past year", "Dentro del último año", 1),
          opt("Within the last 2 years", "En los últimos 2 años", 2),
          opt("Within the last 3 years", "En los últimos 3 años", 3),
          opt("Within the last 5 years", "En los últimos 5 años", 4),
          opt("More than 5 years", "Más de 5 años", 5),
          opt("Prefer not to answer", "Prefiere no responder", 7),
          opt("Don't know", "No sabe", 9),
      ],
      branch=lambda a: a.get("q1_last_visit_any", {}).get("code") in (1,2,3,4,5,6)
                      and a.get("q2_last_visit_wellness", {}).get("code") not in (None, 1))
add_q("Access to Health Services", "q4_usual_source",
      "Is there a place you USUALLY go if you're sick and need care?",
      "¿Tiene un lugar al que USUALMENTE va cuando está enfermo y necesita atención?",
      "radio",
      options=[
          opt("Yes", "Sí", 1),
          opt("There is NO place", "NO hay lugar", 2),
          opt("There is MORE THAN ONE place", "Hay MÁS DE UN lugar", 3),
          opt("Prefer not to answer", "Prefiere no responder", 7),
          opt("Don't know", "No sabe", 9),
      ])
add_q("Access to Health Services", "q5_usual_place_type",
      "What kind of place is it/do you go to most often?",
      "¿Qué tipo de lugar es o al que va con más frecuencia?",
      "radio",
      options=[
          opt("Doctor's office / health center", "Consultorio / centro de salud", 1),
          opt("Walk-in / urgent care / retail clinic", "Clínica sin cita / urgencias / minorista", 2),
          opt("Emergency room", "Sala de emergencias", 3),
          opt("VA Medical Center / VA clinic", "Centro médico/Clínica de VA", 4),
          opt("Some other place", "Otro lugar", 5),
          opt("Does not go to one place most often", "No va a un solo lugar con más frecuencia", 6),
          opt("Prefer not to answer", "Prefiere no responder", 7),
          opt("Don't know", "No sabe", 9),
      ],
      branch=lambda a: a.get("q4_usual_source", {}).get("code") in (1, 3))
add_q("Access to Health Services", "q6_urgent_care_visits",
      "In the past 12 months, how many times did you go to urgent care or a retail clinic? (0–96; 96 = 96+)",
      "En los últimos 12 meses, ¿cuántas veces fue a urgencias o a una clínica minorista? (0–96; 96 = 96+)",
      "int")
add_q("Access to Health Services", "q7_er_visits",
      "In the past 12 months, how many times did you go to a hospital emergency room? (0–96; 96 = 96+)",
      "En los últimos 12 meses, ¿cuántas veces fue a la sala de emergencias de un hospital? (0–96; 96 = 96+)",
      "int")
add_q("Access to Health Services", "q8_hospitalized_overnight",
      "In the past 12 months, were you hospitalized overnight?",
      "En los últimos 12 meses, ¿estuvo hospitalizado durante la noche?",
      "radio", options=YN_DK)
add_q("Access to Health Services", "q9_delayed_care_cost",
      "In the past 12 months, did you DELAY medical care because of cost?",
      "En los últimos 12 meses, ¿RETRASÓ la atención médica por el costo?",
      "radio", options=YN_DK)
add_q("Access to Health Services", "q10_unmet_need_cost",
      "In the past 12 months, was there a time you NEEDED care but DID NOT GET IT because of cost?",
      "En los últimos 12 meses, ¿hubo alguna vez que NECESITÓ atención pero NO LA RECIBIÓ por el costo?",
      "radio", options=YN_DK)

# --- Income / Birthplace / Address / Age (12) ---
add_q("Income", "income_bracket",
      "What is your annual household income from all sources?",
      "¿Cuál es el ingreso anual total de su hogar (todas las fuentes)?",
      "radio", options=INCOME)
add_q("Income", "num_supported",
      "How many people (including you) were supported by that income?",
      "¿Cuántas personas (incluyéndose) se mantuvieron con ese ingreso?",
      "int")
add_q("Birthplace", "bp_where",
      "Where were you born?",
      "¿Dónde nació?",
      "radio", options=[opt("In the United States", "En los Estados Unidos", 1), opt("Outside the United States", "Fuera de los Estados Unidos", 2)])
add_q("Birthplace", "bp_state",
      "If in the U.S., which state?",
      "Si fue en EE. UU., ¿en qué estado?",
      "text", branch=lambda a: a.get("bp_where", {}).get("code") == 1)
add_q("Birthplace", "bp_country",
      "If outside the U.S., which territory or country?",
      "Si fue fuera de EE. UU., ¿qué territorio o país?",
      "text", branch=lambda a: a.get("bp_where", {}).get("code") == 2)

add_q("Address", "addr_street",
      "Street address (number and street) [optional]",
      "Dirección (número y calle) [opcional]",
      "text")
add_q("Address", "addr_city", "City", "Ciudad", "text")
add_q("Address", "addr_state", "State/Province", "Estado/Provincia", "text")
add_q("Address", "addr_zip", "ZIP/Postal code", "Código postal", "text")

add_q("Age", "dob_mm", "Birth month (MM)", "Mes de nacimiento (MM)", "text")
add_q("Age", "dob_dd", "Birth day (DD)", "Día de nacimiento (DD)", "text")
add_q("Age", "dob_yy", "Birth year (YYYY)", "Año de nacimiento (AAAA)", "text")
add_q("Age", "age_years", "Age (in years)", "Edad (en años)", "int")

# --- Employment / Marital / Education / English (5) ---
add_q("Employment", "emp_status", "Current employment status", "Situación laboral actual", "radio", options=EMP)
add_q("Employment", "emp_other", "If 'Other', please specify", "Si seleccionó 'Otro', especifique", "text",
      branch=lambda a: a.get("emp_status", {}).get("code") == 8)
add_q("Marital Status", "marital", "Marital status", "Estado civil", "radio", options=MAR)
add_q("Education", "education", "Highest level of education completed", "Máximo nivel educativo completado", "radio", options=EDU)
add_q("English Proficiency", "english_proficiency", "How well do you speak English?", "¿Qué tan bien habla inglés?", "radio", options=ENG)

# --- Ethnicity & Race (~20) ---
add_q("Ethnicity & Race", "hispanic_origin",
      "Are you of Hispanic/Latino/Spanish origin?", "¿Es de origen hispano/latino/español?",
      "radio",
      options=[
          opt("No, not of Hispanic/Latino/Spanish origin", "No, no de origen hispano/latino/español", 1),
          opt("Yes, Mexican/Mexican Am./Chicano", "Sí, mexicano/mexicoamericano/chicano", 2),
          opt("Yes, Puerto Rican", "Sí, puertorriqueño", 3),
          opt("Yes, Cuban", "Sí, cubano", 4),
          opt("Yes, another Hispanic/Latino/Spanish origin (specify)", "Sí, otro origen hispano/latino/español (especifique)", 5),
      ])
add_q("Ethnicity & Race", "hispanic_origin_detail",
      "Please specify your Hispanic/Latino/Spanish origin", "Especifique su origen hispano/latino/español",
      "text", branch=lambda a: a.get("hispanic_origin", {}).get("code") == 5)

RACE_ITEMS = [
    ("race_white", "White (specify origins if you wish)", "Blanco (especifique orígenes si desea)"),
    ("race_black", "Black or African American (specify origins if you wish)", "Negro o afroamericano (especifique orígenes si desea)"),
    ("race_aian", "American Indian or Alaska Native (specify tribe)", "Indígena americano o nativo de Alaska (especifique tribu)"),
    ("race_chinese", "Chinese", "Chino"),
    ("race_filipino", "Filipino", "Filipino"),
    ("race_asianind", "Asian Indian", "Indio asiático"),
    ("race_viet", "Vietnamese", "Vietnamita"),
    ("race_korean", "Korean", "Coreano"),
    ("race_japanese", "Japanese", "Japonés"),
    ("race_other_asian", "Other Asian (specify)", "Otro asiático (especifique)"),
    ("race_nh", "Native Hawaiian", "Nativo hawaiano"),
    ("race_samoan", "Samoano", "Samoano"),
    ("race_chamorro", "Chamorro", "Chamorro"),
    ("race_other_pi", "Other Pacific Islander (specify)", "Otro isleño del Pacífico (especifique)"),
    ("race_other", "Some other race (specify)", "Otra raza (especifique)"),
]
for rid, en, es in RACE_ITEMS:
    add_q("Ethnicity & Race", rid, f"Race — {en}", f"Raza — {es}", "radio",
          options=[opt("Select", "Seleccionar", 1), opt("Skip", "Omitir", 0)])
    if "specify" in en.lower() or "tribe" in en.lower():
        add_q("Ethnicity & Race", rid + "_detail",
              "Please specify", "Especifique", "text",
              branch=lambda a, key=rid: a.get(key, {}).get("code") == 1)

# --- Food Insecurity (6 + follow-up) ---
add_q("Food Insecurity", "fs1",
      "“The food we bought just didn’t last, and we didn’t have money to get more.”",
      "“La comida que compramos no alcanzó, y no teníamos dinero para comprar más.”",
      "radio", options=FS_OSN)
add_q("Food Insecurity", "fs2",
      "“We couldn’t afford to eat balanced meals.”",
      "“No podíamos permitirnos comer comidas balanceadas.”",
      "radio", options=FS_OSN)
add_q("Food Insecurity", "fs3",
      "In the past 12 months, did you cut meal size or skip meals due to lack of money?",
      "En los últimos 12 meses, ¿recortó el tamaño de las comidas o se saltó comidas por falta de dinero?",
      "radio", options=FS_YN)
add_q("Food Insecurity", "fs3a",
      "If yes, how often?", "Si respondió sí, ¿con qué frecuencia?",
      "radio", options=FS_3A, branch=lambda a: a.get("fs3", {}).get("code") == 1)
add_q("Food Insecurity", "fs4",
      "In the past 12 months, did you eat less than you felt you should due to lack of money?",
      "En los últimos 12 meses, ¿comió menos de lo que debía por falta de dinero?",
      "radio", options=FS_YN)
add_q("Food Insecurity", "fs5",
      "In the past 12 months, were you ever hungry but didn’t eat because there wasn’t enough money for food?",
      "En los últimos 12 meses, ¿tuvo hambre pero no comió por falta de dinero?",
      "radio", options=FS_YN)

# --- Health Insurance (~7 + detail) ---
INS_ITEMS = [
    ("ins_employer", "Employer/union plan (yours/family; includes COBRA)", "Plan de empleador/sindicato (suyo/familia; incluye COBRA)"),
    ("ins_direct", "Direct purchase / Marketplace or exchange", "Compra directa / Mercado o intercambio"),
    ("ins_medicare", "Medicare", "Medicare"),
    ("ins_medicaid", "Medicaid / Medical Assistance / CHIP", "Medicaid / Asistencia médica / CHIP"),
    ("ins_tricare", "TRICARE / VA", "TRICARE / VA"),
    ("ins_ihs", "Indian Health Service", "Servicio de Salud Indígena"),
    ("ins_other", "Other health coverage", "Otro tipo de cobertura de salud"),
]
for iid, en, es in INS_ITEMS:
    add_q("Health Insurance", iid, en, es, "radio",
          options=[opt("Covered", "Con cobertura", 1),
                   opt("Not covered", "Sin cobertura", 2),
                   opt("Not sure", "No seguro(a)", 3)])
add_q("Health Insurance", "ins_other_detail",
      "If 'Other' is covered, what type?",
      "Si 'Otro' tiene cobertura, ¿qué tipo?",
      "text",
      branch=lambda a: a.get("ins_other", {}).get("code") == 1)

# --- Health Literacy (3) ---
add_q("Health Literacy", "hl_conf",
      "How confident are you filling out medical forms by yourself?",
      "¿Qué tan seguro(a) se siente al llenar formularios médicos por su cuenta?",
      "radio", options=HL_CONF)
add_q("Health Literacy", "hl_help_read",
      "How often do you have someone help you read health materials?",
      "¿Con qué frecuencia alguien le ayuda a leer materiales de salud?",
      "radio", options=FREQ5)
add_q("Health Literacy", "hl_learn_prob",
      "How often do you have problems learning about your medical condition due to written information?",
      "¿Con qué frecuencia tiene problemas para aprender sobre su condición por la información escrita?",
      "radio", options=FREQ5)

# --- General Health & Sexual Orientation (4) ---
add_q("General Health", "gen_health",
      "Overall, how would you rate your health?",
      "En general, ¿cómo califica su salud?",
      "radio", options=GEN_HEALTH)
add_q("Sexual Orientation", "so1",
      "Which best represents how you think of yourself?",
      "¿Cuál lo(a) representa mejor?",
      "radio", options=SO1)
add_q("Sexual Orientation", "so2",
      "Additional options (if selected)",
      "Opciones adicionales (si seleccionó)",
      "radio", options=SO2, branch=lambda a: a.get("so1", {}).get("code") == 5)
add_q("Sexual Orientation", "so2_detail",
      "Please describe", "Describa", "text",
      branch=lambda a: a.get("so2", {}).get("code") == 10)

# --- Discrimination (Major) (9) ---
MAJ = [
    ("disc_fired", "Unfairly fired from a job?", "¿Despedido injustamente de un trabajo?"),
    ("disc_not_hired", "Not hired for a job for unfair reasons?", "¿No contratado por razones injustas?"),
    ("disc_denied_promo", "Denied a promotion?", "¿Negada una promoción?"),
    ("disc_police", "Stopped/searched/threatened/abused by police?", "¿Detenido/registrado/amenazado/abusado por la policía?"),
    ("disc_housing_blocked", "Prevented from moving into a neighborhood?", "¿Impedido de mudarse a un vecindario?"),
    ("disc_neighbors_hostile", "Neighbors made life difficult after moving in?", "¿Vecinos le hicieron la vida difícil tras mudarse?"),
    ("disc_bank_loan", "Denied a bank loan?", "¿Negado un préstamo bancario?"),
    ("disc_school_discouraged", "Discouraged from continuing education?", "¿Disuadido de continuar su educación?"),
    ("disc_healthcare", "Denied/poorer healthcare than others?", "¿Atención médica negada o de peor calidad que otros?"),
]
for k, en, es in MAJ:
    add_q("Discrimination (Major)", k, en, es, "radio", options=YN)

# --- Discrimination (Everyday) (9) ---
EDS = [
    ("eds_courtesy", "Treated with less courtesy than other people", "Trato con menos cortesía que otras personas"),
    ("eds_respect", "Treated with less respect than other people", "Trato con menos respeto que otras personas"),
    ("eds_service", "Received poorer service at restaurants or stores", "Servicio peor en restaurantes o tiendas"),
    ("eds_not_smart", "People act as if you are not smart", "La gente actúa como si no fuera inteligente"),
    ("eds_afraid", "People act as if they are afraid of you", "La gente actúa como si le tuviera miedo"),
    ("eds_dishonest", "People act as if you are dishonest", "La gente actúa como si fuera deshonesto"),
    ("eds_not_as_good", "People act as if you are not as good as they are", "La gente actúa como si no fuera tan bueno como ellos"),
    ("eds_insulted", "You are called names or insulted", "Le ponen apodos o insultan"),
    ("eds_threatened", "You are threatened or harassed", "Le amenazan o acosan"),
]
for k, en, es in EDS:
    add_q("Discrimination (Everyday)", k, en, es, "radio",
          options=[
              opt("Almost every day", "Casi todos los días", 1),
              opt("At least once a week", "Al menos una vez por semana", 2),
              opt("A few times a month", "Unas cuantas veces al mes", 3),
              opt("A few times a year", "Unas cuantas veces al año", 4),
              opt("Less than once a year", "Menos de una vez al año", 5),
              opt("Never", "Nunca", 6),
          ])

# --- Neighborhood (7) ---
NBH = [
    ("nbh_safe_walk", "I feel safe walking in my neighborhood, day or night.", "Me siento seguro caminando en mi vecindario, de día o de noche."),
    ("nbh_violence", "Violence is not a problem in my neighborhood.", "La violencia no es un problema en mi vecindario."),
    ("nbh_safe_crime", "My neighborhood is safe from crime.", "Mi vecindario está a salvo del crimen."),
    ("nbh_active", "I see people being active (walking, biking) in my neighborhood.", "Veo gente activa (caminando, en bici) en mi vecindario."),
    ("nbh_sidewalks", "There are sidewalks on most streets.", "Hay aceras en la mayoría de las calles."),
    ("nbh_stores", "There are stores within walking distance.", "Hay tiendas a distancia a pie."),
    ("nbh_parks", "There are parks or open spaces nearby.", "Hay parques o espacios abiertos cerca."),
]
for k, en, es in NBH:
    add_q("Neighborhood", k, en, es, "radio", options=AGREE5)

# --- Housing (5) ---
add_q("Housing", "house_bills",
      "In the last 12 months, were you unable to pay mortgage/rent or utilities on time?",
      "En los últimos 12 meses, ¿no pudo pagar a tiempo la hipoteca/renta o los servicios?",
      "radio", options=YN)
add_q("Housing", "house_moves",
      "How many times did you move in the past 12 months?",
      "¿Cuántas veces se mudó en los últimos 12 meses?",
      "int")
add_q("Housing", "house_homeless",
      "In the past 12 months, were you ever homeless (no stable place to live)?",
      "En los últimos 12 meses, ¿estuvo sin hogar (sin lugar estable para vivir)?",
      "radio", options=YN)
add_q("Housing", "house_sleep_place",
      "If homeless, where did you sleep most often (shelter, street, car, doubled up, etc.)?",
      "Si estuvo sin hogar, ¿dónde durmió con más frecuencia (albergue, calle, auto, con conocidos, etc.)?",
      "text", branch=lambda a: a.get("house_homeless", {}).get("code") == 1)
add_q("Housing", "house_forced_move",
      "In the last 12 months, how many times were you forced to move by a landlord, bank, or mortgage company?",
      "En los últimos 12 meses, ¿cuántas veces fue obligado a mudarse por el propietario, banco o hipotecaria?",
      "int")

# --- Transportation (8) ---
TRN = [
    ("trans_barrier", "In the past 12 months, did lack of transportation keep you from appointments/work/essentials?", "En los últimos 12 meses, ¿la falta de transporte le impidió asistir a citas/trabajo/esenciales?"),
    ("trans_car_access", "How often do you have access to a car when needed?", "¿Con qué frecuencia tiene acceso a un auto cuando lo necesita?"),
    ("trans_public_use", "How often do you use public transportation?", "¿Con qué frecuencia usa transporte público?"),
    ("trans_public_reliable", "How reliable is public transportation in your area?", "¿Qué tan confiable es el transporte público en su zona?"),
    ("trans_time_provider", "How much time does it usually take to reach your healthcare provider?", "¿Cuánto tiempo suele tardar en llegar a su proveedor de salud?"),
    ("trans_cost_month", "How much does transportation cost you per month (estimate)?", "¿Cuánto gasta en transporte por mes (estimado)?"),
    ("trans_rely_others", "Do you rely on family/friends for rides?", "¿Depende de familia/amigos para traslados?"),
    ("trans_missed_essentials", "Have you missed meds/food/essentials due to transport barriers?", "¿Ha dejado de obtener medicinas/comida/esenciales por barreras de transporte?"),
]
for k, en, es in TRN:
    if "time" in k or "cost" in k:
        add_q("Transportation", k, en, es, "int")
    else:
        add_q("Transportation", k, en, es, "radio", options=FREQ5 if "How often" in en else YN)

# --- Financial Strain (6) ---
add_q("Financial Strain", "fin_bills_diff",
      "How difficult is it for you to pay monthly bills?",
      "¿Qué tan difícil es pagar sus cuentas mensuales?",
      "radio", options=[opt("Very difficult", "Muy difícil", 1), opt("Somewhat difficult", "Algo difícil", 2), opt("Not difficult", "No es difícil", 3)])
add_q("Financial Strain", "fin_end_month",
      "At the end of the month, how much money do you usually have?",
      "Al final del mes, ¿cuánto dinero suele tener?",
      "radio", options=[opt("More than enough", "Más que suficiente", 1), opt("Just enough", "Justo suficiente", 2), opt("Not enough", "No suficiente", 3)])
add_q("Financial Strain", "fin_utils_shut",
      "In the past 12 months, were any utilities shut off due to nonpayment?",
      "En los últimos 12 meses, ¿algún servicio fue cortado por falta de pago?",
      "radio", options=YN)
add_q("Financial Strain", "fin_emergency_400",
      "Do you have at least $400 available for an emergency?",
      "¿Tiene al menos $400 disponibles para una emergencia?",
      "radio", options=YN)
add_q("Financial Strain", "fin_payday_loans",
      "Have you used payday loans/borrowed to cover living expenses?",
      "¿Usó préstamos de día de pago o pidió prestado para gastos de vida?",
      "radio", options=YN)
add_q("Financial Strain", "fin_help_others",
      "Do you receive help from family/friends/community programs for living expenses?",
      "¿Recibe ayuda de familia/amigos/programas comunitarios para gastos de vida?",
      "radio", options=YN)

# --- Social Support (6) ---
SS = [
    ("ss_listen", "Someone is available to listen when you need to talk.", "Alguien disponible para escuchar cuando necesita hablar."),
    ("ss_advice", "Someone gives good advice when you are in trouble.", "Alguien da buen consejo cuando tiene problemas."),
    ("ss_chores", "Someone helps with chores if you are sick.", "Alguien ayuda con tareas si está enfermo."),
    ("ss_emotional", "Someone provides emotional support.", "Alguien brinda apoyo emocional."),
    ("ss_private", "Someone to share your private worries and fears.", "Alguien con quien compartir preocupaciones privadas."),
    ("ss_love", "Someone to love you and make you feel wanted.", "Alguien que le ama y le hace sentir valorado."),
]
for k, en, es in SS:
    add_q("Social Support", k, en, es, "radio", options=FREQ5)

# --- Civic Engagement (5) ---
add_q("Civic Engagement", "civ_registered", "Are you registered to vote?", "¿Está registrado para votar?", "radio", options=YN)
add_q("Civic Engagement", "civ_voted", "Did you vote in the most recent national election?", "¿Votó en la elección nacional más reciente?", "radio", options=YN)
add_q("Civic Engagement", "civ_volunteer", "How often do you volunteer in your community?", "¿Con qué frecuencia es voluntario en su comunidad?", "radio", options=FREQ5)
add_q("Civic Engagement", "civ_meetings", "How often do you attend neighborhood/community meetings?", "¿Con qué frecuencia asiste a reuniones comunitarias/vecinales?", "radio", options=FREQ5)
add_q("Civic Engagement", "civ_voice", "Do you feel your voice is heard in local decision-making?", "¿Siente que su voz se escucha en la toma de decisiones locales?", "radio",
      options=[opt("Yes", "Sí", 1), opt("Sometimes", "A veces", 2), opt("No", "No", 3)])

# --- Work & Labor (5) ---
add_q("Work & Labor", "work_sick_leave", "Does your job provide paid sick leave?", "¿Su trabajo ofrece licencia por enfermedad pagada?", "radio", options=YN)
add_q("Work & Labor", "work_insurance", "Does your job provide health insurance?", "¿Su trabajo ofrece seguro de salud?", "radio", options=YN)
add_q("Work & Labor", "work_retirement", "Does your job provide retirement/pension benefits?", "¿Su trabajo ofrece beneficios de jubilación/pensión?", "radio", options=YN)
add_q("Work & Labor", "work_min_wage", "Does your job pay at least local minimum wage?", "¿Su trabajo paga al menos el salario mínimo local?", "radio", options=YN)
add_q("Work & Labor", "work_union", "Are you a member of a union/worker organization?", "¿Es miembro de un sindicato/organización laboral?", "radio", options=YN)

# --- Environment (5) ---
add_q("Environment", "env_air_quality", "Is the air quality in your neighborhood generally good, fair, or poor?", "¿La calidad del aire en su vecindario es buena, regular o mala?", "radio",
      options=[opt("Good", "Buena", 1), opt("Fair", "Regular", 2), opt("Poor", "Mala", 3)])
add_q("Environment", "env_exposure_health", "Any health problems you think related to environmental exposures (pollution/lead/pesticides)?", "¿Problemas de salud que crea relacionados con exposiciones ambientales (contaminación/plomo/plaguicidas)?", "radio", options=YN)
add_q("Environment", "env_trash", "How often do you see trash/litter/illegal dumping in your neighborhood?", "¿Con qué frecuencia ve basura/tiraderos ilegales en su vecindario?", "radio", options=FREQ5)
add_q("Environment", "env_outdoor_spaces", "Do you have access to safe outdoor spaces for exercise and recreation?", "¿Tiene acceso a espacios exteriores seguros para ejercicio y recreación?", "radio", options=YN)
add_q("Environment", "env_safe_water", "Do you have access to clean, safe tap water in your home?", "¿Tiene acceso a agua potable segura en su casa?", "radio", options=YN)

# --- Community Resilience (5) ---
add_q("Community Resilience", "res_safe_place_disaster", "In a disaster (flood/fire/earthquake), do you have a safe place to go?", "En un desastre (inundación/incendio/terremoto), ¿tiene un lugar seguro a dónde ir?", "radio", options=YN)
add_q("Community Resilience", "res_comm_resources", "Does your community have emergency preparedness resources?", "¿Su comunidad tiene recursos de preparación para emergencias?", "radio", options=YN)
add_q("Community Resilience", "res_info_access", "Do you know how to access emergency information in your area?", "¿Sabe cómo acceder a la información de emergencias en su zona?", "radio", options=YN)
add_q("Community Resilience", "res_neighbors_help", "Do you have neighbors/community you can rely on in an emergency?", "¿Tiene vecinos/comunidad en quienes confiar en una emergencia?", "radio", options=YN)
add_q("Community Resilience", "res_recover_quick", "Do you feel your community could recover quickly after a disaster?", "¿Cree que su comunidad podría recuperarse rápidamente tras un desastre?", "radio",
      options=[opt("Yes", "Sí", 1), opt("Maybe", "Quizá", 2), opt("No", "No", 3)])

# --- Tobacco Use (5 + follow-ups) ---
add_q("Tobacco Use", "tob_now_smoke", "Do you now smoke cigarettes?", "¿Actualmente fuma cigarrillos?", "radio",
      options=[opt("Every day", "Todos los días", 1), opt("Some days", "Algunos días", 2), opt("Not at all", "Nada", 3)])
add_q("Tobacco Use", "tob_100_cigs", "Have you smoked at least 100 cigarettes in your life?", "¿Ha fumado al menos 100 cigarrillos en su vida?", "radio", options=YN,
      branch=lambda a: a.get("tob_now_smoke", {}).get("code") in (1, 2))
add_q("Tobacco Use", "tob_age_start", "At what age did you start smoking regularly?", "¿A qué edad comenzó a fumar regularmente?", "int",
      branch=lambda a: a.get("tob_now_smoke", {}).get("code") in (1, 2))
add_q("Tobacco Use", "tob_quit_attempt", "In the past 12 months, have you tried to quit?", "En los últimos 12 meses, ¿intentó dejar de fumar?", "radio", options=YN,
      branch=lambda a: a.get("tob_now_smoke", {}).get("code") in (1, 2))
add_q("Tobacco Use", "tob_other_forms", "Do you now use other tobacco (cigars/pipes/smokeless/e-cigarettes)?", "¿Usa ahora otros productos de tabaco (puros/pipas/tabaco sin humo/cigarrillos electrónicos)?", "radio", options=YN)

# --- Alcohol Use (9 + branching) ---
add_q("Alcohol Use", "alc_ever", "Have you ever had a drink of any kind of alcoholic beverage?", "¿Alguna vez ha tomado alguna bebida alcohólica?", "radio", options=YN)
add_q("Alcohol Use", "alc_30d_any", "During the past 30 days, did you have at least one drink of alcohol?", "En los últimos 30 días, ¿tomó al menos una bebida alcohólica?", "radio", options=YN,
      branch=lambda a: a.get("alc_ever", {}).get("code") == 1)
add_q("Alcohol Use", "alc_30d_days", "During the past 30 days, on how many days did you drink alcohol?", "En los últimos 30 días, ¿en cuántos días bebió alcohol?", "int",
      branch=lambda a: a.get("alc_30d_any", {}).get("code") == 1)
add_q("Alcohol Use", "alc_30d_usual", "On drinking days, how many drinks did you usually have?", "En días que bebió, ¿cuántas bebidas suele tomar?", "int",
      branch=lambda a: a.get("alc_30d_any", {}).get("code") == 1)
add_q("Alcohol Use", "alc_30d_max", "During the past 30 days, what is the largest number of drinks you had on any occasion?", "En los últimos 30 días, ¿cuál fue el mayor número de bebidas en una ocasión?", "int",
      branch=lambda a: a.get("alc_30d_any", {}).get("code") == 1)
add_q("Alcohol Use", "alc_binge_year", "In the past year, how often did you have 5 (men)/4 (women) or more drinks on one occasion?", "En el último año, ¿con qué frecuencia tomó 5 (hombres)/4 (mujeres) o más bebidas en una ocasión?", "radio",
      options=[opt("Never", "Nunca", 0), opt("Less than monthly", "Menos que mensual", 1), opt("Monthly", "Mensual", 2), opt("Weekly", "Semanal", 3), opt("Daily or almost daily", "Diaria o casi diaria", 4)],
      branch=lambda a: a.get("alc_ever", {}).get("code") == 1)
for k, en, es in [
    ("alc_cut", "Have you felt you should cut down on drinking?", "¿Ha sentido que debería reducir su consumo?"),
    ("alc_annoy", "Have people annoyed you by criticizing your drinking?", "¿Le han molestado al criticar su consumo?"),
    ("alc_guilt", "Have you felt bad or guilty about your drinking?", "¿Se ha sentido mal o culpable por su consumo?"),
    ("alc_eyeopener", "Have you had a drink first thing in the morning (eye-opener)?", "¿Ha bebido al despertar (para calmar los nervios)?"),
]:
    add_q("Alcohol Use", k, en, es, "radio", options=YN, branch=lambda a: a.get("alc_ever", {}).get("code") == 1)

# --- Digital Access (5) ---
add_q("Digital Access", "net_home", "Do you have Internet access at home?", "¿Tiene acceso a Internet en casa?", "radio", options=YN)
add_q("Digital Access", "smartphone", "Do you have a smartphone or tablet with Internet?", "¿Tiene un teléfono inteligente o tableta con Internet?", "radio", options=YN)
add_q("Digital Access", "net_health_info", "How often do you look up health information online?", "¿Con qué frecuencia busca información de salud en línea?", "radio", options=FREQ5)
add_q("Digital Access", "net_confidence", "How confident are you finding helpful health resources online?", "¿Qué tan seguro(a) se siente para encontrar recursos de salud útiles en línea?", "radio", options=HL_CONF)
add_q("Digital Access", "portal_comm", "Do you use email/patient portals to communicate with your clinic?", "¿Usa correo o portales del paciente para comunicarse con su clínica?", "radio", options=YN)

# =========================
# Utilities
# =========================
def get_lang() -> str:
    return st.session_state.get("lang", "en")

def t_section(section_key: str) -> str:
    # Map English key to localized label
    for key, lbl in SECTIONS:
        if key == section_key:
            return lbl[get_lang()]
    return section_key

def is_visible(q: Dict[str, Any], answers: Dict[str, Any]) -> bool:
    br = q.get("branch")
    if br is None:
        return True
    try:
        return bool(br(answers))
    except Exception:
        return True

def render_radio(label: str, options: List[Dict[str, Any]], key: str):
    # Radios start unselected (index=None). Uses mouse/touch clicks to select.
    idx = None
    choice_labels = [o[get_lang()] for o in options]
    code_lookup = [o["code"] for o in options]
    sel = st.radio(label, options=choice_labels, index=idx, key=key, horizontal=False)
    # Map back to code
    if st.session_state.get(key) is None:
        return None
    chosen_idx = choice_labels.index(sel) if sel in choice_labels else None
    if chosen_idx is None:
        return None
    return {"code": code_lookup[chosen_idx], "label": sel}

def render_int(label: str, key: str):
    val = st.number_input(label, min_value=0, step=1, key=key, format="%d")
    # number_input defaults to 0; treat "touched" if user changes? keep raw value
    return val

def render_text(label: str, key: str):
    return st.text_input(label, key=key)

def fs_category(answers: Dict[str, Any]) -> Tuple[int, str]:
    def code(k):
        v = answers.get(k)
        return v.get("code") if isinstance(v, dict) else v
    affirm = 0
    if code("fs1") in (1, 2): affirm += 1
    if code("fs2") in (1, 2): affirm += 1
    if code("fs3") == 1:
        affirm += 1
        if code("fs3a") in (1, 2): affirm += 1
    if code("fs4") == 1: affirm += 1
    if code("fs5") == 1: affirm += 1

    if affirm <= 1: cat = "High or marginal food security"
    elif affirm <= 4: cat = "Low food security"
    else: cat = "Very low food security"
    return affirm, cat

def flatten_record_for_sheet(record: Dict[str, Any]) -> Tuple[List[str], Dict[str, Any]]:
    """
    Produce stable headers and a flat row dict for Google Sheets.
    radios -> two columns: <id>__code, <id>__label
    ints/text -> one column: <id>
    """
    headers = ["timestamp", "language"]
    row = {"timestamp": record["meta"]["completed_at"], "language": record["meta"]["language"]}

    for q in QUESTIONS:
        qid = q["id"]
        sec = q["section"]
        val = record["answers"].get(qid, None)
        if q["type"] == "radio":
            code_col = f"{qid}__code"
            lbl_col = f"{qid}__label"
            headers += [code_col, lbl_col]
            if isinstance(val, dict):
                row[code_col] = val.get("code", "")
                row[lbl_col] = val.get("label", "")
            else:
                row[code_col] = ""
                row[lbl_col] = ""
        else:
            headers.append(qid)
            row[qid] = "" if val is None else val

    # Derived
    headers += ["derived_food_security_raw", "derived_food_security_category"]
    row["derived_food_security_raw"] = record["derived"]["food_security_raw_score"]
    row["derived_food_security_category"] = record["derived"]["food_security_category"]
    return headers, row

# =========================
# UI: Header / Language
# =========================
with st.container():
    st.markdown(f"""
        <div class="sdoh-card">
          <div class="sdoh-title">🏥 Social Determinants of Health — Patient Form</div>
          <div class="sdoh-subtitle">{"Please select your language · Seleccione su idioma"}</div>
          <div class="sdoh-langwrap">
            <form>
              <button name="lang_en" class="sdoh-pill {'active' if get_lang()=='en' else ''}" formaction="?lang=en">English</button>
              <button name="lang_es" class="sdoh-pill {'active' if get_lang()=='es' else ''}" formaction="?lang=es">Español</button>
            </form>
          </div>
          <div class="sdoh-divider"></div>
          <div class="sdoh-caption">All items are optional. Radios start unselected. / Todos los campos son opcionales. Las opciones empiezan sin seleccionar.</div>
        </div>
    """, unsafe_allow_html=True)

# Update lang from query param if clicked
params = st.query_params
if params.get("lang") in ("en", "es"):
    st.session_state["lang"] = params.get("lang")
lang = get_lang()

# =========================
# Render Sections (Expanders)
# =========================
answers: Dict[str, Any] = {}

# Pre-fill from session_state if available (keeps answers when switching language)
for q in QUESTIONS:
    if q["id"] in st.session_state:
        val = st.session_state.get(q["id"])
        # We will rebuild answers after render based on fresh inputs
        # (This keeps UI state stable across reruns.)
        pass

question_number = 1
section_to_questions: Dict[str, List[Dict[str, Any]]] = {}
for q in QUESTIONS:
    section_to_questions.setdefault(q["section"], []).append(q)

# Count visible per section dynamically (but we show all questions stacked;
# visibility only hides branch-gated items).
for section_key, _lbl in SECTIONS:
    visible_in_section = [qq for qq in section_to_questions.get(section_key, []) if is_visible(answers=st.session_state, q=qq)]
    if not visible_in_section:
        # Still render expander with 0 count; items may appear as user answers
        visible_count = len(section_to_questions.get(section_key, []))
    else:
        visible_count = len(visible_in_section)

    display_title = f"{t_section(section_key)}  ({visible_count} {'questions' if lang=='en' else 'preguntas'})"
    with st.expander(display_title, expanded=False):
        for q in section_to_questions.get(section_key, []):
            if not is_visible(q, st.session_state):
                continue
            label = f"**{question_number}) {q['text'][lang]}**"
            key = q["id"]

            if q["type"] == "radio":
                val = render_radio(label, q["options"], key=key)
            elif q["type"] == "int":
                val = render_int(label, key=key)
            else:
                val = render_text(label, key=key)

            answers[key] = val
            question_number += 1

# =========================
# Submit & Save
# =========================
st.markdown("<div class='sdoh-divider'></div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    submit_label = "✅ Submit" if lang == "en" else "✅ Enviar"
    if st.button(submit_label, use_container_width=True, type="primary"):
        # Build record
        completed_at = datetime.datetime.now().isoformat(timespec="seconds")
        # Only save simple scalars so Streamlit doesn't choke on dicts
        for k, v in answers.items():
            try:
        # Convert anything complex (dicts/lists) into JSON text
                if isinstance(v, (dict, list)):
                    st.session_state[k] = json.dumps(v, ensure_ascii=False)
                else:
                    st.session_state[k] = v
            except Exception as e:
                st.warning(f"Could not store {k} in session: {e}")



        raw, cat = fs_category(answers)
        record = {
            "meta": {
                "completed_at": completed_at,
                "instrument": "SDoH Bilingual Streamlit v1.0",
                "language": lang
            },
            "answers": answers,
            "derived": {
                "food_security_raw_score": raw,
                "food_security_category": cat,
            }
        }

        # Prepare flat row and headers
        ws = get_worksheet()
        headers, row = flatten_record_for_sheet(record)
        ensure_headers(ws, headers)
        append_flat_record(ws, row, headers)

        # UI success
        msg = "✅ Thank you! Your responses were submitted." if lang == "en" else "✅ ¡Gracias! Sus respuestas fueron enviadas."
        st.success(msg)
        st.balloons()





