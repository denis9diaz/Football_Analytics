import React, { useState } from "react";
import DatePicker from "react-datepicker";
import {
  format,
  addDays,
  subDays,
  isSameDay,
  setHours,
  setMinutes,
} from "date-fns";
import { es } from "date-fns/locale";
import "react-datepicker/dist/react-datepicker.css";

interface Props {
  fecha: Date;
  onChange: (fecha: Date) => void;
}

export default function DateSelector({ fecha, onChange }: Props) {
  const [open, setOpen] = useState(false);

  const avanzar = () => onChange(addDays(fecha, 1));
  const retroceder = () => onChange(subDays(fecha, 1));

  return (
    <div className="flex items-center gap-2 text-sm text-gray-700">
      <button
        onClick={retroceder}
        className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-gray-200"
      >
        <span className="text-lg">←</span>
      </button>

      <button
        onClick={() => setOpen(!open)}
        className="border rounded-full px-4 py-1 flex items-center gap-2 hover:bg-gray-100 focus:outline-none"
      >
        <i className="fas fa-calendar-alt" />
        <span className="font-medium">
          {format(fecha, "dd/MM EEE", { locale: es }).toUpperCase()}
        </span>
      </button>

      <button
        onClick={avanzar}
        className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-gray-200"
      >
        <span className="text-lg">→</span>
      </button>

      {open && (
        <div className="absolute mt-2 z-50">
          <DatePicker
            selected={fecha}
            onChange={(date) => {
              if (date) onChange(date);
              setOpen(false);
            }}
            inline
            locale={es}
            calendarStartDay={1}
            dateFormat="dd/MM/yyyy"
          />
        </div>
      )}
    </div>
  );
}
