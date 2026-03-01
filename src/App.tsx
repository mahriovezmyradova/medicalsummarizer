import React, { useState } from 'react';
import PatientForm from './components/PatientForm';
import RecordingButton from './components/RecordingButton';
import ResultsDisplay from './components/ResultsDisplay';

interface PatientData {
  vorname: string;
  nachname: string;
  geburtsdatum: string;
  geschlecht: 'M' | 'W' | '';
  groesse: number;
  gewicht: number;
  therapiebeginn: string;
  dauer: number;
  twBesprochen: 'ja' | 'nein' | '';
  allergie: string;
  diagnosen: string;
}

interface RecordingData {
  audioBlob: Blob | null;
  audioUrl: string;
  summary: string;
  transcript: string;
}

function App() {
  const [patientData, setPatientData] = useState<PatientData>({
    vorname: '',
    nachname: '',
    geburtsdatum: '',
    geschlecht: '',
    groesse: 170,
    gewicht: 70,
    therapiebeginn: '',
    dauer: 1,
    twBesprochen: '',
    allergie: '',
    diagnosen: '',
  });

  const [isRecording, setIsRecording] = useState(false);
  const [recordingData, setRecordingData] = useState<RecordingData | null>(null);
  const [showTranscript, setShowTranscript] = useState(false);

  const handleStartRecording = async () => {
    setIsRecording(true);
  };

  const handleStopRecording = async () => {
    setIsRecording(false);

    const mockAudioBlob = new Blob([], { type: 'audio/webm' });
    setRecordingData({
      audioBlob: mockAudioBlob,
      audioUrl: '',
      summary: 'Die Zusammenfassung wird hier angezeigt, sobald die Aufnahme verarbeitet wurde...',
      transcript: 'Das vollständige Transkript wird hier angezeigt...',
    });
  };

  const handleDownloadPDF = () => {
    console.log('PDF Download wird generiert...');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-emerald-50 to-cyan-50 relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(59,130,246,0.1),transparent_50%),radial-gradient(circle_at_70%_80%,rgba(16,185,129,0.1),transparent_50%)]" />

      <div className="max-w-5xl mx-auto px-6 py-12 relative z-10">
        <header className="mb-12 text-center">
          <div className="inline-block mb-4 px-4 py-2 bg-gradient-to-r from-blue-500 to-emerald-500 rounded-full">
            <div className="flex items-center gap-2 text-white">
              <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
              <span className="text-sm font-medium">KI-Powered</span>
            </div>
          </div>
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 via-emerald-600 to-cyan-600 bg-clip-text text-transparent mb-3">
            Medizinische Gesprächszusammenfassung
          </h1>
          <p className="text-slate-600 text-lg">
            Intelligente Dokumentation für Patientengespräche
          </p>
        </header>

        <div className="space-y-6">
          <PatientForm
            patientData={patientData}
            setPatientData={setPatientData}
          />

          <RecordingButton
            isRecording={isRecording}
            onStartRecording={handleStartRecording}
            onStopRecording={handleStopRecording}
          />

          {recordingData && (
            <ResultsDisplay
              recordingData={recordingData}
              showTranscript={showTranscript}
              setShowTranscript={setShowTranscript}
              onDownloadPDF={handleDownloadPDF}
              patientData={patientData}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
