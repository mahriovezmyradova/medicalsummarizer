import React from 'react';
import { Mic, Square } from 'lucide-react';

interface RecordingButtonProps {
  isRecording: boolean;
  onStartRecording: () => void;
  onStopRecording: () => void;
}

const RecordingButton: React.FC<RecordingButtonProps> = ({
  isRecording,
  onStartRecording,
  onStopRecording,
}) => {
  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8 transform transition-all duration-300 hover:shadow-2xl">
      <div className="flex items-center justify-center gap-3 mb-6">
        <div className="w-1 h-8 bg-gradient-to-b from-cyan-500 to-blue-500 rounded-full" />
        <h2 className="text-2xl font-semibold text-slate-800">
          Gesprächsaufnahme
        </h2>
        <div className="w-1 h-8 bg-gradient-to-b from-blue-500 to-cyan-500 rounded-full" />
      </div>

      <div className="flex flex-col items-center gap-6">
        {!isRecording ? (
          <button
            onClick={onStartRecording}
            className="group relative w-36 h-36 rounded-full bg-gradient-to-br from-emerald-400 via-cyan-500 to-blue-500 hover:from-emerald-500 hover:via-cyan-600 hover:to-blue-600 transition-all duration-500 shadow-2xl hover:shadow-[0_0_40px_rgba(16,185,129,0.5)] transform hover:scale-110"
          >
            <div className="absolute inset-0 rounded-full bg-gradient-to-br from-emerald-300 to-blue-300 opacity-0 group-hover:opacity-30 animate-pulse" />
            <div className="absolute inset-2 rounded-full bg-gradient-to-br from-white/20 to-transparent" />
            <Mic className="w-14 h-14 text-white absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 drop-shadow-lg" />
          </button>
        ) : (
          <button
            onClick={onStopRecording}
            className="relative w-36 h-36 rounded-full bg-gradient-to-br from-orange-400 via-red-500 to-pink-500 transition-all duration-300 shadow-2xl animate-pulse-glow"
          >
            <div className="absolute inset-0 rounded-full bg-gradient-to-br from-orange-300 to-pink-300 opacity-40 animate-ping" />
            <div className="absolute inset-2 rounded-full bg-gradient-to-br from-white/20 to-transparent" />
            <Square className="w-12 h-12 text-white absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 drop-shadow-lg" />
          </button>
        )}

        <div className="text-center">
          <p className="text-lg font-medium text-slate-700">
            {isRecording ? 'Aufnahme läuft...' : 'Aufnahme starten'}
          </p>
          <p className="text-sm text-slate-500 mt-1">
            {isRecording
              ? 'Klicken Sie auf Stop, um die Aufnahme zu beenden'
              : 'Klicken Sie auf das Mikrofon, um die Aufnahme zu starten'}
          </p>
        </div>

        {isRecording && (
          <div className="flex items-center gap-3 px-4 py-2 bg-gradient-to-r from-red-500 to-pink-500 rounded-full shadow-lg">
            <span className="w-3 h-3 bg-white rounded-full animate-pulse shadow-lg" />
            <span className="text-sm font-bold text-white tracking-wider">REC</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default RecordingButton;
