# Deployment-Anleitung für Streamlit

## Schnellstart (Lokal)

1. **Installation der Abhängigkeiten:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Anwendung starten:**
   ```bash
   streamlit run app.py
   ```

3. **Zugriff:**
   - Die App öffnet sich automatisch im Browser
   - Oder manuell: http://localhost:8501

## Deployment auf Streamlit Cloud

### Schritt 1: Repository vorbereiten

1. Erstellen Sie ein GitHub-Repository
2. Pushen Sie folgende Dateien:
   - `app.py`
   - `requirements.txt`
   - `audio_utils.py` (optional)
   - `pdf_utils.py` (optional)

### Schritt 2: Streamlit Cloud Setup

1. Gehen Sie zu [share.streamlit.io](https://share.streamlit.io)
2. Klicken Sie auf "New app"
3. Verbinden Sie Ihr GitHub-Konto
4. Wählen Sie Ihr Repository aus
5. Konfigurieren Sie:
   - **Main file path:** `app.py`
   - **Python version:** 3.11
   - **Branch:** main

### Schritt 3: Umgebungsvariablen setzen

In den App-Einstellungen unter "Secrets" fügen Sie hinzu:

```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "your-api-key-here"

# Optional: Weitere Konfigurationen
[audio]
sample_rate = 44100
max_duration = 600

[pdf]
company_name = "Ihre Praxis"
logo_path = "path/to/logo.png"
```

### Schritt 4: Deploy

1. Klicken Sie auf "Deploy"
2. Warten Sie, bis die App gebaut ist (2-3 Minuten)
3. Die App ist jetzt live unter: `https://your-app-name.streamlit.app`

## Erweiterte Konfiguration

### .streamlit/config.toml

Erstellen Sie eine Datei `.streamlit/config.toml` für benutzerdefinierte Einstellungen:

```toml
[theme]
primaryColor = "#10b981"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f9ff"
textColor = "#1e293b"
font = "sans serif"

[server]
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

## Sicherheit und Datenschutz

### Authentifizierung hinzufügen

Für Produktionsumgebungen sollten Sie Authentifizierung implementieren:

```python
import streamlit as st
import hmac

def check_password():
    """Returns True if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.text_input(
        "Passwort", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Passwort falsch")
    return False

if not check_password():
    st.stop()

# Rest der App hier...
```

### Datenbank-Integration (Optional)

Für persistente Speicherung verwenden Sie Supabase:

```python
from supabase import create_client, Client

url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

# Patientendaten speichern
def save_patient_data(data):
    response = supabase.table("patients").insert(data).execute()
    return response

# Aufnahme speichern
def save_recording(audio_data, patient_id):
    # Upload zu Supabase Storage
    response = supabase.storage.from_("recordings").upload(
        f"{patient_id}/recording.wav",
        audio_data
    )
    return response
```

## Performance-Optimierung

### Caching verwenden

```python
@st.cache_data
def load_model():
    # Laden Sie ML-Modelle nur einmal
    import whisper
    return whisper.load_model("base")

@st.cache_data
def transcribe_audio(audio_path):
    model = load_model()
    return model.transcribe(audio_path)
```

### Ressourcen-Limits

Streamlit Cloud bietet:
- 1 GB RAM
- 1 CPU
- 1 GB Storage

Für größere Anforderungen:
- Upgrade zu Streamlit Cloud Pro
- Oder deployment auf eigener Infrastruktur (AWS, GCP, Azure)

## Monitoring und Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In Ihrer App
logger.info("Recording started")
logger.error("Transcription failed", exc_info=True)
```

## Troubleshooting

### App startet nicht

1. Überprüfen Sie `requirements.txt`
2. Schauen Sie in die Logs auf Streamlit Cloud
3. Testen Sie lokal mit `streamlit run app.py`

### Langsame Performance

1. Nutzen Sie `@st.cache_data` für teure Operationen
2. Reduzieren Sie die Größe von Session State
3. Optimieren Sie Audio-Dateien (komprimieren)

### Audio funktioniert nicht

1. Browser-Berechtigungen prüfen
2. HTTPS erforderlich für Mikrofon-Zugriff
3. Testen Sie mit verschiedenen Browsern

## Support und Ressourcen

- **Streamlit Docs:** https://docs.streamlit.io
- **Community Forum:** https://discuss.streamlit.io
- **GitHub Issues:** Ihr Repository

## Kosten

- **Streamlit Community Cloud:** Kostenlos
- **Streamlit Cloud Pro:** Ab $20/Monat
- **OpenAI API:** Pay-per-use (Whisper ca. $0.006/Minute)

## Backup und Updates

### Automatische Updates

Bei jedem Push zu GitHub wird die App automatisch neu deployed.

### Rollback

In Streamlit Cloud können Sie zu früheren Versionen zurückkehren:
1. Gehe zu App-Einstellungen
2. Wähle "Reboot app"
3. Oder deploye einen früheren Git-Commit

## Nächste Schritte

1. Implementieren Sie die Audio-Aufnahme-Funktionalität
2. Integrieren Sie Whisper API für Transkription
3. Fügen Sie PDF-Generierung hinzu
4. Implementieren Sie Datenbankanbindung
5. Fügen Sie Authentifizierung hinzu
6. Testen Sie die Anwendung gründlich
7. Deployen Sie auf Streamlit Cloud
