"""
Audio recording and processing utilities.
"""

import io
from typing import Optional, Dict, Any
import streamlit as st

# Optional: For OpenAI API
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def record_audio(duration: int = 60, sample_rate: int = 44100) -> bytes:
    """
    Record audio from the microphone.
    
    Note: In Streamlit, we use st.audio_input() instead of this function.
    This is kept for compatibility.
    """
    # This is a placeholder - we actually use st.audio_input() in the app
    return b""


def transcribe_with_whisper(audio_bytes, api_key: Optional[str] = None) -> str:
    """
    Transcribe audio using OpenAI Whisper API.
    
    Args:
        audio_bytes: Audio data from st.audio_input()
        api_key: OpenAI API key (optional)
    
    Returns:
        Transcribed text
    """
    if audio_bytes is None:
        return ""
    
    # Try OpenAI API if available
    if OPENAI_AVAILABLE:
        try:
            return _transcribe_with_openai(audio_bytes, api_key)
        except Exception as e:
            st.warning(f"OpenAI transcription failed: {e}")
            return _get_mock_transcript()
    else:
        # Mock transcription for development
        return _get_mock_transcript()


def _transcribe_with_openai(audio_bytes, api_key: Optional[str] = None) -> str:
    """Transcribe using OpenAI API."""
    # Get API key from secrets if not provided
    if api_key is None:
        api_key = st.secrets.get("OPENAI_API_KEY", None)
    
    if not api_key:
        return _get_mock_transcript()
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Create a file-like object from bytes
        audio_file = io.BytesIO(audio_bytes.getvalue())
        audio_file.name = "recording.webm"
        
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="de"
        )
        
        return transcript.text
    except Exception as e:
        st.error(f"Fehler bei der Transkription: {e}")
        return _get_mock_transcript()


def _get_mock_transcript() -> str:
    """Return a mock transcript for development."""
    return """
Arzt: Guten Tag Herr Mustermann, was führt Sie heute zu mir?

Patient: Guten Tag Herr Doktor, ich habe seit einigen Wochen immer wieder Kopfschmerzen und bin sehr müde.

Arzt: Wo genau treten die Kopfschmerzen auf?

Patient: Hauptsächlich im Stirnbereich, manchmal auch im Nacken.

Arzt: Haben Sie bereits etwas dagegen unternommen?

Patient: Ich habe es mit Schmerztabletten versucht, aber die helfen nur kurz.

Arzt: Wie ist Ihr Schlaf?

Patient: Nicht gut, ich wache oft nachts auf und finde dann nicht mehr in den Schlaf.

Arzt: Und wie sieht es mit Stress aus?

Patient: Ja, im Beruf ist gerade viel los, das könnte vielleicht damit zusammenhängen.

Arzt: Wir sollten auf jeden Fall Ihre Blutwerte überprüfen und vielleicht auch ein MRT des Kopfes machen, um organische Ursachen auszuschließen.

Patient: Das klingt gut. Was empfehlen Sie bis dahin?

Arzt: Ich verschreibe Ihnen erstmal ein leichtes Schmerzmittel und etwas zur Entspannung. Außerdem wäre es gut, wenn Sie ein Schlaftagebuch führen.

Patient: Vielen Dank, das mache ich.

Arzt: Bitte kommen Sie in zwei Wochen wieder zur Kontrolle, dann haben wir die Ergebnisse.

Patient: Ja, gerne. Auf Wiedersehen.

Arzt: Auf Wiedersehen und gute Besserung.
"""


def generate_summary_with_gpt(
    transcript: str,
    patient_data: Dict[str, Any],
    api_key: Optional[str] = None
) -> str:
    """
    Generate a medical summary using GPT.
    """
    if not OPENAI_AVAILABLE:
        return _get_mock_summary(patient_data)
    
    try:
        # Get API key from secrets if not provided
        if api_key is None:
            api_key = st.secrets.get("OPENAI_API_KEY", None)
        
        if not api_key:
            return _get_mock_summary(patient_data)
        
        client = OpenAI(api_key=api_key)
        
        patient_name = f"{patient_data.get('vorname', '')} {patient_data.get('nachname', '')}".strip()
        if not patient_name:
            patient_name = "Patient/in"
        
        diagnoses = patient_data.get('diagnosen', 'Keine angegeben')
        if not diagnoses:
            diagnoses = "Keine angegeben"
        
        prompt = f"""
        Erstelle eine strukturierte medizinische Zusammenfassung des folgenden Patientengesprächs auf Deutsch.
        
        Patient: {patient_name}
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
            model="gpt-3.5-turbo",  # Using gpt-3.5-turbo instead of gpt-4 for better availability
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        st.error(f"Fehler bei der Zusammenfassung: {e}")
        return _get_mock_summary(patient_data)


def _get_mock_summary(patient_data: Dict[str, Any]) -> str:
    """Generate a mock summary for development."""
    patient_name = f"{patient_data.get('vorname', '')} {patient_data.get('nachname', '')}".strip()
    if not patient_name:
        patient_name = "Patient/in"
    
    return f"""
**Medizinische Zusammenfassung**

**1. Hauptbeschwerden**
{patient_name} berichtet über seit Wochen anhaltende Kopfschmerzen im Stirn- und Nackenbereich sowie ausgeprägte Müdigkeit. Schlafstörungen mit nächtlichem Erwachen werden ebenfalls angegeben.

**2. Anamnese**
Eigenmedikation mit Schmerzmitteln zeigt nur kurzfristige Besserung. Beruflicher Stress wird als möglicher Auslöser genannt. Keine Vorerkrankungen bekannt.

**3. Aktuelle Befunde**
- Blutdruck: 125/85 mmHg (gemessen in der Praxis)
- Puls: 72 Schläge/min
- Neurologischer Status: unauffällig
- Labor: Blutentnahme wurde veranlasst (Ergebnisse stehen aus)
- cMRT Kopf: wurde zur weiteren Abklärung veranlasst

**4. Therapieempfehlungen**
- Leichtes Analgetikum bei Bedarf
- Entspannungsübungen
- Schlafhygiene verbessern
- Führen eines Schlaftagebuchs

**5. Weitere Maßnahmen**
- Wiedervorstellung in 2 Wochen zur Befundbesprechung
- Bei Verschlechterung sofortige Vorstellung
- Stressreduktion im Alltag empfohlen

*Diese Zusammenfassung wurde automatisch generiert und muss von einem Arzt überprüft werden.*
"""
