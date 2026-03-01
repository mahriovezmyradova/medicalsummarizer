import streamlit as st
from datetime import datetime, date
import base64
from io import BytesIO
import os

st.set_page_config(
    page_title="Medizinische Gesprächszusammenfassung",
    #page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Replace the existing CSS with this updated version (matching THERAPIEKONZEPT styling)
custom_css = """
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
    flex: 2;
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
    padding: 12px;
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

/* Original app specific styling */
.main {
    background: linear-gradient(135deg, #eff6ff 0%, #d1fae5 50%, #cffafe 100%);
}

.stApp {
    background: linear-gradient(135deg, #eff6ff 0%, #d1fae5 50%, #cffafe 100%);
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

.card {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    border-radius: 1.5rem;
    padding: 2rem;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    margin-bottom: 1.5rem;
    transition: all 0.3s ease;
}

.card:hover {
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
}

.accent-bar {
    width: 4px;
    height: 2rem;
    background: linear-gradient(to bottom, #3b82f6, #10b981);
    border-radius: 9999px;
}

.section-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1e293b;
    margin: 0;
}

div[data-testid="stSelectbox"] > div,
div[data-testid="stTextInput"] > div,
div[data-testid="stTextArea"] > div,
div[data-testid="stDateInput"] > div,
div[data-testid="stNumberInput"] > div {
    border-radius: 0.75rem !important;
    border: 2px solid #e2e8f0 !important;
    transition: all 0.3s ease !important;
    background: rgba(255, 255, 255, 0.5) !important;
}

div[data-testid="stSelectbox"] > div:hover,
div[data-testid="stTextInput"] > div:hover,
div[data-testid="stTextArea"] > div:hover,
div[data-testid="stDateInput"] > div:hover,
div[data-testid="stNumberInput"] > div:hover {
    background: white !important;
    border-color: #10b981 !important;
}

div[data-testid="stSelectbox"] > div:focus-within,
div[data-testid="stTextInput"] > div:focus-within,
div[data-testid="stTextArea"] > div:focus-within,
div[data-testid="stDateInput"] > div:focus-within,
div[data-testid="stNumberInput"] > div:focus-within {
    border-color: #10b981 !important;
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1) !important;
}

.stButton > button {
    border-radius: 0.75rem;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    transition: all 0.3s ease;
    border: none;
}

.stButton > button:hover {
    transform: scale(1.05);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.recording-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
    padding: 2rem;
}

.recording-button {
    width: 140px;
    height: 140px;
    border-radius: 50%;
    border: none;
    cursor: pointer;
    transition: all 0.5s ease;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3rem;
}

.recording-button.idle {
    background: linear-gradient(135deg, #34d399, #06b6d4, #3b82f6);
}

.recording-button.recording {
    background: linear-gradient(135deg, #fb923c, #ef4444, #ec4899);
    animation: pulse-glow 2s ease-in-out infinite;
}

@keyframes pulse-glow {
    0%, 100% {
        box-shadow: 0 0 30px rgba(251, 146, 60, 0.6), 0 0 60px rgba(236, 72, 153, 0.4);
    }
    50% {
        box-shadow: 0 0 50px rgba(251, 146, 60, 0.8), 0 0 90px rgba(236, 72, 153, 0.6);
    }
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

label {
    font-weight: 600 !important;
    color: #334155 !important;
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# Header with three columns (matching THERAPIEKONZEPT)
col1, col2, col3 = st.columns([1.2, 3, 0.7])

with col1:
    st.markdown('<div class="header-logo">', unsafe_allow_html=True)
    # Logo file should be placed in the same directory as your app
    # Save your logo as "clinic_logo.png" in your app directory
    if os.path.exists("clinic_logo.png"):
        st.image("clinic_logo.svg", width=200)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="header-title">', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; margin: 0;'>Medizinische Gesprächszusammenfassung</h1>", unsafe_allow_html=True)
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



if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'recorded_data' not in st.session_state:
    st.session_state.recorded_data = None
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = {}

# Patient data section (matching THERAPIEKONZEPT styling)
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("""
<div class="section-header">
    <div class="accent-bar"></div>
    <h2 class="section-title">Patientendaten</h2>
</div>
""", unsafe_allow_html=True)

# Use the same layout as THERAPIEKONZEPT for patient data
c1, c2, c3, c4, c5, c6, c7 = st.columns(7)

with c1:
    geburtsdatum = st.date_input(
        "Geburtsdatum",
        value=None,
        min_value=date(1900, 1, 1),
        max_value=date.today(),
        format="DD.MM.YYYY",
        key="geburtsdatum_input"
    )

with c2:
    geschlecht = st.radio(
        "Geschlecht", ["M", "W"], horizontal=True,
        index=0,
        key="geschlecht_input"
    )

with c3:
    groesse = st.number_input("Grösse (cm)", min_value=0, max_value=250, value=170, key="groesse_input")

with c4:
    gewicht = st.number_input("Gewicht (kg)", min_value=0, max_value=300, value=70, key="gewicht_input")

with c5:
    therapiebeginn = st.date_input(
        "Therapiebeginn",
        value=None,
        format="DD.MM.YYYY",
        key="therapiebeginn_input"
    )

with c6:
    dauer = st.selectbox(
        "Dauer (Monate)",
        list(range(1, 13)),
        index=0,
        key="dauer_input"
    )

with c7:
    tw_besprochen = st.radio(
        "TW besprochen?",
        ["Ja", "Nein"],
        horizontal=True,
        index=0,
        key="tw_besprochen_input"
    )

allergie = st.text_input("Bekannte Allergie?", placeholder="Allergien eingeben", key="allergie_input")
diagnosen = st.text_area("Diagnosen", placeholder="Diagnosen eingeben", height=100, key="diagnosen_input")

st.markdown("---")
st.markdown("#### Kontrolltermine")

kontroll_col1, kontroll_col2 = st.columns(2)
with kontroll_col1:
    kontrolltermin_4 = st.checkbox("4 Wochen", key="kontrolltermin_4_input")
with kontroll_col2:
    kontrolltermin_12 = st.checkbox("12 Wochen", key="kontrolltermin_12_input")

kontrolltermin_kommentar = st.text_input("Kommentar:", key="kontrolltermin_kommentar_input")

st.session_state.patient_data = {
    'geburtsdatum': geburtsdatum,
    'geschlecht': geschlecht,
    'groesse': groesse,
    'gewicht': gewicht,
    'therapiebeginn': therapiebeginn,
    'dauer': dauer,
    'tw_besprochen': tw_besprochen,
    'allergie': allergie,
    'diagnosen': diagnosen,
    'kontrolltermin_4': kontrolltermin_4,
    'kontrolltermin_12': kontrolltermin_12,
    'kontrolltermin_kommentar': kontrolltermin_kommentar
}

st.markdown('</div>', unsafe_allow_html=True)

# Rest of your app remains the same from here...
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("""
<div class="section-header" style="justify-content: center;">
    <div class="accent-bar" style="background: linear-gradient(to bottom, #06b6d4, #3b82f6);"></div>
    <h2 class="section-title">Gesprächsaufnahme</h2>
    <div class="accent-bar" style="background: linear-gradient(to bottom, #3b82f6, #06b6d4);"></div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if not st.session_state.recording:
        if st.button("🎤 Aufnahme starten", key="start_recording", use_container_width=True, type="primary"):
            st.session_state.recording = True
            st.rerun()
        st.markdown("<p style='text-align: center; color: #64748b; margin-top: 1rem;'>Klicken Sie auf das Mikrofon, um die Aufnahme zu starten</p>", unsafe_allow_html=True)
    else:
        if st.button("⏹️ Aufnahme beenden", key="stop_recording", use_container_width=True, type="secondary"):
            st.session_state.recording = False
            st.session_state.recorded_data = {
                'summary': 'Die Zusammenfassung wird hier angezeigt, sobald die Aufnahme verarbeitet wurde...\n\nHier können Sie Ihre Python-Backend-Integration für Whisper API hinzufügen.',
                'transcript': 'Das vollständige Transkript wird hier angezeigt...\n\nIntegrieren Sie hier Ihren Python-Code für die Whisper API-Verarbeitung.',
                'audio_data': None
            }
            st.rerun()
        st.markdown("<p style='text-align: center; color: #ef4444; font-weight: 600; margin-top: 1rem;'> Aufnahme läuft...</p>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.recorded_data:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">
        <div class="accent-bar"></div>
        <h2 class="section-title">Zusammenfassung</h2>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button(" PDF Herunterladen", use_container_width=True, type="primary"):
            st.info("PDF-Download-Funktionalität - Integrieren Sie hier Ihren Python-Code für PDF-Generierung")

    st.markdown(f"""
    <div class="summary-box">
        <p style="color: #1e293b; line-height: 1.8;">{st.session_state.recorded_data['summary']}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Patienteninformationen")

    col1, col2, col3 = st.columns(3)

    with col1:
        geburtsdatum_str = st.session_state.patient_data.get('geburtsdatum', '')
        if geburtsdatum_str:
            geburtsdatum_str = geburtsdatum_str.strftime("%d.%m.%Y")

        st.markdown(f"""
        <div class="info-card" style="background: linear-gradient(135deg, #f8fafc, #dbeafe);">
            <div class="info-label">Geburtsdatum</div>
            <div class="info-value">{geburtsdatum_str}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="info-card" style="background: linear-gradient(135deg, #f8fafc, #dbeafe);">
            <div class="info-label">Größe</div>
            <div class="info-value">{st.session_state.patient_data.get('groesse', 0)} cm</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="info-card" style="background: linear-gradient(135deg, #f8fafc, #dbeafe);">
            <div class="info-label">Dauer</div>
            <div class="info-value">{st.session_state.patient_data.get('dauer', 1)} Monate</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="info-card" style="background: linear-gradient(135deg, #f8fafc, #d1fae5);">
            <div class="info-label">Geschlecht</div>
            <div class="info-value">{st.session_state.patient_data.get('geschlecht', '-')}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="info-card" style="background: linear-gradient(135deg, #f8fafc, #d1fae5);">
            <div class="info-label">Gewicht</div>
            <div class="info-value">{st.session_state.patient_data.get('gewicht', 0)} kg</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="info-card" style="background: linear-gradient(135deg, #f8fafc, #d1fae5);">
            <div class="info-label">TW besprochen</div>
            <div class="info-value">{st.session_state.patient_data.get('tw_besprochen', '-')}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        therapiebeginn_str = st.session_state.patient_data.get('therapiebeginn', '')
        if therapiebeginn_str:
            therapiebeginn_str = therapiebeginn_str.strftime("%d.%m.%Y")

        st.markdown(f"""
        <div class="info-card" style="background: linear-gradient(135deg, #f8fafc, #cffafe);">
            <div class="info-label">Therapiebeginn</div>
            <div class="info-value">{therapiebeginn_str}</div>
        </div>
        """, unsafe_allow_html=True)

        kontrolltermine = []
        if st.session_state.patient_data.get('kontrolltermin_4'):
            kontrolltermine.append("4 Wochen")
        if st.session_state.patient_data.get('kontrolltermin_12'):
            kontrolltermine.append("12 Wochen")
        
        kontrolltext = ", ".join(kontrolltermine) if kontrolltermine else "-"
        
        st.markdown(f"""
        <div class="info-card" style="background: linear-gradient(135deg, #f8fafc, #cffafe);">
            <div class="info-label">Kontrolltermine</div>
            <div class="info-value">{kontrolltext}</div>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.patient_data.get('allergie'):
        st.markdown(f"""
        <div class="info-card" style="background: linear-gradient(135deg, #fed7aa, #fef3c7); border-color: #fdba74;">
            <div class="info-label">Allergien</div>
            <div class="info-value">{st.session_state.patient_data.get('allergie', '')}</div>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.patient_data.get('diagnosen'):
        st.markdown(f"""
        <div class="info-card" style="background: linear-gradient(135deg, #cffafe, #dbeafe); border-color: #67e8f9;">
            <div class="info-label">Diagnosen</div>
            <div class="info-value">{st.session_state.patient_data.get('diagnosen', '')}</div>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.patient_data.get('kontrolltermin_kommentar'):
        st.markdown(f"""
        <div class="info-card" style="background: linear-gradient(135deg, #cffafe, #dbeafe); border-color: #67e8f9;">
            <div class="info-label">Kontrolltermin Kommentar</div>
            <div class="info-value">{st.session_state.patient_data.get('kontrolltermin_kommentar', '')}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    with st.expander(" Vollständiges Transkript anzeigen"):
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f8fafc, #dbeafe); border: 2px solid #bfdbfe; border-radius: 0.75rem; padding: 1.5rem; margin: 1rem 0;">
            <pre style="font-family: monospace; color: #1e293b; white-space: pre-wrap; margin: 0;">{st.session_state.recorded_data['transcript']}</pre>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">
        <div class="accent-bar" style="background: linear-gradient(to bottom, #06b6d4, #3b82f6);"></div>
        <h2 class="section-title">Audioaufnahme</h2>
    </div>
    """, unsafe_allow_html=True)
    st.info("Die Audioaufnahme wird hier angezeigt. Integrieren Sie Ihren Python-Code für Audio-Speicherung und Wiedergabe.")
    st.markdown('</div>', unsafe_allow_html=True)