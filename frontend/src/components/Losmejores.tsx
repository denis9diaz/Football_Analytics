import React, { useEffect, useState } from "react";
import MetodosSidebar from "./MetodosSidebar";
import { format } from "date-fns";
import { es } from "date-fns/locale";
import "animate.css";
import { fetchWithAuth } from "../utils/fetchWithAuth";

const API_URL = import.meta.env.PUBLIC_API_URL;

type Liga = {
  id: number;
  nombre: string;
  codigo_pais: string;
};

type PartidoAnalizado = {
  id: number;
  metodo: string;
  partido: {
    id: number;
    fecha: string;
    liga: Liga;
    equipo_local: string;
    equipo_visitante: string;
  };
  porcentaje_acierto: string;
  cuota_estim_real: string;
  cuota_casa_apuestas: string;
  valor_estimado: string;
  favorito: boolean;
  equipo_destacado?: "local" | "visitante";
};

export default function LosMejores() {
  const [partidosAnalizados, setPartidosAnalizados] = useState<
    Record<string, PartidoAnalizado[]>
  >({});
  const [metodoSeleccionado, setMetodoSeleccionado] = useState<string>("");
  const [isCargando, setIsCargando] = useState(true);
  const [mostrarAviso, setMostrarAviso] = useState(false);

  useEffect(() => {
    const ocultadoHasta = localStorage.getItem("avisoCuotasRankingOcultoHasta");
    if (!ocultadoHasta || new Date() > new Date(ocultadoHasta)) {
      setMostrarAviso(true);
    }
  }, []);

  const cerrarAviso = () => {
    setMostrarAviso(false);
    const mañana = new Date();
    mañana.setDate(mañana.getDate() + 1);
    mañana.setHours(0, 0, 0, 0);
    localStorage.setItem("avisoCuotasRankingOcultoHasta", mañana.toISOString());
  };

  useEffect(() => {
    fetchWithAuth(`${API_URL}/api/ranking-partidos-analizados/`)
      .then((res) => res.json())
      .then((data) => {
        setPartidosAnalizados(data);

        const metodos = Object.keys(data);
        if (metodos.length > 0) {
          const preferido = metodos.find((m) =>
            m.toLowerCase().includes("over 0.5 ht")
          );
          setMetodoSeleccionado(preferido || metodos[0]);
        }

        setIsCargando(false);
      })
      .catch(() => {
        setPartidosAnalizados({});
        setIsCargando(false);
      });
  }, []);

  const partidosMostrar = metodoSeleccionado
    ? partidosAnalizados[metodoSeleccionado] || []
    : [];
  return (
    <div className="bg-white min-h-[calc(100vh-105px)] w-full overflow-hidden pt-5">
      <header className="max-w-6xl mx-auto px-4 py-4 md:hidden">
        <MetodosSidebar
          metodoSeleccionado={metodoSeleccionado}
          onSeleccionar={setMetodoSeleccionado}
        />
      </header>

      <main className="max-w-6xl mx-auto px-4 py-10 flex gap-4 md:flex-row">
        <div className="hidden md:block">
          <MetodosSidebar
            metodoSeleccionado={metodoSeleccionado}
            onSeleccionar={setMetodoSeleccionado}
          />
        </div>

        <div className="flex-1">
          {mostrarAviso && (
            <div className="relative bg-yellow-100 border-l-4 border-yellow-500 text-yellow-800 p-4 rounded-md mb-6">
              <button
                onClick={cerrarAviso}
                className="absolute top-2 right-3 text-yellow-800 cursor-pointer hover:text-yellow-600 text-2xl"
              >
                ×
              </button>
              <p className="font-bold mb-1">🔔 IMPORTANTE</p>
              <p className="text-sm leading-relaxed">
                En Fútbol Analytics recomendamos{" "}
                <strong>no apostar a cuotas inferiores a 1.60</strong>.<br />
                Si la cuota es más baja, es preferible{" "}
                <strong>esperar al directo (LIVE)</strong> y entrar solo si
                alcanza el valor mínimo indicado.
              </p>
            </div>
          )}

          {isCargando ? (
            <div className="flex justify-center items-center h-[300px] text-gray-500 text-lg">
              <i className="fas fa-spinner fa-spin mr-2"></i>
              Cargando partidos...
            </div>
          ) : partidosMostrar.length === 0 ? (
            <p className="text-gray-500 italic">
              Aún no hay partidos analizados para hoy. Vuelve más tarde.
            </p>
          ) : (
            <div className="flex flex-col gap-4 sm:grid sm:grid-cols-1 md:grid-cols-1 lg:grid-cols-1 xl:grid-cols-1 2xl:grid-cols-1">
              {partidosMostrar.slice(0, 3).map((partido, index) => {
                const ranking = index + 1;
                const p = partido;
                const valor = parseFloat(p.valor_estimado);
                const prob = parseFloat(p.porcentaje_acierto);

                const getRankingStyle = (rank: number) => {
                  switch (rank) {
                    case 1:
                      return "bg-yellow-100 border-yellow-400 text-yellow-500";
                    case 2:
                      return "bg-gray-100 border-gray-400 text-gray-500";
                    case 3:
                      return "bg-orange-100 border-orange-400 text-orange-500";
                    default:
                      return "bg-white border-gray-300 text-gray-600";
                  }
                };

                return (
                  <div
                    key={p.id}
                    className={`p-4 rounded-md shadow-md border ${getRankingStyle(
                      ranking
                    )} animate__animated animate__fadeInUp`}
                    style={{ animationDelay: `${index * 0.4}s` }}
                  >
                    <div className="flex items-center gap-3">
                      <div className="text-3xl font-bold">
                        {ranking === 1
                          ? "🥇"
                          : ranking === 2
                          ? "🥈"
                          : ranking === 3
                          ? "🥉"
                          : ranking}
                      </div>
                      <div className="flex-1">
                        <h3 className="text-md font-semibold text-gray-800">
                          <span
                            className={
                              p.equipo_destacado === "local"
                                ? "font-bold text-[1.05rem]"
                                : "text-[0.95rem]"
                            }
                          >
                            {p.partido.equipo_local}
                          </span>{" "}
                          -{" "}
                          <span
                            className={
                              p.equipo_destacado === "visitante"
                                ? "font-bold text-[1.05rem]"
                                : "text-[0.95rem]"
                            }
                          >
                            {p.partido.equipo_visitante}
                          </span>
                        </h3>

                        <p className="text-sm text-gray-500">
                          {format(new Date(p.partido.fecha), "HH:mm", {
                            locale: es,
                          })}
                        </p>
                      </div>
                    </div>

                    <div className="mt-3 flex justify-between items-center">
                      <div className="text-blue-600 font-bold text-lg">
                        {prob ? `${prob.toFixed(1)}%` : "-"}
                      </div>
                      <div className="text-gray-800 font-medium text-base">
                        <span className="block">
                          Cuota estimada:{" "}
                          <span className="text-blue-700 font-bold text-lg">
                            @{p.cuota_estim_real}
                          </span>
                        </span>
                        <span className="block">
                          Cuota bookies:{" "}
                          <span className="text-black font-bold text-lg">
                            @{p.cuota_casa_apuestas}
                          </span>
                        </span>
                      </div>

                      <div
                        className="text-md font-bold"
                        style={{
                          color: valor >= 0 ? "#16a34a" : "#dc2626",
                        }}
                      >
                        {valor !== null && valor !== undefined
                          ? `${valor >= 0 ? "+" : ""}${parseFloat(
                              valor.toFixed(0)
                            )}%`
                          : "-"}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
