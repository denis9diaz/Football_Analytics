import React, { useEffect, useState } from "react";
import DatePicker from "react-datepicker";
import { format, addDays, subDays } from "date-fns";
import { es } from "date-fns/locale";
import "react-datepicker/dist/react-datepicker.css";
import { fetchWithAuth } from "../utils/fetchWithAuth";

const API_URL = import.meta.env.PUBLIC_API_URL;

type Liga = {
  id: number;
  nombre: string;
  codigo_pais: string;
  pais?: string;
  codigo_iso_pais?: string;
  nivel?: number | null;
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
  cuota_estim_real: string;
  cuota_casa_apuestas: string;
  valor_estimado: string;
  porcentaje_acierto: string;
  equipo_destacado?: "local" | "visitante";
};

type Favorito = {
  id: number;
  partido_analisis: PartidoAnalizado;
};

export default function Favoritos() {
  const [favoritos, setFavoritos] = useState<Favorito[]>([]);
  const [isCargando, setIsCargando] = useState(true);
  const [fechaSeleccionada, setFechaSeleccionada] = useState<Date>(new Date());
  const [calendarioAbierto, setCalendarioAbierto] = useState(false);

  useEffect(() => {
    fetchWithAuth(`${API_URL}/api/favoritos/`)
      .then((res) => res.json())
      .then((data: Favorito[]) => {
        if (Array.isArray(data)) {
          setFavoritos(data);
        } else {
          setFavoritos([]);
        }
        setIsCargando(false);
      })
      .catch(() => {
        setFavoritos([]);
        setIsCargando(false);
      });
  }, []);

  const toggleFavorito = async (favoritoId: number) => {
    await fetchWithAuth(`${API_URL}/api/favoritos/${favoritoId}/`, {
      method: "DELETE",
    });
    setFavoritos((prev) => prev.filter((f) => f.id !== favoritoId));
  };

  const favoritosFiltrados = favoritos.filter(
    (f) =>
      f.partido_analisis.partido.fecha.slice(0, 10) ===
      fechaSeleccionada.toISOString().slice(0, 10)
  );

  const favoritosPorMetodo = favoritosFiltrados.reduce((acc, fav) => {
    const metodo = fav.partido_analisis.metodo;
    if (!acc[metodo]) acc[metodo] = [];
    acc[metodo].push(fav);
    return acc;
  }, {} as Record<string, Favorito[]>);

  return (
    <div className="bg-white min-h-screen w-full pt-5">
      <main className="max-w-6xl mx-auto pt-8 px-4 py-10">
        <div className="flex justify-end mb-6">
          <div className="relative flex items-center gap-1 sm:gap-2">
            <button
              onClick={() =>
                setFechaSeleccionada(subDays(fechaSeleccionada, 1))
              }
              className="w-7 h-7 rounded-full flex items-center justify-center hover:bg-gray-200 cursor-pointer text-sm"
            >
              ←
            </button>
            <button
              onClick={() => setCalendarioAbierto(!calendarioAbierto)}
              className="border rounded-full px-2 py-1 min-w-[120px] justify-center flex items-center gap-1 sm:gap-2 hover:bg-gray-100 cursor-pointer text-sm"
            >
              <i className="fas fa-calendar-alt text-sm" />
              <span className="font-medium truncate">
                {format(fechaSeleccionada, "dd/MM EEE", {
                  locale: es,
                }).toUpperCase()}
              </span>
            </button>
            <button
              onClick={() =>
                setFechaSeleccionada(addDays(fechaSeleccionada, 1))
              }
              className="w-7 h-7 rounded-full flex items-center justify-center hover:bg-gray-200 cursor-pointer text-sm"
            >
              →
            </button>
            {calendarioAbierto && (
              <div className="absolute top-full right-0 mt-2 z-50">
                <DatePicker
                  selected={fechaSeleccionada}
                  onChange={(date) => {
                    if (date) {
                      setFechaSeleccionada(date);
                      setCalendarioAbierto(false);
                    }
                  }}
                  inline
                  locale={es}
                  calendarStartDay={1}
                />
              </div>
            )}
          </div>
        </div>

        {isCargando ? (
          <div className="flex justify-center items-center h-[300px] text-gray-500 text-lg">
            <i className="fas fa-spinner fa-spin mr-2"></i>
            Cargando favoritos...
          </div>
        ) : Object.keys(favoritosPorMetodo).length === 0 ? (
          <p className="text-gray-500">
            No tienes partidos guardados como favoritos.
          </p>
        ) : (
          Object.entries(favoritosPorMetodo).map(([metodo, favs]) => {
            const favoritosPorLiga = favs.reduce((acc, f) => {
              const ligaId = f.partido_analisis.partido.liga.id;
              if (!acc[ligaId]) acc[ligaId] = [];
              acc[ligaId].push(f);
              return acc;
            }, {} as Record<number, Favorito[]>);

            return (
              <div key={metodo} className="mb-8">
                <h2 className="text-lg font-bold text-blue-900 mb-2">
                  {metodo}
                </h2>

                {Object.entries(favoritosPorLiga)
                  .sort(([, a], [, b]) => {
                    const ligaA = a[0].partido_analisis.partido.liga;
                    const ligaB = b[0].partido_analisis.partido.liga;
                    const paisA = (ligaA.pais || "").toLowerCase();
                    const paisB = (ligaB.pais || "").toLowerCase();
                    const comparePais = paisA.localeCompare(paisB);
                    if (comparePais !== 0) return comparePais;
                    return ligaA.nombre.localeCompare(ligaB.nombre);
                  })
                  .map(([ligaId, favoritosLiga]) => {
                    const liga = favoritosLiga[0].partido_analisis.partido.liga;

                    return (
                      <div key={ligaId} className="mb-4">
                        <div className="flex items-center gap-2 px-4 py-2 bg-blue-100 text-sm font-semibold text-gray-800 rounded-t">
                          <img
                            src={`https://flagcdn.com/w20/${(
                              liga.codigo_iso_pais || ""
                            ).toLowerCase()}.png`}
                            alt={liga.codigo_pais}
                            className="w-5 h-[14px] object-cover"
                          />
                          <span>
                            {(liga.pais || "").toUpperCase()} -{" "}
                            {liga.nombre.charAt(0).toUpperCase() +
                              liga.nombre.slice(1).toLowerCase()}
                          </span>
                        </div>

                        <div className="overflow-x-auto border border-gray-200 rounded-b bg-[#fefefe]">
                          <table className="min-w-[650px] w-full text-sm text-left table-fixed">
                            <thead className="text-xs text-gray-500 bg-gray-50 border-b border-gray-200">
                              <tr>
                                <th className="px-4 py-2 w-[70px]">Hora</th>
                                <th className="px-4 py-2 min-w-[210px]">
                                  Partido
                                </th>
                                <th className="px-4 py-2 w-[110px]">
                                  Probabilidad
                                </th>
                                <th className="px-4 py-2 w-[124px]">
                                  Cuota estimada
                                </th>
                                <th className="px-4 py-2 w-[120px]">
                                  Cuota bookies
                                </th>
                                <th className="px-4 py-2 w-[95px]">% Valor</th>
                                <th className="px-2 py-2 w-[40px] text-center">
                                  Fav
                                </th>
                              </tr>
                            </thead>
                            <tbody>
                              {favoritosLiga.map((f) => {
                                const p = f.partido_analisis;
                                return (
                                  <tr
                                    key={f.id}
                                    className="hover:bg-gray-100 border-b border-gray-200 last:border-b-0 transition-colors"
                                  >
                                    <td className="px-4 py-2 text-gray-700">
                                      {format(
                                        new Date(p.partido.fecha),
                                        "HH:mm",
                                        { locale: es }
                                      )}
                                    </td>
                                    <td className="px-4 py-2 font-medium text-gray-800">
                                      <span
                                        className={
                                          p.equipo_destacado === "local"
                                            ? "font-bold"
                                            : ""
                                        }
                                      >
                                        {p.partido.equipo_local}
                                      </span>{" "}
                                      -{" "}
                                      <span
                                        className={
                                          p.equipo_destacado === "visitante"
                                            ? "font-bold"
                                            : ""
                                        }
                                      >
                                        {p.partido.equipo_visitante}
                                      </span>
                                    </td>
                                    <td className="px-4 py-2 text-blue-600 font-semibold">
                                      {p.porcentaje_acierto
                                        ? `${parseFloat(
                                            p.porcentaje_acierto
                                          ).toFixed(1)}%`
                                        : "-"}
                                    </td>
                                    <td className="px-4 py-2 text-gray-800 font-semibold">
                                      {p.cuota_estim_real}
                                    </td>
                                    <td className="px-4 py-2 text-gray-800 font-semibold">
                                      {p.cuota_casa_apuestas}
                                    </td>
                                    <td
                                      className="px-4 py-2 font-semibold"
                                      style={{
                                        color:
                                          parseFloat(p.valor_estimado) > 0
                                            ? "#16a34a"
                                            : parseFloat(p.valor_estimado) < 0
                                            ? "#dc2626"
                                            : undefined,
                                      }}
                                    >
                                      {p.valor_estimado
                                        ? `${
                                            parseFloat(p.valor_estimado) >= 0
                                              ? "+"
                                              : ""
                                          }${parseFloat(
                                            p.valor_estimado
                                          ).toFixed(0)}%`
                                        : "-"}
                                    </td>
                                    <td
                                      className="px-2 py-2 text-center cursor-pointer text-xl"
                                      onClick={() => toggleFavorito(f.id)}
                                    >
                                      <i
                                        className="fas fa-star"
                                        style={{ color: "#facc15" }}
                                      />
                                    </td>
                                  </tr>
                                );
                              })}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    );
                  })}
              </div>
            );
          })
        )}
      </main>
    </div>
  );
}
