import React from "react";

type Props = {
  metodoSeleccionado: string;
  onSeleccionar: (metodo: string) => void;
};

export default function MetodosSidebar({
  metodoSeleccionado,
  onSeleccionar,
}: Props) {
  return (
    <aside className="w-48 border-r pr-4">
      <h2 className="text-lg font-semibold mb-4">Métodos</h2>
      <ul className="space-y-2">
        {[
          "TTS",
          "BTTS",
          "Over 0.5 HT",
          "Over 1.5",
          "Over 2.5",
          "Over 1.5 Home",
          "Home to Win",
        ].map((metodo) => (
          <li key={metodo}>
            <button
              type="button" // <-- IMPORTANTE
              onClick={() => onSeleccionar(metodo)}
              className={`text-left w-full px-2 py-1 rounded hover:bg-blue-100 ${
                metodo === metodoSeleccionado ? "bg-blue-200 font-bold" : ""
              }`}
            >
              {metodo}
            </button>
          </li>
        ))}
      </ul>
    </aside>
  );
}
