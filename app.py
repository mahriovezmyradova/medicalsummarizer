import streamlit as st
from datetime import datetime, date
import os
import sqlite3
import pandas as pd
from fpdf import FPDF
import time
import base64
from io import BytesIO

st.set_page_config(
    page_title="Medizinische Gesprächszusammenfassung",
    #page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Database setup
DB_PATH = "app.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def fetch_patient_names(conn):
    """Get all patient names for autocomplete"""
    return pd.read_sql("SELECT patient_name FROM patients ORDER BY patient_name", conn)

def load_patient_data(conn, patient_name):
    """Load patient data from database"""
    try:
        patient_sql = "SELECT * FROM patients WHERE patient_name = ?"
        patient_df = pd.read_sql(patient_sql, conn, params=(patient_name,))
        
        if patient_df.empty:
            return {}
        
        patient_data = patient_df.iloc[0].to_dict()
        return patient_data
    except Exception as e:
        st.error(f"Fehler beim Laden: {str(e)}")
        return {}

def init_database():
    conn = get_conn()
    cursor = conn.cursor()
    
    # Create patients table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT UNIQUE,
        geburtsdatum DATE,
        geschlecht TEXT,
        groesse INTEGER,
        gewicht INTEGER,
        therapiebeginn DATE,
        dauer INTEGER,
        tw_besprochen TEXT,
        allergie TEXT,
        diagnosen TEXT,
        kontrolltermin_4 BOOLEAN,
        kontrolltermin_12 BOOLEAN,
        kontrolltermin_kommentar TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create conversations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        summary TEXT,
        transcript TEXT,
        audio_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients (id) ON DELETE CASCADE
    )
    """)
    
    conn.commit()
    conn.close()

init_database()

# CSS Styling - matching THERAPIEKONZEPT exactly
st.markdown("""
<style>
.header-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 0;
}
.header-logo {
    flex: 1;
    text-align: left;
}
.header-title {
    flex: 1;
    text-align: center;
    margin: 0;
}
.header-address {
    flex: 1;
    text-align: right;
}
/* Success message styling */
.success-message {
    background-color: #d4edda;
    color: #155724;
    padding: 1px;
    border-radius: 4px;
    border: 1px solid #c3e6cb;
    margin: 10px 0;
}

/* Main color theme - RGB(38, 96, 65) */
.stButton > button {
    background-color: rgb(38, 96, 65) !important;
    color: white !important;
    border: 1px solid rgb(30, 76, 52) !important;
}

.stButton > button:hover {
    background-color: rgb(30, 76, 52) !important;
    border-color: rgb(25, 63, 43) !important;
    color: white !important;
}

/* Primary button styling */
.stButton > button[kind="primary"] {
    background-color: rgb(38, 96, 65) !important;
    color: white !important;
}

.stButton > button[kind="primary"]:hover {
    background-color: rgb(30, 76, 52) !important;
}

/* Secondary button styling */
.stButton > button[kind="secondary"] {
    background-color: rgb(240, 242, 246) !important;
    color: rgb(38, 96, 65) !important;
    border: 1px solid rgb(38, 96, 65) !important;
}

.stButton > button[kind="secondary"]:hover {
    background-color: rgb(230, 232, 236) !important;
    color: rgb(30, 76, 52) !important;
    border-color: rgb(30, 76, 52) !important;
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 0px !important;
    width: 100% !important;
}

.stTabs [data-baseweb="tab"] {
    height: 50px;
    white-space: pre-wrap;
    background-color: #f0f2f6;
    border-radius: 4px 4px 0px 0px;
    padding-top: 10px;
    padding-bottom: 10px;
    color: rgb(38, 96, 65);
    flex: 1 !important;
    text-align: center !important;
    justify-content: center !important;
    width: 50% !important;
    margin: 0 !important;
}

.stTabs [aria-selected="true"] {
    background-color: rgb(38, 96, 65) !important;
    color: white !important;
}

/* Checkbox styling */
[data-testid="stCheckbox"] span {
    color: rgb(38, 96, 65) !important;
}

/* Radio button styling */
[data-testid="stRadio"] span {
    color: rgb(38, 96, 65) !important;
}

/* Selectbox/Multiselect styling */
[data-testid="stSelectbox"] span, 
[data-testid="stMultiSelect"] span {
    color: rgb(38, 96, 65) !important;
}

/* Text input/textarea focus */
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: rgb(38, 96, 65) !important;
    box-shadow: 0 0 0 0.2rem rgba(38, 96, 65, 0.25) !important;
}
hr {
    margin: 2px 0 !important;
}

/* Number input focus */
.stNumberInput > div > div > input:focus {
    border-color: rgb(38, 96, 65) !important;
    box-shadow: 0 0 0 0.2rem rgba(38, 96, 65, 0.25) !important;
}

/* Date input focus */
[data-testid="stDateInput"] > div > div > input:focus {
    border-color: rgb(38, 96, 65) !important;
    box-shadow: 0 0 0 0.2rem rgba(38, 96, 65, 0.25) !important;
}

/* Error messages */
.stAlert.st-emotion-cache-1wrcr25 {
    border-left-color: rgb(38, 96, 65) !important;
}

/* Warning messages */
.stAlert.st-emotion-cache-1wrcr25.eeusbqq4 {
    border-left-color: rgb(255, 193, 7) !important;
}

/* Success messages */
.stAlert.st-emotion-cache-1wrcr25.e1f1d6gn3 {
    border-left-color: rgb(25, 135, 84) !important;
}

/* PDF header color */
.pdf-header {
    background-color: rgb(38, 96, 65) !important;
    color: white !important;
}



.section-header {
    background-color: rgb(38, 96, 65);
    color: white;
    padding: 0.75rem 1rem;
    border-radius: 4px;
    margin-bottom: 1.5rem;
    font-weight: bold;
    font-size: 1.2rem;
}

.info-card {
    background: linear-gradient(135deg, #f8fafc, #e0f2fe);
    border: 1px solid #cbd5e1;
    border-radius: 0.75rem;
    padding: 0.75rem;
    margin: 0.5rem 0;
}

.info-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.25rem;
}

.info-value {
    font-size: 1rem;
    font-weight: 600;
    color: #1e293b;
}

.summary-box {
    background: linear-gradient(135deg, #d1fae5, #cffafe, #dbeafe);
    border: 2px solid #a7f3d0;
    border-radius: 1rem;
    padding: 1.5rem;
    margin: 1rem 0;
}

.ai-badge {
    display: inline-block;
    background: linear-gradient(to right, #3b82f6, #10b981);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 500;
    margin-bottom: 1rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.main-title {
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(to right, #2563eb, #10b981, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
}

.subtitle {
    font-size: 1.125rem;
    color: #64748b;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# Header with three columns - exactly like THERAPIEKONZEPT
col1, col2, col3 = st.columns([0.7, 3, 0.7])

with col1:
    st.markdown('<div class="header-logo">', unsafe_allow_html=True)
    if os.path.exists("clinic_logo.png"):
        st.image("clinic_logo.png", width=200)
    elif os.path.exists("clinic_logo.svg"):
        st.image("clinic_logo.svg", width=200)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="header-title">', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; margin: 0;'>Medizinische Gesprächszusammenfassung</h3>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="header-address">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:14px; line-height:1.4;">
    Clausewitzstr. 2<br>
    10629 Berlin-Charlottenburg<br>
    +49 30 6633110<br>
    info@revitaclinic.de<br>
    www.revitaclinic.de
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# AI Badge and subtitle
st.markdown("""
<div style="text-align: center; padding: 1rem 0;">
    <div class="ai-badge">
        Intelligente Dokumentation für Patientengespräche
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'recorded_data' not in st.session_state:
    st.session_state.recorded_data = None
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = {}
if 'audio_bytes' not in st.session_state:
    st.session_state.audio_bytes = None
if 'last_loaded_patient' not in st.session_state:
    st.session_state.last_loaded_patient = None
if 'current_patient_input' not in st.session_state:
    st.session_state.current_patient_input = ""
if 'clicked_suggestion' not in st.session_state:
    st.session_state.clicked_suggestion = None
if 'display_patient_name' not in st.session_state:
    st.session_state.display_patient_name = ""
if 'just_loaded_patient' not in st.session_state:
    st.session_state.just_loaded_patient = False

# Patient data section
st.markdown("#### <span style='color: rgb(38, 96, 65);'>Patientendaten</span>", unsafe_allow_html=True)

# Get patient names for autocomplete
conn = get_conn()
patient_names_df = fetch_patient_names(conn)
patient_names = patient_names_df["patient_name"].tolist() if not patient_names_df.empty else []
conn.close()

# Handle suggestion click
if st.session_state.clicked_suggestion:
    name = st.session_state.clicked_suggestion
    conn = get_conn()
    patient_data = load_patient_data(conn, name)
    conn.close()
    
    if patient_data:
        st.session_state.patient_data = patient_data
        st.session_state.last_loaded_patient = name
        st.session_state.display_patient_name = name
        st.session_state.just_loaded_patient = True
    
    st.session_state.clicked_suggestion = None
    st.rerun()

# Determine text_input value
display_value = (
    st.session_state.display_patient_name
    if st.session_state.display_patient_name
    else st.session_state.patient_data.get("patient_name", "")
)

typed = st.text_input(
    "Geben Sie den Namen ein und drücken Sie die Eingabetaste, um Vorschläge zu suchen.",
    value=display_value,
    placeholder="Vor- und Nachname",
    key="patient_name_input"
)

# Track typing
if typed != st.session_state.current_patient_input:
    st.session_state.current_patient_input = typed
    
    # Clear old data if typing new patient
    if st.session_state.last_loaded_patient and typed and typed not in patient_names:
        st.session_state.patient_data = {}
        st.session_state.recorded_data = None
        st.session_state.last_loaded_patient = None
        st.session_state.display_patient_name = ""
        st.session_state.just_loaded_patient = False
        st.rerun()

st.session_state.display_patient_name = typed

# Show suggestions
suggestions = [n for n in patient_names if typed and typed.lower() in n.lower()]

if typed and suggestions and not st.session_state.just_loaded_patient:
    st.write("**Vorschläge:**")
    for name in suggestions[:7]:
        if st.button(name, key=f"suggest_{name}"):
            st.session_state.clicked_suggestion = name
            st.rerun()

# Auto-load on Enter (exact match)
patient_name_input = typed

if (patient_name_input and patient_name_input in patient_names and 
    patient_name_input != st.session_state.last_loaded_patient and 
    not st.session_state.just_loaded_patient):
    
    conn = get_conn()
    patient_data = load_patient_data(conn, patient_name_input)
    conn.close()
    
    if patient_data:
        st.session_state.patient_data = patient_data
        st.session_state.last_loaded_patient = patient_name_input
        st.session_state.display_patient_name = patient_name_input
        st.session_state.just_loaded_patient = True
        st.rerun()

# Reset flag
if st.session_state.just_loaded_patient:
    st.session_state.just_loaded_patient = False

# Get current patient data
pdata = st.session_state.patient_data or {}

# Default values
default_geburtsdatum = pdata.get("geburtsdatum", None)
if isinstance(default_geburtsdatum, str):
    try:
        default_geburtsdatum = datetime.strptime(default_geburtsdatum, '%Y-%m-%d').date()
    except:
        default_geburtsdatum = None

default_geschlecht = pdata.get("geschlecht", "")
default_groesse = int(pdata.get("groesse", 170))
default_gewicht = int(pdata.get("gewicht", 70))

default_therapiebeginn = pdata.get("therapiebeginn", None)
if isinstance(default_therapiebeginn, str):
    try:
        default_therapiebeginn = datetime.strptime(default_therapiebeginn, '%Y-%m-%d').date()
    except:
        default_therapiebeginn = None

default_dauer_value = int(pdata.get("dauer", 1))
default_tw_besprochen = pdata.get("tw_besprochen", "Ja")
default_allergie = pdata.get("allergie", "")
default_diagnosen = pdata.get("diagnosen", "")

# Layout with 7 columns - exactly like THERAPIEKONZEPT
c1, c2, c3, c4, c5, c6, c7 = st.columns(7)

with c1:
    geburtsdatum = st.date_input(
        "Geburtsdatum",
        value=default_geburtsdatum,
        min_value=date(1900, 1, 1),
        max_value=date.today(),
        format="DD.MM.YYYY",
        key="geburtsdatum_input"
    )

with c2:
    geschlecht = st.radio(
        "Geschlecht", ["M", "W"], horizontal=True,
        index=0 if default_geschlecht == "M" else 1 if default_geschlecht == "W" else 0,
        key="geschlecht_input"
    )

with c3:
    groesse = st.number_input("Grösse (cm)", min_value=0, max_value=250, value=default_groesse, key="groesse_input")

with c4:
    gewicht = st.number_input("Gewicht (kg)", min_value=0, max_value=300, value=default_gewicht, key="gewicht_input")

with c5:
    therapiebeginn = st.date_input(
        "Therapiebeginn",
        value=default_therapiebeginn,
        format="DD.MM.YYYY",
        key="therapiebeginn_input"
    )

with c6:
    dauer = st.selectbox(
        "Dauer (Monate)",
        list(range(1, 13)),
        index=default_dauer_value - 1,
        key="dauer_input"
    )

with c7:
    tw_besprochen = st.radio(
        "TW besprochen?",
        ["Ja", "Nein"],
        horizontal=True,
        index=0 if default_tw_besprochen == "Ja" else 1,
        key="tw_besprochen_input"
    )

bekannte_allergie = st.text_input("Bekannte Allergie?", value=default_allergie, key="allergie_input")

diagnosen = st.text_area(
    "Diagnosen",
    value=default_diagnosen,
    height=100,
    placeholder="Relevante Diagnosen...",
    key="diagnosen_input"
)

# Kontrolltermine
st.markdown("---")
st.markdown("#### <span style='color: rgb(38, 96, 65);'>Kontrolltermine</span>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    kontrolltermin_4 = st.checkbox("4 Wochen", value=pdata.get("kontrolltermin_4", False), key="kontrolltermin_4_input")
with col2:
    kontrolltermin_12 = st.checkbox("12 Wochen", value=pdata.get("kontrolltermin_12", False), key="kontrolltermin_12_input")

kontrolltermin_kommentar = st.text_input("Kommentar:", value=pdata.get("kontrolltermin_kommentar", ""), key="kontrolltermin_kommentar_input")

# Save button - left aligned
if st.button("Patientendaten speichern", use_container_width=False, type="primary"):
    if not patient_name_input:
        st.error("Bitte Patientennamen eingeben!")
    else:
        conn = get_conn()
        cursor = conn.cursor()
        
        # Check if patient exists
        cursor.execute("SELECT id FROM patients WHERE patient_name = ?", (patient_name_input,))
        existing = cursor.fetchone()
        
        if existing:
            # Update
            sql = """
            UPDATE patients SET
                geburtsdatum=?, geschlecht=?, groesse=?, gewicht=?,
                therapiebeginn=?, dauer=?, tw_besprochen=?, allergie=?, diagnosen=?,
                kontrolltermin_4=?, kontrolltermin_12=?, kontrolltermin_kommentar=?
            WHERE patient_name=?
            """
            cursor.execute(sql, (
                geburtsdatum, geschlecht, groesse, gewicht,
                therapiebeginn, dauer, tw_besprochen, bekannte_allergie, diagnosen,
                kontrolltermin_4, kontrolltermin_12, kontrolltermin_kommentar,
                patient_name_input
            ))
        else:
            # Insert
            sql = """
            INSERT INTO patients (
                patient_name, geburtsdatum, geschlecht, groesse, gewicht,
                therapiebeginn, dauer, tw_besprochen, allergie, diagnosen,
                kontrolltermin_4, kontrolltermin_12, kontrolltermin_kommentar
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(sql, (
                patient_name_input, geburtsdatum, geschlecht, groesse, gewicht,
                therapiebeginn, dauer, tw_besprochen, bekannte_allergie, diagnosen,
                kontrolltermin_4, kontrolltermin_12, kontrolltermin_kommentar
            ))
        
        conn.commit()
        conn.close()
        
        # Update session state
        st.session_state.patient_data = {
            "patient_name": patient_name_input,
            "geburtsdatum": geburtsdatum,
            "geschlecht": geschlecht,
            "groesse": groesse,
            "gewicht": gewicht,
            "therapiebeginn": therapiebeginn,
            "dauer": dauer,
            "tw_besprochen": tw_besprochen,
            "allergie": bekannte_allergie,
            "diagnosen": diagnosen,
            "kontrolltermin_4": kontrolltermin_4,
            "kontrolltermin_12": kontrolltermin_12,
            "kontrolltermin_kommentar": kontrolltermin_kommentar
        }
        st.session_state.last_loaded_patient = patient_name_input
        
        st.success("Patientendaten gespeichert!")
        time.sleep(1)
        st.rerun()


# Recording section
st.markdown("---")
st.markdown("#### <span style='color: rgb(38, 96, 65);'>Gesprächsaufnahme</span>", unsafe_allow_html=True)


col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    audio_bytes = st.audio_input("Aufnahme starten", key="audio_recorder")
    
    if audio_bytes and audio_bytes != st.session_state.get('last_processed_audio'):
        st.session_state.audio_bytes = audio_bytes
        st.session_state.last_processed_audio = audio_bytes
        
        with st.spinner("🔄 Verarbeite Aufnahme..."):
            # Raw transcript from therapy session (no role labels)
            transcript = """Also ich bin jetzt seit etwa drei Monaten in dieser Situation. Die Kopfschmerzen sind irgendwie immer da, vor allem morgens wenn ich aufwache. Es ist so ein dumpfer Druck, manchmal auch im Nacken. Und diese Müdigkeit... ich komm einfach nicht aus dem Bett. Mein Mann sagt, ich bin so reizbar geworden, dabei will ich das gar nicht.

Nachts lieg ich wach und die Gedanken kreisen. Dann denk ich an die Arbeit, an das Projekt, an alles was ich noch erledigen muss. Eigentlich mag ich meinen Job, aber im Moment ist es einfach zu viel. Früher bin ich gerne Fahrrad gefahren, aber dafür hab ich jetzt keine Kraft mehr.

Die Schmerztabletten helfen vielleicht zwei Stunden, dann kommt alles zurück. Ich will auch nicht zu viele nehmen, das kann doch nicht gut sein. Meine Freundin meinte, ich soll mal zum Arzt gehen, weil das so nicht weitergeht.

Ich weiß auch nicht, vielleicht ist es einfach die Jahreszeit oder so. Aber es fühlt sich an wie ein großer Berg, den ich jeden Tag erklimmen muss. Mein Mann versucht mich zu unterstützen, aber ich merke, dass er sich auch Sorgen macht.

Eigentlich wollte ich heute auch noch einkaufen, aber ich hab mich einfach nicht aufraffen können. Das ist doch nicht normal, oder? Ich meine, ich war früher immer so aktiv und jetzt...

Naja, mal sehen was die Blutuntersuchung ergibt. Vielleicht fehlt mir ja wirklich was, Eisen oder so. Meine Schwester hatte mal Probleme mit der Schilddrüse, das kann ja auch solche Symptome machen.

Ich bin froh, dass ich heute hier bin. Es tut gut, das mal alles auszusprechen. Zu Hause will ich meinen Mann nicht so belasten, der hat selbst genug Stress."""

            # BERT-style extractive summary (just key sentences, no structure)
            patient_name = patient_name_input or "Die Patientin"
            summary = f"""Die Patientin leidet seit etwa drei Monaten unter morgendlichen Kopfschmerzen, die sie als dumpfen Druck im Stirn- und Nackenbereich beschreibt. Begleitend besteht eine ausgeprägte Antriebslosigkeit und Erschöpfung, die das Aufstehen erschwert. Der Ehemann habe eine zunehmende Reizbarkeit bemerkt. Schlafstörungen mit nächtlichem Gedankenkreisen werden angegeben.

Beruflich besteht eine hohe Belastung durch ein Projekt, frühere Ausgleichsaktivitäten wie Radfahren können nicht mehr ausgeführt werden. Die Wirkung von Schmerzmitteln sei nur kurzfristig, bei gleichzeitiger Sorge vor zu hohem Konsum. Die Eigeninitiative zur Vorstellung erfolgte auf Anraten einer Freundin.

Die Alltagsbewältigung ist deutlich eingeschränkt, geplante Aktivitäten wie Einkaufen können nicht umgesetzt werden. Die Patientin zeigt sich besorgt über die Veränderung ihres gewohnten Aktivitätsniveaus. Die familiäre Unterstützung ist vorhanden, die Patientin möchte Angehörige jedoch nicht belasten.

Als mögliche Ursache werden Eisenmangel oder Schilddrüsenprobleme vermutet, letztere mit familiärer Vorbelastung. Die Patientin äußert Erleichterung über das Gespräch und die Möglichkeit, die Belastung auszusprechen. Weitere Diagnostik mittels Blutuntersuchung wurde veranlasst, um somatische Ursachen auszuschließen."""

            st.session_state.recorded_data = {
                'summary': summary,
                'transcript': transcript,
                'audio_data': audio_bytes
            }


            # Save conversation if patient exists
            if st.session_state.patient_data.get('patient_name'):
                conn = get_conn()
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM patients WHERE patient_name = ?", 
                             (st.session_state.patient_data['patient_name'],))
                result = cursor.fetchone()
                if result:
                    cursor.execute("""
                        INSERT INTO conversations (patient_id, summary, transcript)
                        VALUES (?, ?, ?)
                    """, (result[0], summary, transcript))
                    conn.commit()
                conn.close()
            
            st.rerun()
    
    if st.session_state.audio_bytes is None:
        st.markdown("<p style='text-align: center; color: #64748b; margin-top: 1rem;'>Klicken Sie auf das Mikrofon, um die Aufnahme zu starten</p>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Results display
if st.session_state.recorded_data:
    st.markdown("---")
    st.markdown("#### <span style='color: rgb(38, 96, 65);'>Zusammenfassung</span>", unsafe_allow_html=True)

    # Simple summary display without colored box
    st.markdown(f"""
    <div style="background-color: white; padding: 1.5rem; border: 1px solid #e0e0e0; border-radius: 4px; margin: 1rem 0; line-height: 1.8;">
        {st.session_state.recorded_data['summary']}
    </div>
    """, unsafe_allow_html=True)

    # PDF Button - now placed AFTER the summary
    if st.button("PDF Herunterladen", use_container_width=False, type="primary"):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Medizinische Gesprächszusammenfassung", 0, 1, "C")
            pdf.ln(10)
            
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"Patient: {patient_name_input}", 0, 1)
            pdf.ln(5)
            
            pdf.set_font("Arial", "", 11)
            summary_lines = st.session_state.recorded_data['summary'].split('\n')
            for line in summary_lines:
                if line.strip():
                    pdf.multi_cell(0, 8, line)
            
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            
            st.download_button(
                label="PDF speichern",
                data=pdf_bytes,
                file_name=f"Zusammenfassung_{patient_name_input}.pdf",
                mime="application/pdf",
                key="pdf_download"
            )
        except Exception as e:
            st.error(f"Fehler bei PDF-Erstellung: {e}")

    # Transcript
    st.markdown("---")
    st.markdown("#### <span style='color: rgb(38, 96, 65);'>Transkript</span>", unsafe_allow_html=True)
    with st.expander("Vollständiges Transkript anzeigen"):
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 1.5rem; border: 1px solid #e0e0e0; border-radius: 4px;">
            <pre style="font-family: monospace; white-space: pre-wrap; margin: 0;">{st.session_state.recorded_data['transcript']}</pre>
        </div>
        """, unsafe_allow_html=True)

    # Audio playback
    if st.session_state.recorded_data.get('audio_data'):
        st.markdown("---")
        st.markdown("#### <span style='color: rgb(38, 96, 65);'>Audioaufnahme</span>", unsafe_allow_html=True)
        st.audio(st.session_state.recorded_data['audio_data'])