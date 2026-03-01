# Quick Reference - Medizinische Gesprächszusammenfassung

## 🚀 Schnellstart in 30 Sekunden

```bash
# Option 1: Automatisch
./run.sh          # Linux/Mac
run.bat           # Windows

# Option 2: Manuell
pip install -r requirements.txt
streamlit run app.py
```

→ Öffne http://localhost:8501

## 📂 Wichtige Dateien

| Datei | Zweck |
|-------|-------|
| `app.py` | Haupt-Streamlit-App (Frontend fertig) |
| `audio_utils.py` | Audio-Funktionen (Backend TODO) |
| `pdf_utils.py` | PDF-Funktionen (Backend TODO) |
| `requirements.txt` | Python-Abhängigkeiten |

## 🔧 Backend-Integration (3 Schritte)

### 1. API-Key setzen

```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "sk-..."
```

### 2. Whisper integrieren

```python
import openai
client = openai.OpenAI()

transcript = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    language="de"
)
```

### 3. GPT-4 Zusammenfassung

```python
summary = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": f"Fasse zusammen: {transcript}"}]
)
```

## 📝 Was ist fertig?

✅ Komplettes UI-Design
✅ Alle Formularfelder
✅ Patientendaten-Management
✅ Recording-Interface
✅ Ergebnisanzeige
✅ PDF-Download-Button
✅ Responsive Design
✅ Moderne Farben & Animationen

## ⚙️ Was fehlt noch?

❌ Audio-Aufnahme-Logik
❌ Whisper API-Anbindung
❌ GPT-4 Integration
❌ PDF-Generierung
❌ Datenbank (optional)

## 📚 Wo finde ich was?

- **Erste Schritte** → `GETTING_STARTED.md`
- **Backend-Integration** → `INTEGRATION_GUIDE.md`
- **Deployment** → `DEPLOYMENT.md`
- **Projekt-Übersicht** → `README.md`

## 🎯 Formular-Felder

Alle Felder sind implementiert:
- ✅ Vor- und Nachname
- ✅ Geburtsdatum (Kalender ab 1900)
- ✅ Geschlecht (M/W)
- ✅ Größe mit +/- Buttons
- ✅ Gewicht mit +/- Buttons
- ✅ Therapiebeginn (Kalender)
- ✅ Dauer (1-12 Monate)
- ✅ TW besprochen (Ja/Nein)
- ✅ Allergien
- ✅ Diagnosen

## 🎨 Design-Features

- Gradient-Hintergründe (Blau/Grün/Cyan)
- Glassmorphismus-Effekte
- Glowing Record-Button
- Smooth Animationen
- Colorful Info-Cards
- Mobile-responsive

## 🌐 Deployment auf Streamlit Cloud

1. Push zu GitHub
2. Gehe zu share.streamlit.io
3. Verbinde Repository
4. Deploy!

**Fertig!** 🎉

## 💰 Kosten-Schätzung

| Service | Kosten |
|---------|--------|
| Streamlit Cloud | Kostenlos |
| Whisper API | $0.006/Minute |
| GPT-4 | $0.03/1K Tokens |

**Beispiel:** 10-Min-Gespräch ≈ $0.26

## 🔐 Sicherheit

```python
# ✅ Richtig - Secrets verwenden
api_key = st.secrets["OPENAI_API_KEY"]

# ❌ Falsch - Nie im Code!
api_key = "sk-..."
```

## 🐛 Debug-Tipps

```python
# Session State anzeigen
st.write(st.session_state)

# Performance messen
import time
start = time.time()
# ... code ...
st.write(f"Dauer: {time.time() - start:.2f}s")

# Errors loggen
import logging
logging.error("Fehler", exc_info=True)
```

## 📦 Abhängigkeiten installieren

```bash
# Minimal (App starten)
pip install streamlit python-dateutil

# Vollständig (mit Backend)
pip install streamlit openai reportlab sounddevice soundfile

# Aus Datei
pip install -r requirements.txt
```

## 🎤 Audio-Integration

### Option A: File Upload (Einfach)

```python
audio_file = st.file_uploader("Audio", type=['wav', 'mp3'])
```

### Option B: Browser Recording (Erweitert)

Siehe `INTEGRATION_GUIDE.md` für JavaScript-Integration

## 📄 PDF-Export

```python
from pdf_utils import generate_medical_pdf

pdf = generate_medical_pdf(
    patient_data,
    summary,
    transcript
)

st.download_button(
    "Download PDF",
    pdf,
    "patient.pdf",
    "application/pdf"
)
```

## 🔍 Häufige Probleme

**Problem:** Streamlit nicht gefunden
```bash
pip install streamlit
```

**Problem:** Port bereits belegt
```bash
streamlit run app.py --server.port 8502
```

**Problem:** Secrets nicht gefunden
```bash
# Erstelle .streamlit/secrets.toml
mkdir -p .streamlit
echo 'OPENAI_API_KEY = "sk-..."' > .streamlit/secrets.toml
```

## 📞 Support

- 📚 Streamlit Docs: docs.streamlit.io
- 🤖 OpenAI Docs: platform.openai.com/docs
- 💬 Forum: discuss.streamlit.io

## ✅ Checkliste

- [ ] App lokal gestartet
- [ ] Formular getestet
- [ ] Dokumentation gelesen
- [ ] API-Key eingerichtet
- [ ] Whisper integriert
- [ ] GPT-4 integriert
- [ ] PDF-Export implementiert
- [ ] Getestet mit echten Daten
- [ ] Auf Streamlit Cloud deployed
- [ ] Produktionsbereit

## 🎉 Sie sind bereit!

Die App ist **produktionsfertig** als Frontend. Integrieren Sie jetzt Ihr Backend mit den Guides!

**Viel Erfolg!** 🚀
