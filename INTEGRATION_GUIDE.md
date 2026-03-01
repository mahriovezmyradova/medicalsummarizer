# Backend-Integration Guide

Diese Anleitung zeigt Ihnen, wie Sie Ihre Python-Backend-Logik mit Whisper API und PDF-Generierung integrieren.

## Übersicht

Die Streamlit-App ist als Frontend-Interface vorbereitet. Sie müssen folgende Backend-Komponenten integrieren:

1. **Audio-Aufnahme** - Browser-basierte Aufnahme
2. **Whisper API** - Transkription von Gesprächen
3. **GPT-4 API** - Generierung von Zusammenfassungen
4. **PDF-Generierung** - Export der Dokumentation

## 1. Audio-Aufnahme Integration

### Option A: Browser-basierte Aufnahme mit JavaScript

Fügen Sie dies in `app.py` ein:

```python
import streamlit as st
from streamlit.components.v1 import html

def audio_recorder():
    html_code = """
    <script>
    let mediaRecorder;
    let audioChunks = [];

    async function startRecording() {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const reader = new FileReader();
            reader.readAsDataURL(audioBlob);
            reader.onloadend = () => {
                const base64Audio = reader.result;
                window.parent.postMessage({type: 'audio', data: base64Audio}, '*');
            };
        };

        mediaRecorder.start();
        document.getElementById('status').innerText = '🔴 Aufnahme läuft...';
    }

    function stopRecording() {
        mediaRecorder.stop();
        document.getElementById('status').innerText = '✅ Aufnahme beendet';
    }
    </script>

    <div style="text-align: center;">
        <button onclick="startRecording()" style="margin: 10px;">Start</button>
        <button onclick="stopRecording()" style="margin: 10px;">Stop</button>
        <p id="status"></p>
    </div>
    """
    html(html_code, height=200)

# In app.py verwenden:
if st.session_state.recording:
    audio_recorder()
```

### Option B: Datei-Upload

Einfachere Alternative für Tests:

```python
audio_file = st.file_uploader("Audio-Datei hochladen", type=['wav', 'mp3', 'm4a'])
if audio_file:
    # Verarbeitung hier
    st.audio(audio_file)
```

## 2. Whisper API Integration

### Setup

```bash
pip install openai
```

### Code für app.py

```python
import openai
from openai import OpenAI
import os

# API Key aus Streamlit Secrets oder Environment Variable
openai_api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

def transcribe_audio(audio_file):
    """
    Transkribiert Audio-Datei mit Whisper API
    """
    try:
        # Audio-Datei an Whisper API senden
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="de",  # Deutsch
            response_format="text"
        )
        return transcript
    except Exception as e:
        st.error(f"Fehler bei der Transkription: {str(e)}")
        return None

# In app.py verwenden:
if audio_file:
    with st.spinner("Transkription läuft..."):
        transcript = transcribe_audio(audio_file)
        if transcript:
            st.session_state.recorded_data['transcript'] = transcript
```

## 3. GPT-4 Zusammenfassung

### Code für app.py

```python
def generate_medical_summary(transcript, patient_data):
    """
    Generiert medizinische Zusammenfassung mit GPT-4
    """
    try:
        prompt = f"""
Du bist ein medizinischer Assistent. Erstelle eine strukturierte medizinische
Zusammenfassung des folgenden Patientengesprächs.

PATIENTENINFORMATION:
Name: {patient_data.get('vorname')} {patient_data.get('nachname')}
Geburtsdatum: {patient_data.get('geburtsdatum')}
Geschlecht: {patient_data.get('geschlecht')}
Bekannte Allergien: {patient_data.get('allergie', 'Keine')}
Diagnosen: {patient_data.get('diagnosen', 'Keine')}

GESPRÄCHSTRANSKRIPT:
{transcript}

Bitte erstelle eine Zusammenfassung mit folgenden Abschnitten:

1. HAUPTBESCHWERDEN
2. ANAMNESE
3. AKTUELLE BEFUNDE
4. THERAPIEEMPFEHLUNGEN
5. WEITERE MASSNAHMEN

Halte die Zusammenfassung präzise und professionell.
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Du bist ein erfahrener medizinischer Dokumentationsassistent."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )

        summary = response.choices[0].message.content
        return summary

    except Exception as e:
        st.error(f"Fehler bei der Zusammenfassung: {str(e)}")
        return None

# In app.py verwenden:
if transcript:
    with st.spinner("Zusammenfassung wird generiert..."):
        summary = generate_medical_summary(transcript, st.session_state.patient_data)
        if summary:
            st.session_state.recorded_data['summary'] = summary
```

## 4. PDF-Generierung

### Installation

```bash
pip install reportlab
```

### Code für pdf_utils.py

Ersetzen Sie die Platzhalter-Funktionen:

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from io import BytesIO
from datetime import datetime

def generate_medical_pdf(patient_data, summary, transcript):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()

    # Custom Styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=20,
        alignment=1  # Center
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#10b981'),
        spaceAfter=12,
        spaceBefore=12
    )

    story = []

    # Title
    story.append(Paragraph("Medizinische Gesprächszusammenfassung", title_style))
    story.append(Spacer(1, 20))

    # Patient Information Table
    patient_info = [
        ['Patient:', f"{patient_data.get('vorname', '')} {patient_data.get('nachname', '')}"],
        ['Geburtsdatum:', str(patient_data.get('geburtsdatum', ''))],
        ['Geschlecht:', patient_data.get('geschlecht', '')],
        ['Größe:', f"{patient_data.get('groesse', '')} cm"],
        ['Gewicht:', f"{patient_data.get('gewicht', '')} kg"],
        ['Therapiebeginn:', str(patient_data.get('therapiebeginn', ''))],
        ['Dauer:', f"{patient_data.get('dauer', '')} Monate"],
        ['TW besprochen:', patient_data.get('tw_besprochen', '')],
    ]

    if patient_data.get('allergie'):
        patient_info.append(['Allergien:', patient_data.get('allergie')])

    if patient_data.get('diagnosen'):
        patient_info.append(['Diagnosen:', patient_data.get('diagnosen')])

    table = Table(patient_info, colWidths=[4*cm, 11*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    story.append(table)
    story.append(Spacer(1, 30))

    # Summary
    story.append(Paragraph("Zusammenfassung", heading_style))
    for para in summary.split('\n'):
        if para.strip():
            story.append(Paragraph(para.strip(), styles['Normal']))
            story.append(Spacer(1, 6))

    story.append(Spacer(1, 30))

    # Transcript
    story.append(Paragraph("Vollständiges Transkript", heading_style))
    for para in transcript.split('\n'):
        if para.strip():
            story.append(Paragraph(para.strip(), styles['Normal']))
            story.append(Spacer(1, 6))

    # Footer
    story.append(Spacer(1, 30))
    footer_text = f"Erstellt am: {datetime.now().strftime('%d.%m.%Y um %H:%M Uhr')}"
    story.append(Paragraph(footer_text, styles['Italic']))

    doc.build(story)
    buffer.seek(0)
    return buffer
```

### In app.py verwenden:

```python
from pdf_utils import generate_medical_pdf

if st.button("📥 PDF Herunterladen"):
    try:
        pdf_buffer = generate_medical_pdf(
            st.session_state.patient_data,
            st.session_state.recorded_data['summary'],
            st.session_state.recorded_data['transcript']
        )

        st.download_button(
            label="Download PDF",
            data=pdf_buffer,
            file_name=f"patient_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Fehler bei PDF-Generierung: {str(e)}")
```

## 5. Komplette Integration in app.py

Hier ist der vollständige Workflow:

```python
# Nach dem Stop-Button:
if st.button("⏹️ Aufnahme beenden"):
    st.session_state.recording = False

    # 1. Audio verarbeiten
    audio_file = st.session_state.get('audio_file')

    if audio_file:
        # 2. Transkription
        with st.spinner("Transkription läuft..."):
            transcript = transcribe_audio(audio_file)

        # 3. Zusammenfassung generieren
        if transcript:
            with st.spinner("Zusammenfassung wird erstellt..."):
                summary = generate_medical_summary(
                    transcript,
                    st.session_state.patient_data
                )

            # 4. Ergebnisse speichern
            st.session_state.recorded_data = {
                'summary': summary,
                'transcript': transcript,
                'audio_data': audio_file
            }

            st.success("✅ Verarbeitung abgeschlossen!")
            st.rerun()
```

## 6. Secrets-Konfiguration

### Lokal (.streamlit/secrets.toml):

```toml
OPENAI_API_KEY = "sk-..."
```

### Streamlit Cloud:

1. Gehe zu App-Einstellungen
2. Klicke auf "Secrets"
3. Füge hinzu:

```toml
OPENAI_API_KEY = "sk-..."
```

## 7. Error Handling

Fügen Sie robustes Error Handling hinzu:

```python
try:
    # Ihre Funktion
    result = transcribe_audio(audio_file)
except openai.APIError as e:
    st.error(f"OpenAI API Fehler: {e}")
except openai.RateLimitError as e:
    st.error("Rate Limit erreicht. Bitte warten Sie einen Moment.")
except Exception as e:
    st.error(f"Unerwarteter Fehler: {e}")
    import traceback
    st.code(traceback.format_exc())
```

## 8. Testing

Testen Sie jede Komponente einzeln:

```python
# Test-Modus aktivieren
if st.checkbox("Test-Modus"):
    st.subheader("Komponenten-Tests")

    # Audio-Test
    test_audio = st.file_uploader("Test-Audio")
    if test_audio and st.button("Transkription testen"):
        result = transcribe_audio(test_audio)
        st.write(result)

    # Zusammenfassung-Test
    test_text = st.text_area("Test-Text für Zusammenfassung")
    if st.button("Zusammenfassung testen"):
        summary = generate_medical_summary(test_text, {})
        st.write(summary)

    # PDF-Test
    if st.button("PDF testen"):
        pdf = generate_medical_pdf({}, "Test Summary", "Test Transcript")
        st.download_button("Download Test PDF", pdf, "test.pdf")
```

## Nächste Schritte

1. Installieren Sie die erforderlichen Pakete
2. Fügen Sie Ihren OpenAI API-Key hinzu
3. Integrieren Sie die Funktionen Schritt für Schritt
4. Testen Sie jede Komponente einzeln
5. Testen Sie den kompletten Workflow
6. Deployen Sie auf Streamlit Cloud

## Hilfe und Support

- **OpenAI API Docs:** https://platform.openai.com/docs
- **Streamlit Docs:** https://docs.streamlit.io
- **ReportLab Docs:** https://www.reportlab.com/docs/

Bei Fragen oder Problemen erstellen Sie bitte ein Issue im Repository.
