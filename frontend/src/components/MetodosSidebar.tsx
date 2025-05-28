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
    <aside
      className="w-full sm:w-56 md:w-60 lg:w-64 xl:w-72 bg-white/80 border-r border-gray-200 pr-0 sm:pr-4 py-6 flex-shrink-0 relative overflow-x-hidden"
      style={{ minHeight: "100%" }}
    >
      <h2 className="text-xl font-bold mb-6 pl-6 tracking-wide text-blue-600">
        Métodos
      </h2>
      <ul className="space-y-1">
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
              type="button"
              onClick={() => onSeleccionar(metodo)}
              className={`text-left w-full px-6 py-2 rounded-lg transition-all duration-150 font-medium tracking-wide cursor-pointer
              border-l-4
              ${
                metodo === metodoSeleccionado
                  ? "bg-blue-50 border-blue-600 text-blue-900 shadow-sm font-bold"
                  : "border-transparent text-gray-700 hover:bg-blue-100 hover:text-blue-700"
              }
            `}
              style={{
                boxShadow:
                  metodo === metodoSeleccionado
                    ? "0 2px 8px 0 rgba(37, 99, 235, 0.08)"
                    : undefined,
              }}
            >
              {metodo}
            </button>
          </li>
        ))}
      </ul>
      <div
        className="hidden sm:block absolute top-0 right-0 h-full w-px bg-gradient-to-b from-transparent via-gray-200 to-transparent"
        style={{ right: "-1px" }}
      />
    </aside>
  );
}
