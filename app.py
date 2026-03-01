import streamlit as st
from datetime import datetime, date
import base64
from io import BytesIO
import os

# Import utility modules
from audio_utils import record_audio, transcribe_with_whisper
from pdf_utils import generate_medical_pdf

st.set_page_config(
    page_title="Medizinische Gesprächszusammenfassung",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS styling (keep your existing CSS from app.py)
custom_css = """
<style>
/* Paste your existing CSS here */
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# Header
col1, col2, col3 = st.columns([1.2, 3, 0.7])

with col1:
    st.markdown('<div class="header-logo">', unsafe_allow_html=True)
    # Try both .png and .svg formats
    if os.path.exists("clinic_logo.png"):
        st.image("clinic_logo.png", width=200)
    elif os.path.exists("clinic_logo.svg"):
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

# Initialize session state
if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'recorded_data' not in st.session_state:
    st.session_state.recorded_data = None
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = {}
if 'audio_bytes' not in st.session_state:
    st.session_state.audio_bytes = None

# AI Badge
st.markdown("""
<div style="text-align: center; padding: 1rem 0;">
    <div class="ai-badge">
        ● KI-Powered
    </div>
    <p class="subtitle">Intelligente Dokumentation für Patientengespräche</p>
</div>
""", unsafe_allow_html=True)

# Patient data section
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("""
<div class="section-header">
    <div class="accent-bar"></div>
    <h2 class="section-title">Patientendaten</h2>
</div>
""", unsafe_allow_html=True)

# Patient form - 7 columns layout
c1, c2, c3, c4, c5, c6, c7 = st.columns(7)

with c1:
    vorname = st.text_input("Vorname", key="vorname")
with c2:
    nachname = st.text_input("Nachname", key="nachname")
with c3:
    geburtsdatum = st.date_input(
        "Geburtsdatum",
        value=None,
        min_value=date(1900, 1, 1),
        max_value=date.today(),
        format="DD.MM.YYYY",
        key="geburtsdatum_input"
    )
with c4:
    geschlecht = st.selectbox("Geschlecht", ["", "M", "W"], key="geschlecht")
with c5:
    groesse = st.number_input("Größe (cm)", min_value=0, max_value=250, value=170, key="groesse")
with c6:
    gewicht = st.number_input("Gewicht (kg)", min_value=0, max_value=300, value=70, key="gewicht")
with c7:
    therapiebeginn = st.date_input(
        "Therapiebeginn",
        value=None,
        format="DD.MM.YYYY",
        key="therapiebeginn_input"
    )

# Second row
c1, c2, c3, c4, c5, c6, c7 = st.columns(7)

with c1:
    dauer = st.selectbox("Dauer (Monate)", list(range(1, 13)), index=0, key="dauer")
with c2:
    tw_besprochen = st.selectbox("TW besprochen?", ["", "Ja", "Nein"], key="tw_besprochen")
with c3:
    pass  # Empty for spacing
with c4:
    pass  # Empty for spacing
with c5:
    pass  # Empty for spacing
with c6:
    pass  # Empty for spacing
with c7:
    pass  # Empty for spacing

allergie = st.text_input("Bekannte Allergie?", placeholder="Allergien eingeben", key="allergie")
diagnosen = st.text_area("Diagnosen", placeholder="Diagnosen eingeben", height=100, key="diagnosen")

st.markdown("---")
st.markdown("#### Kontrolltermine")

kontroll_col1, kontroll_col2 = st.columns(2)
with kontroll_col1:
    kontrolltermin_4 = st.checkbox("4 Wochen", key="kontrolltermin_4")
with kontroll_col2:
    kontrolltermin_12 = st.checkbox("12 Wochen", key="kontrolltermin_12")

kontrolltermin_kommentar = st.text_input("Kommentar:", key="kontrolltermin_kommentar")

# Save patient data to session state
st.session_state.patient_data = {
    'vorname': vorname,
    'nachname': nachname,
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

# Recording section
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
    # Audio recording using Streamlit's built-in audio recorder
    audio_bytes = st.audio_input("Aufnahme starten", key="audio_recorder")
    
    if audio_bytes:
        st.session_state.audio_bytes = audio_bytes
        st.session_state.recording = False
        
        # Process the audio (mock for now)
        with st.spinner("Verarbeite Aufnahme..."):
            # TODO: Implement actual transcription with Whisper
            # transcript = transcribe_with_whisper(audio_bytes)
            transcript = "Hier würde das transkribierte Gespräch erscheinen..."
            
            # TODO: Generate summary with GPT
            summary = "Hier würde die KI-generierte Zusammenfassung erscheinen..."
            
            st.session_state.recorded_data = {
                'summary': summary,
                'transcript': transcript,
                'audio_data': audio_bytes
            }
        st.rerun()
    
    if st.session_state.audio_bytes is None:
        st.markdown("<p style='text-align: center; color: #64748b; margin-top: 1rem;'>Klicken Sie auf das Mikrofon, um die Aufnahme zu starten</p>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Results display
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
        if st.button("📥 PDF Herunterladen", use_container_width=True, type="primary"):
            # Generate PDF
            pdf_buffer = generate_medical_pdf(
                st.session_state.patient_data,
                st.session_state.recorded_data['summary'],
                st.session_state.recorded_data['transcript']
            )
            
            # Download button
            st.download_button(
                label="PDF speichern",
                data=pdf_buffer,
                file_name=f"Patient_{st.session_state.patient_data.get('vorname', '')}_{st.session_state.patient_data.get('nachname', '')}.pdf",
                mime="application/pdf",
                key="pdf_download"
            )

    st.markdown(f"""
    <div class="summary-box">
        <p style="color: #1e293b; line-height: 1.8;">{st.session_state.recorded_data['summary']}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Patienteninformationen")

    # Display patient info in columns
    col1, col2, col3 = st.columns(3)

    with col1:
        geburtsdatum_str = st.session_state.patient_data.get('geburtsdatum', '')
        if geburtsdatum_str:
            geburtsdatum_str = geburtsdatum_str.strftime("%d.%m.%Y") if hasattr(geburtsdatum_str, 'strftime') else str(geburtsdatum_str)

        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">Name</div>
            <div class="info-value">{st.session_state.patient_data.get('vorname', '')} {st.session_state.patient_data.get('nachname', '')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">Geburtsdatum</div>
            <div class="info-value">{geburtsdatum_str}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">Geschlecht</div>
            <div class="info-value">{st.session_state.patient_data.get('geschlecht', '-')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">Größe / Gewicht</div>
            <div class="info-value">{st.session_state.patient_data.get('groesse', 0)} cm / {st.session_state.patient_data.get('gewicht', 0)} kg</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        therapiebeginn_str = st.session_state.patient_data.get('therapiebeginn', '')
        if therapiebeginn_str:
            therapiebeginn_str = therapiebeginn_str.strftime("%d.%m.%Y") if hasattr(therapiebeginn_str, 'strftime') else str(therapiebeginn_str)

        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">Therapiebeginn</div>
            <div class="info-value">{therapiebeginn_str}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">Dauer / TW</div>
            <div class="info-value">{st.session_state.patient_data.get('dauer', 1)} Monate / {st.session_state.patient_data.get('tw_besprochen', '-')}</div>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.patient_data.get('allergie'):
        st.markdown(f"""
        <div class="info-card" style="background: linear-gradient(135deg, #fed7aa, #fef3c7);">
            <div class="info-label">Allergien</div>
            <div class="info-value">{st.session_state.patient_data.get('allergie', '')}</div>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.patient_data.get('diagnosen'):
        st.markdown(f"""
        <div class="info-card" style="background: linear-gradient(135deg, #cffafe, #dbeafe);">
            <div class="info-label">Diagnosen</div>
            <div class="info-value">{st.session_state.patient_data.get('diagnosen', '')}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Transcript expander
    st.markdown('<div class="card">', unsafe_allow_html=True)
    with st.expander("📄 Vollständiges Transkript anzeigen"):
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f8fafc, #dbeafe); border: 2px solid #bfdbfe; border-radius: 0.75rem; padding: 1.5rem;">
            <pre style="font-family: monospace; color: #1e293b; white-space: pre-wrap;">{st.session_state.recorded_data['transcript']}</pre>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Audio playback
    if st.session_state.recorded_data.get('audio_data'):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="section-header">
            <div class="accent-bar" style="background: linear-gradient(to bottom, #06b6d4, #3b82f6);"></div>
            <h2 class="section-title">Audioaufnahme</h2>
        </div>
        """, unsafe_allow_html=True)
        st.audio(st.session_state.recorded_data['audio_data'])
        st.markdown('</div>', unsafe_allow_html=True)
