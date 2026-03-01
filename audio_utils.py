"""
Audio recording and processing utilities.
"""

import io
from typing import Optional, Dict, Any
import streamlit as st

# Optional: For local Whisper
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

# Optional: For OpenAI API
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def transcribe_with_whisper(audio_bytes: bytes, api_key: Optional[str] = None) -> str:
    """
    Transcribe audio using OpenAI Whisper API or local model.
    
    Args:
        audio_bytes: Audio data in bytes
        api_key: OpenAI API key (optional)
    
    Returns:
        Transcribed text
    """
    # Try OpenAI API first if API key is available
    if api_key or (api_key is None and OPENAI_AVAILABLE):
        try:
            return _transcribe_with_openai(audio_bytes, api_key)
        except Exception as e:
            st.warning(f"OpenAI transcription failed: {e}. Trying local model...")
    
    # Fallback to local Whisper
    if WHISPER_AVAILABLE:
        try:
            return _transcribe_local(audio_bytes)
        except Exception as e:
            st.error(f"Local transcription failed: {e}")
            return "Transkription fehlgeschlagen."
    
    # Mock transcription for development
    return "Dies ist ein Platzhalter für das transkribierte Gespräch. In der Produktion wird hier die echte Transkription erscheinen."


def _transcribe_with_openai(audio_bytes: bytes, api_key: Optional[str] = None) -> str:
    """Transcribe using OpenAI API."""
    client = OpenAI(api_key=api_key)
    
    # Create a file-like object from bytes
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "recording.webm"
    
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="de"
    )
    
    return transcript.text


def _transcribe_local(audio_bytes: bytes) -> str:
    """Transcribe using local Whisper model."""
    # Save bytes to temporary file
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp_file:
        tmp_file.write(audio_bytes)
        tmp_path = tmp_file.name
    
    try:
        model = whisper.load_model("base")
        result = model.transcribe(tmp_path, language="de")
        return result["text"]
    finally:
        # Clean up temp file
        os.unlink(tmp_path)


def generate_summary_with_gpt(
    transcript: str,
    patient_data: Dict[str, Any],
    api_key: Optional[str] = None
) -> str:
    """
    Generate a medical summary using GPT.
    """
    if not OPENAI_AVAILABLE:
        # Mock summary for development
        return _generate_mock_summary(transcript, patient_data)
    
    try:
        client = OpenAI(api_key=api_key)
        
        patient_name = f"{patient_data.get('vorname', '')} {patient_data.get('nachname', '')}".strip()
        diagnoses = patient_data.get('diagnosen', 'Keine angegeben')
        
        prompt = f"""
        Erstelle eine strukturierte medizinische Zusammenfassung des folgenden Patientengesprächs auf Deutsch.
        
        Patient: {patient_name or 'Unbekannt'}
        Diagnosen: {diagnoses}
        
        Gesprächstranskript:
        {transcript}
        
        Bitte erstelle eine Zusammenfassung mit folgenden Abschnitten:
        1. Hauptbeschwerden
        2. Anamnese
        3. Aktuelle Befunde
        4. Therapieempfehlungen
        5. Weitere Maßnahmen
        
        Halte die Zusammenfassung professionell und präzise.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        st.error(f"Fehler bei der Zusammenfassung: {e}")
        return _generate_mock_summary(transcript, patient_data)


def _generate_mock_summary(transcript: str, patient_data: Dict[str, Any]) -> str:
    """Generate a mock summary for development."""
    patient_name = f"{patient_data.get('vorname', '')} {patient_data.get('nachname', '')}".strip()
    
    return f"""
    **Zusammenfassung des Patientengesprächs**
    
    **1. Hauptbeschwerden**
    Der Patient {patient_name or 'Unbekannt'} berichtet über aktuelle gesundheitliche Probleme.
    
    **2. Anamnese**
    Im Gespräch wurden die bisherigen Erkrankungen und Behandlungen besprochen.
    
    **3. Aktuelle Befunde**
    Die aktuellen Befunde wurden dokumentiert und besprochen.
    
    **4. Therapieempfehlungen**
    Folgende Therapie wird empfohlen:
    - Regelmäßige Kontrollen
    - Anpassung der Medikation
    - Weitere Diagnostik bei Bedarf
    
    **5. Weitere Maßnahmen**
    - Nächster Termin in 4 Wochen
    - Bei Verschlechterung sofort melden
    
    *Diese Zusammenfassung wurde automatisch generiert und muss von einem Arzt überprüft werden.*
    """
