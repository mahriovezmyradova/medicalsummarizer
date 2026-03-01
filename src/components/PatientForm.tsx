import React from 'react';
import { Plus, Minus } from 'lucide-react';
import DatePicker from './DatePicker';

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

interface PatientFormProps {
  patientData: PatientData;
  setPatientData: React.Dispatch<React.SetStateAction<PatientData>>;
}

const PatientForm: React.FC<PatientFormProps> = ({ patientData, setPatientData }) => {
  const handleChange = (field: keyof PatientData, value: string | number) => {
    setPatientData((prev) => ({ ...prev, [field]: value }));
  };

  const adjustNumber = (field: 'groesse' | 'gewicht', delta: number) => {
    setPatientData((prev) => ({
      ...prev,
      [field]: Math.max(0, prev[field] + delta),
    }));
  };

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8 transform transition-all duration-300 hover:shadow-2xl">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-1 h-8 bg-gradient-to-b from-blue-500 to-emerald-500 rounded-full" />
        <h2 className="text-2xl font-semibold text-slate-800">Patientendaten</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">
            Vorname
          </label>
          <input
            type="text"
            value={patientData.vorname}
            onChange={(e) => handleChange('vorname', e.target.value)}
            className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400 transition-all duration-300 bg-white/50 hover:bg-white"
            placeholder="Vorname eingeben"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">
            Nachname
          </label>
          <input
            type="text"
            value={patientData.nachname}
            onChange={(e) => handleChange('nachname', e.target.value)}
            className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400 transition-all duration-300 bg-white/50 hover:bg-white"
            placeholder="Nachname eingeben"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">
            Geburtsdatum
          </label>
          <DatePicker
            value={patientData.geburtsdatum}
            onChange={(value) => handleChange('geburtsdatum', value)}
            minYear={1900}
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">
            Geschlecht
          </label>
          <div className="flex gap-4">
            <button
              type="button"
              onClick={() => handleChange('geschlecht', 'M')}
              className={`flex-1 px-4 py-3 rounded-xl border-2 transition-all duration-300 ${
                patientData.geschlecht === 'M'
                  ? 'border-emerald-500 bg-gradient-to-r from-emerald-50 to-cyan-50 text-emerald-700 font-medium shadow-md'
                  : 'border-slate-200 hover:border-emerald-300 hover:bg-slate-50'
              }`}
            >
              Männlich
            </button>
            <button
              type="button"
              onClick={() => handleChange('geschlecht', 'W')}
              className={`flex-1 px-4 py-3 rounded-xl border-2 transition-all duration-300 ${
                patientData.geschlecht === 'W'
                  ? 'border-emerald-500 bg-gradient-to-r from-emerald-50 to-cyan-50 text-emerald-700 font-medium shadow-md'
                  : 'border-slate-200 hover:border-emerald-300 hover:bg-slate-50'
              }`}
            >
              Weiblich
            </button>
          </div>
        </div>

        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">
            Größe (cm)
          </label>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => adjustNumber('groesse', -1)}
              className="group px-3 py-2.5 bg-gradient-to-br from-slate-100 to-slate-200 hover:from-emerald-100 hover:to-cyan-100 rounded-xl transition-all duration-300 shadow-sm hover:shadow-md"
            >
              <Minus className="w-5 h-5 text-slate-600 group-hover:text-emerald-600 transition-colors" />
            </button>
            <input
              type="number"
              value={patientData.groesse}
              onChange={(e) => handleChange('groesse', parseInt(e.target.value) || 0)}
              className="flex-1 text-center px-4 py-3 border-2 border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400 transition-all duration-300 bg-white/50 hover:bg-white font-semibold text-lg"
              min="0"
            />
            <button
              type="button"
              onClick={() => adjustNumber('groesse', 1)}
              className="group px-3 py-2.5 bg-gradient-to-br from-slate-100 to-slate-200 hover:from-emerald-100 hover:to-cyan-100 rounded-xl transition-all duration-300 shadow-sm hover:shadow-md"
            >
              <Plus className="w-5 h-5 text-slate-600 group-hover:text-emerald-600 transition-colors" />
            </button>
          </div>
        </div>

        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">
            Gewicht (kg)
          </label>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => adjustNumber('gewicht', -1)}
              className="group px-3 py-2.5 bg-gradient-to-br from-slate-100 to-slate-200 hover:from-emerald-100 hover:to-cyan-100 rounded-xl transition-all duration-300 shadow-sm hover:shadow-md"
            >
              <Minus className="w-5 h-5 text-slate-600 group-hover:text-emerald-600 transition-colors" />
            </button>
            <input
              type="number"
              value={patientData.gewicht}
              onChange={(e) => handleChange('gewicht', parseInt(e.target.value) || 0)}
              className="flex-1 text-center px-4 py-3 border-2 border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400 transition-all duration-300 bg-white/50 hover:bg-white font-semibold text-lg"
              min="0"
            />
            <button
              type="button"
              onClick={() => adjustNumber('gewicht', 1)}
              className="group px-3 py-2.5 bg-gradient-to-br from-slate-100 to-slate-200 hover:from-emerald-100 hover:to-cyan-100 rounded-xl transition-all duration-300 shadow-sm hover:shadow-md"
            >
              <Plus className="w-5 h-5 text-slate-600 group-hover:text-emerald-600 transition-colors" />
            </button>
          </div>
        </div>

        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">
            Therapiebeginn
          </label>
          <DatePicker
            value={patientData.therapiebeginn}
            onChange={(value) => handleChange('therapiebeginn', value)}
            minYear={2000}
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">
            Dauer (Monate)
          </label>
          <select
            value={patientData.dauer}
            onChange={(e) => handleChange('dauer', parseInt(e.target.value))}
            className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400 transition-all duration-300 bg-white/50 hover:bg-white"
          >
            {Array.from({ length: 12 }, (_, i) => i + 1).map((month) => (
              <option key={month} value={month}>
                {month} {month === 1 ? 'Monat' : 'Monate'}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">
            TW besprochen?
          </label>
          <div className="flex gap-4">
            <button
              type="button"
              onClick={() => handleChange('twBesprochen', 'ja')}
              className={`flex-1 px-4 py-3 rounded-xl border-2 transition-all duration-300 ${
                patientData.twBesprochen === 'ja'
                  ? 'border-emerald-500 bg-gradient-to-r from-emerald-50 to-cyan-50 text-emerald-700 font-medium shadow-md'
                  : 'border-slate-200 hover:border-emerald-300 hover:bg-slate-50'
              }`}
            >
              Ja
            </button>
            <button
              type="button"
              onClick={() => handleChange('twBesprochen', 'nein')}
              className={`flex-1 px-4 py-3 rounded-xl border-2 transition-all duration-300 ${
                patientData.twBesprochen === 'nein'
                  ? 'border-emerald-500 bg-gradient-to-r from-emerald-50 to-cyan-50 text-emerald-700 font-medium shadow-md'
                  : 'border-slate-200 hover:border-emerald-300 hover:bg-slate-50'
              }`}
            >
              Nein
            </button>
          </div>
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-semibold text-slate-700 mb-2">
            Bekannte Allergie?
          </label>
          <input
            type="text"
            value={patientData.allergie}
            onChange={(e) => handleChange('allergie', e.target.value)}
            className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400 transition-all duration-300 bg-white/50 hover:bg-white"
            placeholder="Allergien eingeben"
          />
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-semibold text-slate-700 mb-2">
            Diagnosen
          </label>
          <textarea
            value={patientData.diagnosen}
            onChange={(e) => handleChange('diagnosen', e.target.value)}
            className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400 transition-all duration-300 bg-white/50 hover:bg-white resize-none"
            rows={3}
            placeholder="Diagnosen eingeben"
          />
        </div>
      </div>
    </div>
  );
};

export default PatientForm;
