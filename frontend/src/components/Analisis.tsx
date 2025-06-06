import React, { useEffect, useState } from "react";
import MetodosSidebar from "./MetodosSidebar";
import DatePicker from "react-datepicker";
import { format, addDays, subDays, isSameDay, parseISO } from "date-fns";
import { es } from "date-fns/locale";
import "react-datepicker/dist/react-datepicker.css";
import { fetchWithAuth } from "../utils/fetchWithAuth";
import Select from "react-select";

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
  partido_analisis: {
    id: number;
  };
};

function isoToEmojiFlag(iso: string): string {
  const clean = iso.toUpperCase();
  if (clean.length !== 2) return ""; // evita mostrar basura
  return clean
    .split("")
    .map((c) => String.fromCodePoint(127397 + c.charCodeAt(0)))
    .join("");
}

function capitalize(text: string) {
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
}

export default function Analisis() {
  const [ligas, setLigas] = useState<Liga[]>([]);
  const [partidos, setPartidos] = useState<PartidoAnalizado[]>([]);
  const [ligaFiltrada, setLigaFiltrada] = useState<number | null>(null);
  const [metodoSeleccionado, setMetodoSeleccionado] =
    useState<string>("Over 0.5 HT");
  const [fechaSeleccionada, setFechaSeleccionada] = useState<Date>(new Date());
  const [calendarioAbierto, setCalendarioAbierto] = useState(false);
  const [ordenCampo, setOrdenCampo] = useState<string | null>(null);
  const [ordenAscendente, setOrdenAscendente] = useState<boolean>(true);
  const [favoritos, setFavoritos] = useState<Favorito[]>([]);
  const [isCargando, setIsCargando] = useState(true);
  const [showTooltip, setShowTooltip] = useState<string | null>(null);

  useEffect(() => {
    if (!metodoSeleccionado) {
      setIsCargando(false);
      return;
    }

    setIsCargando(true); // 🔹 Activa el estado de carga antes de comenzar

    fetchWithAuth(`${API_URL}/api/favoritos/`)
      .then((res) => res.json())
      .then((data: Favorito[]) => {
        if (Array.isArray(data)) {
          setFavoritos(data);
        } else {
          console.error("La respuesta de favoritos no es un array:", data);
          setFavoritos([]);
        }
      })
      .catch((err) => {
        console.error("Error al cargar favoritos:", err);
        setFavoritos([]);
      });

    fetch(
      `${API_URL}/api/partidos-analisis/${encodeURIComponent(
        metodoSeleccionado
      )}/`
    )
      .then((res) => res.json())
      .then((data: PartidoAnalizado[]) => {
        const duplicados =
          metodoSeleccionado === "TTS"
            ? data.flatMap((p) => {
                if (!p.equipo_destacado) return [];
                return [p];
              })
            : data;

        setPartidos(duplicados);

        const partidosFechaSeleccionada = duplicados.filter(
          (p) =>
            p.partido.fecha.slice(0, 10) ===
            fechaSeleccionada.toISOString().slice(0, 10)
        );

        const ligasUnicas = Array.from(
          new Set<string>(
            partidosFechaSeleccionada.map((p) => JSON.stringify(p.partido.liga))
          )
        ).map((ligaJson) => JSON.parse(ligaJson) as Liga);

        setLigas(ligasUnicas);
        setLigaFiltrada(null);

        // 🔹 Evita render intermedio antes de completar
        setTimeout(() => {
          setIsCargando(false);
        }, 0);
      })
      .catch((err) => {
        console.error("Error al cargar análisis:", err);
        setIsCargando(false);
      });
  }, [metodoSeleccionado, fechaSeleccionada]);

  const partidosFiltradosPorFecha = partidos.filter(
    (p) =>
      p.partido.fecha.slice(0, 10) ===
      fechaSeleccionada.toISOString().slice(0, 10)
  );

  const partidosAgrupados = partidosFiltradosPorFecha.reduce((acc, partido) => {
    const id = partido.partido.liga.id;
    if (!acc[id]) acc[id] = [];
    acc[id].push(partido);
    return acc;
  }, {} as Record<number, PartidoAnalizado[]>);

  const ordenarPartidos = (
    partidos: PartidoAnalizado[],
    campo: keyof PartidoAnalizado | "fecha"
  ) => {
    const sorted = [...partidos].sort((a, b) => {
      let aVal: number;
      let bVal: number;

      if (campo === "fecha") {
        aVal = new Date(a.partido.fecha).getTime();
        bVal = new Date(b.partido.fecha).getTime();
      } else {
        aVal = parseFloat(a[campo] as string);
        bVal = parseFloat(b[campo] as string);
      }

      if (isNaN(aVal) || isNaN(bVal)) return 0;
      return ordenAscendente ? aVal - bVal : bVal - aVal;
    });

    return sorted;
  };

  const handleOrden = (campo: keyof PartidoAnalizado) => {
    if (ordenCampo === campo) {
      setOrdenAscendente(!ordenAscendente);
    } else {
      setOrdenCampo(campo);
      setOrdenAscendente(false);
    }
  };

  const handleOrdenFecha = () => {
    const campo = "fecha";
    if (ordenCampo === campo) {
      setOrdenAscendente(!ordenAscendente);
    } else {
      setOrdenCampo(campo);
      setOrdenAscendente(true);
    }
  };

  const esFavorito = (partidoAnalisisId: number) => {
    return favoritos.find((f) => f.partido_analisis.id === partidoAnalisisId);
  };

  const toggleFavorito = async (partidoAnalisisId: number) => {
    const existente = favoritos.find(
      (f) => f.partido_analisis.id === partidoAnalisisId
    );
    try {
      if (existente) {
        // Eliminar favorito
        const res = await fetchWithAuth(
          `${API_URL}/api/favoritos/${existente.id}/`,
          {
            method: "DELETE",
          }
        );

        if (res.ok) {
          setFavoritos((prev) =>
            prev.filter((f) => f.partido_analisis.id !== partidoAnalisisId)
          );
        } else {
          const error = await res.text();
          console.error("Error al eliminar favorito:", error);
        }
      } else {
        // Añadir favorito
        const res = await fetchWithAuth(`${API_URL}/api/favoritos/`, {
          method: "POST",
          body: JSON.stringify({ partido_analisis_id: partidoAnalisisId }),
        });

        if (res.ok) {
          const nuevo = await res.json();
          setFavoritos((prev) => [...prev, nuevo]);
        } else if (res.status === 400) {
          const errorText = await res.text();
          if (errorText.includes("llave duplicada")) {
            console.warn("El favorito ya existe en la base de datos.");
          } else {
            console.error("Error al añadir favorito:", errorText);
          }
        } else {
          const errorText = await res.text();
          console.error("Error al añadir favorito:", errorText);
        }
      }
    } catch (err) {
      console.error("Error al alternar favorito:", err);
    }
  };

  const [mostrarAviso, setMostrarAviso] = useState(false);

  useEffect(() => {
    const ocultadoHasta = localStorage.getItem("avisoCuotasOcultoHasta");

    if (!ocultadoHasta || new Date() > new Date(ocultadoHasta)) {
      setMostrarAviso(true);
    }
  }, []);

  const cerrarAviso = () => {
    setMostrarAviso(false);
    const mañana = new Date();
    mañana.setDate(mañana.getDate() + 1);
    mañana.setHours(0, 0, 0, 0); // se oculta hasta mañana a las 00:00
    localStorage.setItem("avisoCuotasOcultoHasta", mañana.toISOString());
  };

  const sortedLigas = [...ligas].sort((a, b) => {
    const paisA = (a.pais || a.codigo_pais || "").trim().toLowerCase();
    const paisB = (b.pais || b.codigo_pais || "").trim().toLowerCase();
    const comparePais = paisA.localeCompare(paisB);
    if (comparePais !== 0) return comparePais;

    const nivelA = a.nivel ?? 99;
    const nivelB = b.nivel ?? 99;
    return nivelA - nivelB;
  });

  return (
    <div className="flex flex-col lg:flex-row gap-8 bg-white min-h-screen pt-15">
      <MetodosSidebar
        metodoSeleccionado={metodoSeleccionado}
        onSeleccionar={setMetodoSeleccionado}
      />

      <div className="flex-1">
        {mostrarAviso && (
          <div className="relative bg-yellow-100 border-l-4 border-yellow-500 text-yellow-800 p-4 rounded-md mb-6 mx-2 sm:mx-0">
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
        {isCargando ? null : metodoSeleccionado ? (
          <>
            <div className="flex justify-between items-center mb-4">
              <div className="text-sm font-medium text-gray-700">
                <div className="ml-2 w-[300px]">
                  <Select
                    options={[
                      {
                        value: null,
                        label: "Todas las ligas",
                      },
                      ...sortedLigas.map((liga) => ({
                        value: liga.id,
                        label: (
                          <div className="flex items-center gap-2">
                            <img
                              src={`https://flagcdn.com/w20/${(
                                liga.codigo_iso_pais || liga.codigo_pais
                              ).toLowerCase()}.png`}
                              alt={liga.nombre}
                              className="inline"
                              width={20}
                              height={14}
                            />
                            <span>
                              {(liga.pais || liga.codigo_pais).toUpperCase()} -{" "}
                              {capitalize(liga.nombre)}
                            </span>
                          </div>
                        ),
                      })),
                    ]}
                    value={
                      ligaFiltrada === null
                        ? {
                            value: null,
                            label: "Todas las ligas",
                          }
                        : (() => {
                            const liga = sortedLigas.find(
                              (l) => l.id === ligaFiltrada
                            );
                            if (!liga) return null;
                            return {
                              value: liga.id,
                              label: (
                                <div className="flex items-center gap-2">
                                  <img
                                    src={`https://flagcdn.com/w20/${(
                                      liga.codigo_iso_pais || liga.codigo_pais
                                    ).toLowerCase()}.png`}
                                    alt={liga.nombre}
                                    className="inline"
                                    width={20}
                                    height={14}
                                  />
                                  <span>
                                    {(
                                      liga.pais || liga.codigo_pais
                                    ).toUpperCase()}{" "}
                                    - {capitalize(liga.nombre)}
                                  </span>
                                </div>
                              ),
                            };
                          })()
                    }
                    onChange={(selected) =>
                      setLigaFiltrada(selected?.value ?? null)
                    }
                    classNamePrefix="react-select"
                    styles={{
                      control: (base) => ({
                        ...base,
                        cursor: "pointer",
                        minHeight: 38,
                      }),
                      option: (base) => ({ ...base, cursor: "pointer" }),
                      menu: (base) => ({ ...base, zIndex: 50 }),
                    }}
                  />
                </div>
              </div>
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
            {sortedLigas
              .filter(
                (liga) => ligaFiltrada === null || liga.id === ligaFiltrada
              )
              .sort((a, b) =>
                (a.pais || a.codigo_pais).localeCompare(b.pais || b.codigo_pais)
              )
              .map((liga) => {
                let partidosLiga = partidosAgrupados[liga.id] || [];
                if (ordenCampo) {
                  partidosLiga = ordenarPartidos(
                    partidosLiga,
                    ordenCampo as keyof PartidoAnalizado
                  );
                }

                return (
                  <div key={liga.id} className="mb-1">
                    <div className="flex items-center gap-2 px-4 py-2 bg-blue-100 text-sm font-semibold text-gray-800 rounded-t">
                      <img
                        src={`https://flagcdn.com/w20/${(
                          liga.codigo_iso_pais || ""
                        ).toLowerCase()}.png`}
                        alt={liga.codigo_iso_pais}
                        className="w-5 h-[14px] object-cover"
                      />
                      <span>
                        {(liga.pais || liga.codigo_pais).toUpperCase()} -{" "}
                        {capitalize(liga.nombre)}
                      </span>
                    </div>

                    {partidosLiga.length > 0 ? (
                      <div className="overflow-x-auto border border-gray-200 rounded-b bg-[#fefefe]">
                        <table className="min-w-[650px] w-full text-sm text-left table-fixed">
                          <thead className="text-xs text-gray-500 bg-gray-50 border-b border-gray-200">
                            <tr>
                              <th
                                className="px-4 py-2 w-[70px] cursor-pointer select-none"
                                onClick={handleOrdenFecha}
                              >
                                <div className="flex items-center gap-1">
                                  Hora
                                  <span
                                    className={
                                      ordenCampo === "fecha"
                                        ? "text-blue-600"
                                        : "text-gray-400"
                                    }
                                  >
                                    {ordenCampo === "fecha"
                                      ? ordenAscendente
                                        ? "▲"
                                        : "▼"
                                      : "↕"}
                                  </span>
                                </div>
                              </th>
                              <th className="px-4 py-2 min-w-[210px]">
                                Partido
                              </th>

                              <th
                                className="px-4 py-2 w-[105px] cursor-pointer select-none"
                                onClick={() =>
                                  handleOrden("porcentaje_acierto")
                                }
                              >
                                <div className="flex items-center gap-1">
                                  Probabilidad
                                  <span
                                    className={
                                      ordenCampo === "porcentaje_acierto"
                                        ? "text-blue-600"
                                        : "text-gray-400"
                                    }
                                  >
                                    {ordenCampo === "porcentaje_acierto"
                                      ? ordenAscendente
                                        ? "▲"
                                        : "▼"
                                      : "↕"}
                                  </span>
                                </div>
                              </th>

                              <th
                                className="px-4 py-2 w-[110px] cursor-pointer select-none"
                                onClick={() => handleOrden("cuota_estim_real")}
                                title="Cuota estimada según Fútbol Analytics."
                              >
                                <div className="flex items-center gap-1">
                                  @Estimada
                                  <span
                                    className={
                                      ordenCampo === "cuota_estim_real"
                                        ? "text-blue-600"
                                        : "text-gray-400"
                                    }
                                  >
                                    {ordenCampo === "cuota_estim_real"
                                      ? ordenAscendente
                                        ? "▲"
                                        : "▼"
                                      : "↕"}
                                  </span>
                                </div>
                              </th>

                              <th
                                className="px-4 py-2 w-[105px] select-none"
                                title="Cuota en las casas de apuestas"
                              >
                                @Bookies
                              </th>

                              <th
                                className="px-4 py-2 w-[95px] cursor-pointer select-none"
                                onClick={() => handleOrden("valor_estimado")}
                              >
                                <div className="flex items-center gap-1">
                                  % Valor
                                  <span
                                    className={
                                      ordenCampo === "valor_estimado"
                                        ? "text-blue-600"
                                        : "text-gray-400"
                                    }
                                  >
                                    {ordenCampo === "valor_estimado"
                                      ? ordenAscendente
                                        ? "▲"
                                        : "▼"
                                      : "↕"}
                                  </span>
                                </div>
                              </th>
                              <th className="px-2 py-2 w-[40px] text-center">
                                Fav
                              </th>
                            </tr>
                          </thead>
                          <tbody>
                            {partidosLiga.map((p) => (
                              <tr
                                key={p.id}
                                className="hover:bg-gray-100 border-b border-gray-200 last:border-b-0"
                              >
                                <td className="px-4 py-2 text-gray-700">
                                  {format(
                                    new Date(
                                      new Date(p.partido.fecha).toLocaleString(
                                        "en-US",
                                        {
                                          timeZone: "Europe/Madrid",
                                        }
                                      )
                                    ),
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
                                  {p.cuota_casa_apuestas &&
                                  !["", "–"].includes(
                                    p.cuota_casa_apuestas.trim()
                                  )
                                    ? p.cuota_casa_apuestas
                                    : "-"}
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
                                      }${parseFloat(p.valor_estimado).toFixed(
                                        0
                                      )}%`
                                    : "-"}
                                </td>
                                <td
                                  className="px-2 py-2 text-center cursor-pointer text-xl"
                                  onClick={() => toggleFavorito(p.id)}
                                >
                                  <i
                                    className={`fas fa-star transition-colors duration-200 ${
                                      esFavorito(p.id)
                                        ? "text-yellow-400"
                                        : "text-gray-300 hover:text-yellow-400"
                                    }`}
                                  />
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : !isCargando ? (
                      <p className="px-4 py-2 text-gray-500">
                        No hay partidos.
                      </p>
                    ) : null}
                  </div>
                );
              })}
          </>
        ) : (
          <p className="text-gray-500">
            Selecciona un método para ver los análisis.
          </p>
        )}
      </div>
    </div>
  );
}
