# 🏥 Medizinische Gesprächszusammenfassung

Eine professionelle, KI-gestützte Streamlit-Anwendung zur Dokumentation von medizinischen Patientengesprächen mit deutscher Benutzeroberfläche.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

### 📋 Patientendaten-Erfassung
- Vollständiges deutsches Formular
- Vor- und Nachname
- Geburtsdatum (Kalender ab 1900)
- Geschlecht (Männlich/Weiblich)
- Größe mit +/- Regulatoren
- Gewicht mit +/- Regulatoren
- Therapiebeginn (Kalender)
- Therapiedauer (1-12 Monate)
- TW-Status (Ja/Nein)
- Allergien und Diagnosen

### 🎤 Audio-Aufnahme
- Intuitive Aufnahme-Steuerung
- Visuelles Feedback während Aufnahme
- Glowing-Animation im Recording-Modus
- Bereit für Browser-Audio-API oder File-Upload

### 🤖 KI-Integration (Backend)
- Vorbereitet für Whisper API (Transkription)
- Vorbereitet für GPT-4 (Zusammenfassung)
- Strukturierte medizinische Dokumentation

### 📄 Export-Funktionen
- PDF-Download der Zusammenfassung
- Vollständiges Transkript
- Audio-Wiedergabe

### 🎨 Modernes Design
- Farbenfrohe Gradient-Hintergründe
- Glassmorphismus-Effekte
- Smooth Animationen
- Mobile-responsive
- Production-ready UI

## 🚀 Schnellstart

### Option 1: Automatisch (Empfohlen)

**Linux/Mac:**
```bash
./run.sh
```

**Windows:**
```bash
run.bat
```

### Option 2: Manuell

```bash
# 1. Abhängigkeiten installieren
pip install -r requirements.txt

# 2. App starten
streamlit run app.py
```

Die App öffnet sich automatisch unter `http://localhost:8501`

## 📦 Installation

### Voraussetzungen
- Python 3.8 oder höher
- pip (Python Package Manager)

### Abhängigkeiten
```bash
pip install -r requirements.txt
```

Hauptabhängigkeiten:
- `streamlit` - Web-Framework
- `reportlab` - PDF-Generierung
- `python-dateutil` - Datums-Handling

Optional (für Backend-Integration):
- `openai` - Whisper & GPT-4 API
- `sounddevice` - Audio-Aufnahme
- `soundfile` - Audio-Verarbeitung

## 🔧 Backend-Integration

Die App ist als vollständiges Frontend bereit. Für die Backend-Integration siehe:

### Detaillierte Guides
1. **[GETTING_STARTED.md](GETTING_STARTED.md)** - Erste Schritte und Übersicht
2. **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - Schritt-für-Schritt Backend-Integration
3. **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment auf Streamlit Cloud

### Quick Integration

```python
# In app.py nach dem Stop-Button:

import openai
client = openai.OpenAI(api_key="YOUR_KEY")

# 1. Whisper-Transkription
transcript = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    language="de"
)

# 2. GPT-4 Zusammenfassung
summary = client.chat.completions.create(
    model="gpt-4",
    messages=[{
        "role": "user",
        "content": f"Medizinische Zusammenfassung: {transcript}"
    }]
)

# 3. Ergebnisse speichern
st.session_state.recorded_data = {
    'summary': summary.choices[0].message.content,
    'transcript': transcript,
    'audio_data': audio_file
}
```

Vollständige Code-Beispiele in `INTEGRATION_GUIDE.md`

## 📁 Projektstruktur

```
├── app.py                      # 🎯 Haupt-Streamlit-Anwendung
├── audio_utils.py              # 🎤 Audio-Verarbeitungs-Funktionen
├── pdf_utils.py                # 📄 PDF-Generierungs-Funktionen
├── requirements.txt            # 📦 Python-Abhängigkeiten
├── .streamlit/
│   └── config.toml            # ⚙️ Streamlit-Konfiguration
├── run.sh                      # 🚀 Start-Script (Linux/Mac)
├── run.bat                     # 🚀 Start-Script (Windows)
├── README.md                   # 📖 Diese Datei
├── GETTING_STARTED.md         # 🎓 Erste Schritte
├── INTEGRATION_GUIDE.md       # 🔧 Backend-Integration
└── DEPLOYMENT.md              # 🌐 Deployment-Anleitung
```

## 🎨 Screenshots

### Patientenformular
Alle erforderlichen Felder mit modernem Design und intuitiver Bedienung.

### Aufnahme-Interface
Großer, auffälliger Record-Button mit Glowing-Animation während der Aufnahme.

### Ergebnisanzeige
Strukturierte Darstellung von Zusammenfassung, Patientendaten und Transkript mit farbigen Info-Karten.

## 🌐 Deployment

### Streamlit Cloud (Kostenlos)

1. **Repository erstellen**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Auf Streamlit Cloud deployen**
   - Gehe zu [share.streamlit.io](https://share.streamlit.io)
   - Verbinde dein GitHub-Repository
   - Wähle `app.py` als Hauptdatei
   - Deploy!

3. **Secrets konfigurieren**
   - In App-Einstellungen → Secrets
   - Füge API-Keys hinzu:
   ```toml
   OPENAI_API_KEY = "sk-..."
   ```

Siehe `DEPLOYMENT.md` für ausführliche Anleitung.

## 🔐 Sicherheit

### API-Keys
- **Niemals** API-Keys im Code hart-codieren
- Nutze Streamlit Secrets oder Environment Variables
- Lokale Entwicklung: `.streamlit/secrets.toml`
- Production: Streamlit Cloud Secrets

### Datenschutz
- App speichert keine Daten automatisch
- Implementiere Verschlüsselung für Produktionsumgebung
- Folge DSGVO-Richtlinien für medizinische Daten
- Nutze HTTPS für alle Deployments

## 💰 Kosten

### Development (Kostenlos)
- Streamlit Community Cloud: **Kostenlos**
- Lokale Entwicklung: **Kostenlos**

### Production (Pay-per-Use)
- OpenAI Whisper API: ~**$0.006/Minute**
- OpenAI GPT-4: ~**$0.03/1K Tokens**

**Beispiel:** 10-Minuten-Gespräch ≈ $0.26

## 🛠️ Entwicklung

### Debug-Modus
```python
if st.checkbox("🐛 Debug"):
    st.write(st.session_state)
```

### Lokale Entwicklung
```bash
# Auto-reload bei Änderungen
streamlit run app.py --server.runOnSave true
```

### Tests
```bash
# Komponenten einzeln testen
python -m pytest tests/
```

## 📚 Dokumentation

| Datei | Beschreibung |
|-------|-------------|
| **README.md** | Projekt-Übersicht (diese Datei) |
| **GETTING_STARTED.md** | Erste Schritte und Quick Guide |
| **INTEGRATION_GUIDE.md** | Detaillierte Backend-Integration |
| **DEPLOYMENT.md** | Deployment-Anleitung |
| **README_STREAMLIT.md** | Ausführliche Projekt-Dokumentation |

## 🤝 Support

### Ressourcen
- 📚 [Streamlit Dokumentation](https://docs.streamlit.io)
- 🤖 [OpenAI API Docs](https://platform.openai.com/docs)
- 💬 [Streamlit Community Forum](https://discuss.streamlit.io)

### Häufige Fragen

**Q: Funktioniert die Audio-Aufnahme?**
A: Das UI ist fertig. Backend-Integration siehe `INTEGRATION_GUIDE.md`

**Q: Brauche ich OpenAI API?**
A: Nein zum Testen. Ja für Whisper/GPT-4 in Production.

**Q: Ist es DSGVO-konform?**
A: Die App ist vorbereitet. Sie müssen Verschlüsselung und Datenschutz selbst implementieren.

**Q: Kostet Streamlit Cloud etwas?**
A: Community Cloud ist kostenlos für Public Apps.

## 🎯 Nächste Schritte

1. ✅ **Jetzt:** App lokal starten
   ```bash
   ./run.sh  # oder run.bat
   ```

2. 📖 **Heute:** Dokumentation lesen
   - Start: `GETTING_STARTED.md`
   - Integration: `INTEGRATION_GUIDE.md`

3. 🔧 **Diese Woche:** Backend integrieren
   - Whisper API
   - GPT-4 Zusammenfassung
   - PDF-Export

4. 🚀 **Nächste Woche:** Deployment
   - Push zu GitHub
   - Deploy auf Streamlit Cloud

## 📝 Lizenz

MIT License - Frei verwendbar für private und kommerzielle Projekte.

## 🙏 Credits

Erstellt mit:
- [Streamlit](https://streamlit.io) - Web Framework
- [OpenAI](https://openai.com) - Whisper & GPT-4
- [ReportLab](https://www.reportlab.com) - PDF-Generierung

---

**Viel Erfolg mit Ihrer medizinischen KI-Anwendung!** 🏥��

Bei Fragen schauen Sie in die Dokumentation oder erstellen Sie ein Issue.
