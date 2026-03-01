# Medizinische Gesprächszusammenfassung - Streamlit App

Eine KI-gestützte Streamlit-Anwendung zur Dokumentation von medizinischen Patientengesprächen mit deutscher Benutzeroberfläche.

## Installation

1. Installieren Sie die erforderlichen Abhängigkeiten:

```bash
pip install -r requirements.txt
```

2. Starten Sie die Streamlit-Anwendung:

```bash
streamlit run app.py
```

Die Anwendung wird automatisch in Ihrem Browser unter `http://localhost:8501` geöffnet.

## Funktionen

- **Patientendatenformular**: Vollständige Erfassung von Patienteninformationen
- **Audioaufnahme**: Interface für Gesprächsaufnahmen
- **KI-Zusammenfassung**: Platzhalter für Whisper API-Integration
- **Transkription**: Vollständiges Gesprächstranskript
- **PDF-Export**: Exportfunktion für Dokumentation
- **Moderne UI**: Farbenfrohe, professionelle Benutzeroberfläche

## Backend-Integration

### 1. Audio-Aufnahme

Integrieren Sie Ihre Audio-Aufnahme-Logik in der Funktion `start_recording`:

```python
import sounddevice as sd
import soundfile as sf
import numpy as np

# In app.py, ersetzen Sie die Aufnahme-Funktionalität:
if st.button("🎤 Aufnahme starten"):
    # Ihre Audio-Aufnahme-Logik hier
    duration = 60  # Sekunden
    fs = 44100
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    # Speichern Sie die Aufnahme
```

### 2. Whisper API-Integration

Fügen Sie die Whisper API-Integration hinzu:

```python
import openai
# oder
from whisper import load_model

def transcribe_audio(audio_file):
    # OpenAI Whisper API
    client = openai.OpenAI()
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    return transcript.text

# Oder lokales Whisper-Modell
def transcribe_local(audio_file):
    model = load_model("base")
    result = model.transcribe(audio_file)
    return result["text"]
```

### 3. KI-Zusammenfassung

Implementieren Sie die Zusammenfassungs-Logik:

```python
from openai import OpenAI

def generate_summary(transcript, patient_data):
    client = OpenAI()

    prompt = f"""
    Erstelle eine medizinische Zusammenfassung des folgenden Patientengesprächs:

    Patient: {patient_data['vorname']} {patient_data['nachname']}

    Transkript:
    {transcript}

    Bitte erstelle eine strukturierte Zusammenfassung mit:
    - Hauptbeschwerden
    - Anamnese
    - Befunde
    - Empfehlungen
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
```

### 4. PDF-Generierung

Implementieren Sie die PDF-Export-Funktionalität:

```python
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

def generate_pdf(patient_data, summary, transcript):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    story = []

    # Titel
    story.append(Paragraph("Medizinische Gesprächszusammenfassung", styles['Title']))
    story.append(Spacer(1, 12))

    # Patientendaten
    story.append(Paragraph(f"Patient: {patient_data['vorname']} {patient_data['nachname']}", styles['Normal']))
    story.append(Paragraph(f"Geburtsdatum: {patient_data['geburtsdatum']}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Zusammenfassung
    story.append(Paragraph("Zusammenfassung:", styles['Heading2']))
    story.append(Paragraph(summary, styles['Normal']))
    story.append(Spacer(1, 12))

    # Transkript
    story.append(Paragraph("Vollständiges Transkript:", styles['Heading2']))
    story.append(Paragraph(transcript, styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer

# In app.py:
if st.button("📥 PDF Herunterladen"):
    pdf_buffer = generate_pdf(
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
```

## Deployment auf Streamlit Cloud

1. Pushen Sie Ihren Code zu GitHub
2. Gehen Sie zu [share.streamlit.io](https://share.streamlit.io)
3. Verbinden Sie Ihr GitHub-Repository
4. Wählen Sie `app.py` als Hauptdatei
5. Deployen Sie die Anwendung

## Umgebungsvariablen

Fügen Sie Ihre API-Keys in Streamlit Cloud hinzu:

```
OPENAI_API_KEY=your_api_key_here
```

## Datenschutz und Sicherheit

- Verwenden Sie HTTPS für alle Produktions-Deployments
- Speichern Sie keine sensiblen Patientendaten unverschlüsselt
- Implementieren Sie Authentifizierung für Produktionsumgebungen
- Folgen Sie DSGVO- und HIPAA-Richtlinien für medizinische Daten

## Support

Für Fragen und Support kontaktieren Sie bitte Ihren Systemadministrator.
