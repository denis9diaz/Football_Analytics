import React, { useEffect, useState } from "react";
import MetodosSidebar from "./MetodosSidebar";
import DatePicker from "react-datepicker";
import { format, addDays, subDays, isSameDay, parseISO } from "date-fns";
import { es } from "date-fns/locale";
import "react-datepicker/dist/react-datepicker.css";

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
  cuota_estim_real: string;
  cuota_casa_apuestas: string;
  valor_estimado: string;
  porcentaje_acierto: string;
};

export default function Analisis() {
  const [ligas, setLigas] = useState<Liga[]>([]);
  const [partidos, setPartidos] = useState<PartidoAnalizado[]>([]);
  const [ligaFiltrada, setLigaFiltrada] = useState<number | null>(null);
  const [metodoSeleccionado, setMetodoSeleccionado] = useState<string>("");
  const [fechaSeleccionada, setFechaSeleccionada] = useState<Date>(new Date());
  const [calendarioAbierto, setCalendarioAbierto] = useState(false);
  const [ordenCampo, setOrdenCampo] = useState<string | null>(null);
  const [ordenAscendente, setOrdenAscendente] = useState<boolean>(true);

  useEffect(() => {
    if (!metodoSeleccionado) return;

    fetch(
      `${API_URL}/api/partidos-analisis/${encodeURIComponent(
        metodoSeleccionado
      )}/`
    )
      .then((res) => res.json())
      .then((data: PartidoAnalizado[]) => {
        setPartidos(data);

        const ligasUnicas = Array.from(
          new Set<string>(data.map((p) => JSON.stringify(p.partido.liga)))
        ).map((ligaJson) => JSON.parse(ligaJson) as Liga);

        setLigas(ligasUnicas);
        setLigaFiltrada(null);
      });
  }, [metodoSeleccionado]);

  const partidosFiltradosPorFecha = partidos.filter((p) =>
    isSameDay(parseISO(p.partido.fecha), fechaSeleccionada)
  );

  const partidosAgrupados = partidosFiltradosPorFecha.reduce((acc, partido) => {
    const id = partido.partido.liga.id;
    if (!acc[id]) acc[id] = [];
    acc[id].push(partido);
    return acc;
  }, {} as Record<number, PartidoAnalizado[]>);

  const ordenarPartidos = (
    partidos: PartidoAnalizado[],
    campo: keyof PartidoAnalizado
  ) => {
    const sorted = [...partidos].sort((a, b) => {
      const aVal = parseFloat(a[campo] as string);
      const bVal = parseFloat(b[campo] as string);

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

  return (
    <div className="flex flex-col lg:flex-row gap-8 pt-4">
      <MetodosSidebar
        metodoSeleccionado={metodoSeleccionado}
        onSeleccionar={setMetodoSeleccionado}
      />

      <div className="flex-1">
        {metodoSeleccionado ? (
          <>
            <div className="flex justify-between items-center mb-4">
              <div className="text-sm font-medium text-gray-700">
                Filtrar por liga
                <select
                  className="ml-2 border border-gray-300 rounded-lg px-2 py-1 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={ligaFiltrada ?? ""}
                  onChange={(e) =>
                    setLigaFiltrada(
                      e.target.value ? Number(e.target.value) : null
                    )
                  }
                >
                  <option value="">Todas</option>
                  {ligas.map((l) => (
                    <option key={l.id} value={l.id}>
                      {l.nombre}
                    </option>
                  ))}
                </select>
              </div>
              <div className="relative flex items-center gap-2">
                <button
                  onClick={() =>
                    setFechaSeleccionada(subDays(fechaSeleccionada, 1))
                  }
                  className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-gray-200"
                >
                  ←
                </button>
                <button
                  onClick={() => setCalendarioAbierto(!calendarioAbierto)}
                  className="border rounded-full px-4 py-1 flex items-center gap-2 hover:bg-gray-100"
                >
                  <i className="fas fa-calendar-alt" />
                  <span className="font-medium">
                    {format(fechaSeleccionada, "dd/MM EEE", {
                      locale: es,
                    }).toUpperCase()}
                  </span>
                </button>
                <button
                  onClick={() =>
                    setFechaSeleccionada(addDays(fechaSeleccionada, 1))
                  }
                  className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-gray-200"
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

            {ligas
              .filter(
                (liga) => ligaFiltrada === null || liga.id === ligaFiltrada
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
                    <div className="flex items-center justify-between px-4 py-2 bg-blue-100 text-sm font-semibold text-blue-900 uppercase rounded-t">
                      {liga.nombre}
                    </div>

                    {partidosLiga.length > 0 ? (
                      <div className="overflow-x-auto border border-gray-200 rounded-b">
                        <table className="w-full max-w-6xl text-sm text-left table-fixed">
                          <thead className="text-xs text-gray-500 bg-gray-50">
                            <tr>
                              <th className="px-4 py-2 w-[90px]">Hora</th>
                              <th className="px-4 py-2 min-w-[200px]">
                                Partido
                              </th>

                              <th
                                className="px-4 py-2 w-[120px] cursor-pointer select-none"
                                onClick={() =>
                                  handleOrden("porcentaje_acierto")
                                }
                              >
                                <div className="flex items-center gap-1">
                                  % Acierto
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
                                className="px-4 py-2 w-[120px] cursor-pointer select-none"
                                onClick={() => handleOrden("cuota_estim_real")}
                              >
                                <div className="flex items-center gap-1">
                                  Cuota real
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

                              <th className="px-4 py-2 w-[120px]">
                                Cuota casa
                              </th>

                              <th
                                className="px-4 py-2 w-[120px] cursor-pointer select-none"
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
                            </tr>
                          </thead>
                          <tbody>
                            {partidosLiga.map((p) => (
                              <tr key={p.id} className="hover:bg-gray-50">
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
                                  {p.partido.equipo_local} vs{" "}
                                  {p.partido.equipo_visitante}
                                </td>
                                <td className="px-4 py-2 text-blue-600 font-semibold">
                                  {p.porcentaje_acierto
                                    ? `${parseFloat(
                                        p.porcentaje_acierto
                                      ).toFixed(2)}%`
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
                                    ? `${parseFloat(p.valor_estimado).toFixed(
                                        2
                                      )}%`
                                    : "-"}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <p className="px-4 py-2 text-gray-500">
                        No hay partidos disponibles.
                      </p>
                    )}
                  </div>
                );
              })}
          </>
        ) : (
          <p className="text-gray-500">Selecciona un método para comenzar.</p>
        )}
      </div>
    </div>
  );
}
