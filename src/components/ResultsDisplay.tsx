import React, { useRef, useEffect, useState } from 'react';
import { Download, FileText, Volume2, ChevronDown, ChevronUp } from 'lucide-react';

interface RecordingData {
  audioBlob: Blob | null;
  audioUrl: string;
  summary: string;
  transcript: string;
}

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

interface ResultsDisplayProps {
  recordingData: RecordingData;
  showTranscript: boolean;
  setShowTranscript: (show: boolean) => void;
  onDownloadPDF: () => void;
  patientData: PatientData;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({
  recordingData,
  showTranscript,
  setShowTranscript,
  onDownloadPDF,
  patientData,
}) => {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [audioUrl, setAudioUrl] = useState<string>('');

  useEffect(() => {
    if (recordingData.audioBlob) {
      const url = URL.createObjectURL(recordingData.audioBlob);
      setAudioUrl(url);
      return () => URL.revokeObjectURL(url);
    }
  }, [recordingData.audioBlob]);

  const formatDate = (dateString: string) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('de-DE');
  };

  return (
    <div className="space-y-6">
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8 transform transition-all duration-300 hover:shadow-2xl">
        <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <div className="w-1 h-8 bg-gradient-to-b from-emerald-500 to-cyan-500 rounded-full" />
            <h2 className="text-2xl font-semibold text-slate-800">Zusammenfassung</h2>
          </div>
          <button
            onClick={onDownloadPDF}
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 text-white rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105 font-medium"
          >
            <Download className="w-5 h-5" />
            PDF Herunterladen
          </button>
        </div>

        <div className="bg-gradient-to-br from-emerald-50 via-cyan-50 to-blue-50 rounded-xl p-6 mb-6 border-2 border-emerald-100">
          <div className="prose max-w-none">
            <p className="text-slate-700 leading-relaxed whitespace-pre-wrap">
              {recordingData.summary}
            </p>
          </div>
        </div>

        <div className="border-t-2 border-gradient-to-r from-emerald-200 to-cyan-200 pt-6">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-1 h-6 bg-gradient-to-b from-emerald-500 to-cyan-500 rounded-full" />
            <h3 className="text-lg font-semibold text-slate-800">Patienteninformationen</h3>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-6 text-sm">
            <div className="bg-gradient-to-br from-slate-50 to-blue-50 p-3 rounded-lg border border-slate-200">
              <span className="text-slate-500 text-xs font-semibold">Name</span>
              <p className="font-semibold text-slate-800 mt-1">
                {patientData.vorname} {patientData.nachname}
              </p>
            </div>
            <div className="bg-gradient-to-br from-slate-50 to-emerald-50 p-3 rounded-lg border border-slate-200">
              <span className="text-slate-500 text-xs font-semibold">Geburtsdatum</span>
              <p className="font-semibold text-slate-800 mt-1">{formatDate(patientData.geburtsdatum)}</p>
            </div>
            <div className="bg-gradient-to-br from-slate-50 to-cyan-50 p-3 rounded-lg border border-slate-200">
              <span className="text-slate-500 text-xs font-semibold">Geschlecht</span>
              <p className="font-semibold text-slate-800 mt-1">
                {patientData.geschlecht === 'M' ? 'Männlich' : patientData.geschlecht === 'W' ? 'Weiblich' : '-'}
              </p>
            </div>
            <div className="bg-gradient-to-br from-slate-50 to-blue-50 p-3 rounded-lg border border-slate-200">
              <span className="text-slate-500 text-xs font-semibold">Größe</span>
              <p className="font-semibold text-slate-800 mt-1">{patientData.groesse} cm</p>
            </div>
            <div className="bg-gradient-to-br from-slate-50 to-emerald-50 p-3 rounded-lg border border-slate-200">
              <span className="text-slate-500 text-xs font-semibold">Gewicht</span>
              <p className="font-semibold text-slate-800 mt-1">{patientData.gewicht} kg</p>
            </div>
            <div className="bg-gradient-to-br from-slate-50 to-cyan-50 p-3 rounded-lg border border-slate-200">
              <span className="text-slate-500 text-xs font-semibold">Therapiebeginn</span>
              <p className="font-semibold text-slate-800 mt-1">{formatDate(patientData.therapiebeginn)}</p>
            </div>
            <div className="bg-gradient-to-br from-slate-50 to-blue-50 p-3 rounded-lg border border-slate-200">
              <span className="text-slate-500 text-xs font-semibold">Dauer</span>
              <p className="font-semibold text-slate-800 mt-1">{patientData.dauer} Monate</p>
            </div>
            <div className="bg-gradient-to-br from-slate-50 to-emerald-50 p-3 rounded-lg border border-slate-200">
              <span className="text-slate-500 text-xs font-semibold">TW besprochen</span>
              <p className="font-semibold text-slate-800 mt-1">
                {patientData.twBesprochen === 'ja' ? 'Ja' : patientData.twBesprochen === 'nein' ? 'Nein' : '-'}
              </p>
            </div>
            {patientData.allergie && (
              <div className="md:col-span-3 bg-gradient-to-br from-orange-50 to-amber-50 p-3 rounded-lg border border-orange-200">
                <span className="text-slate-500 text-xs font-semibold">Allergien</span>
                <p className="font-semibold text-slate-800 mt-1">{patientData.allergie}</p>
              </div>
            )}
            {patientData.diagnosen && (
              <div className="md:col-span-3 bg-gradient-to-br from-cyan-50 to-blue-50 p-3 rounded-lg border border-cyan-200">
                <span className="text-slate-500 text-xs font-semibold">Diagnosen</span>
                <p className="font-semibold text-slate-800 mt-1">{patientData.diagnosen}</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8 transform transition-all duration-300 hover:shadow-2xl">
        <button
          onClick={() => setShowTranscript(!showTranscript)}
          className="w-full flex items-center justify-between text-left group"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg shadow-md group-hover:shadow-lg transition-all duration-300">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <h2 className="text-2xl font-semibold text-slate-800">Vollständiges Transkript</h2>
          </div>
          {showTranscript ? (
            <ChevronUp className="w-6 h-6 text-slate-400 group-hover:text-slate-600 transition-colors" />
          ) : (
            <ChevronDown className="w-6 h-6 text-slate-400 group-hover:text-slate-600 transition-colors" />
          )}
        </button>

        {showTranscript && (
          <div className="mt-6 bg-gradient-to-br from-slate-50 to-blue-50 rounded-xl p-6 border-2 border-blue-100 shadow-inner">
            <p className="text-slate-700 leading-relaxed whitespace-pre-wrap font-mono text-sm">
              {recordingData.transcript}
            </p>
          </div>
        )}
      </div>

      {audioUrl && (
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8 transform transition-all duration-300 hover:shadow-2xl">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-gradient-to-br from-cyan-500 to-blue-500 rounded-lg shadow-md">
              <Volume2 className="w-6 h-6 text-white" />
            </div>
            <h2 className="text-2xl font-semibold text-slate-800">Audioaufnahme</h2>
          </div>
          <audio
            ref={audioRef}
            src={audioUrl}
            controls
            className="w-full"
            style={{
              outline: 'none',
              height: '54px',
            }}
          />
        </div>
      )}
    </div>
  );
};

export default ResultsDisplay;
