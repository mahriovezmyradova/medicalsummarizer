import React, { useState, useRef, useEffect } from 'react';
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight } from 'lucide-react';

interface DatePickerProps {
  value: string;
  onChange: (value: string) => void;
  minYear?: number;
}

const DatePicker: React.FC<DatePickerProps> = ({ value, onChange, minYear = 1900 }) => {
  const [showCalendar, setShowCalendar] = useState(false);
  const [currentMonth, setCurrentMonth] = useState(new Date().getMonth());
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear());
  const calendarRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (calendarRef.current && !calendarRef.current.contains(event.target as Node)) {
        setShowCalendar(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const daysInMonth = (month: number, year: number) => {
    return new Date(year, month + 1, 0).getDate();
  };

  const firstDayOfMonth = (month: number, year: number) => {
    return new Date(year, month, 1).getDay();
  };

  const handleDateSelect = (day: number) => {
    const date = new Date(currentYear, currentMonth, day);
    const formattedDate = date.toISOString().split('T')[0];
    onChange(formattedDate);
    setShowCalendar(false);
  };

  const handlePrevMonth = () => {
    if (currentMonth === 0) {
      setCurrentMonth(11);
      setCurrentYear(currentYear - 1);
    } else {
      setCurrentMonth(currentMonth - 1);
    }
  };

  const handleNextMonth = () => {
    if (currentMonth === 11) {
      setCurrentMonth(0);
      setCurrentYear(currentYear + 1);
    } else {
      setCurrentMonth(currentMonth + 1);
    }
  };

  const days = [];
  const totalDays = daysInMonth(currentMonth, currentYear);
  const firstDay = firstDayOfMonth(currentMonth, currentYear);
  const adjustedFirstDay = firstDay === 0 ? 6 : firstDay - 1;

  for (let i = 0; i < adjustedFirstDay; i++) {
    days.push(<div key={`empty-${i}`} className="h-8" />);
  }

  for (let day = 1; day <= totalDays; day++) {
    days.push(
      <button
        key={day}
        type="button"
        onClick={() => handleDateSelect(day)}
        className="h-8 w-8 rounded-lg hover:bg-gradient-to-br hover:from-emerald-100 hover:to-cyan-100 hover:text-emerald-700 transition-all duration-200 flex items-center justify-center text-sm font-medium hover:shadow-md"
      >
        {day}
      </button>
    );
  }

  const months = [
    'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
    'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'
  ];

  const years = Array.from(
    { length: new Date().getFullYear() - minYear + 1 },
    (_, i) => minYear + i
  ).reverse();

  const formatDisplayDate = (dateString: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('de-DE');
  };

  return (
    <div className="relative" ref={calendarRef}>
      <div className="relative">
        <input
          type="text"
          value={formatDisplayDate(value)}
          readOnly
          onClick={() => setShowCalendar(!showCalendar)}
          className="w-full px-4 py-3 pr-10 border-2 border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400 transition-all duration-300 cursor-pointer bg-white/50 hover:bg-white"
          placeholder="TT.MM.JJJJ"
        />
        <CalendarIcon
          className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none"
        />
      </div>

      {showCalendar && (
        <div className="absolute z-50 mt-2 bg-white/95 backdrop-blur-md rounded-2xl shadow-2xl border-2 border-emerald-100 p-5 w-80 animate-in fade-in slide-in-from-top-2 duration-300">
          <div className="flex items-center justify-between mb-4">
            <button
              type="button"
              onClick={handlePrevMonth}
              className="p-2 hover:bg-gradient-to-br hover:from-emerald-100 hover:to-cyan-100 rounded-lg transition-all duration-200 hover:shadow-md"
            >
              <ChevronLeft className="w-5 h-5 text-slate-600" />
            </button>

            <div className="flex gap-2">
              <select
                value={currentMonth}
                onChange={(e) => setCurrentMonth(parseInt(e.target.value))}
                className="px-3 py-1.5 border-2 border-slate-200 rounded-lg text-sm font-medium focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400 transition-all duration-200 bg-white hover:bg-slate-50"
              >
                {months.map((month, index) => (
                  <option key={month} value={index}>
                    {month}
                  </option>
                ))}
              </select>

              <select
                value={currentYear}
                onChange={(e) => setCurrentYear(parseInt(e.target.value))}
                className="px-3 py-1.5 border-2 border-slate-200 rounded-lg text-sm font-medium focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400 transition-all duration-200 bg-white hover:bg-slate-50"
              >
                {years.map((year) => (
                  <option key={year} value={year}>
                    {year}
                  </option>
                ))}
              </select>
            </div>

            <button
              type="button"
              onClick={handleNextMonth}
              className="p-2 hover:bg-gradient-to-br hover:from-emerald-100 hover:to-cyan-100 rounded-lg transition-all duration-200 hover:shadow-md"
            >
              <ChevronRight className="w-5 h-5 text-slate-600" />
            </button>
          </div>

          <div className="grid grid-cols-7 gap-1 mb-2">
            {['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'].map((day) => (
              <div key={day} className="h-8 flex items-center justify-center text-xs font-medium text-slate-600">
                {day}
              </div>
            ))}
          </div>

          <div className="grid grid-cols-7 gap-1">
            {days}
          </div>
        </div>
      )}
    </div>
  );
};

export default DatePicker;
