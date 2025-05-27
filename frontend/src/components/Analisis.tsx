import React, { useEffect, useState } from "react";
import MetodosSidebar from "./MetodosSidebar";

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
};

export default function Analisis() {
  const [ligas, setLigas] = useState<Liga[]>([]);
  const [partidos, setPartidos] = useState<PartidoAnalizado[]>([]);
  const [ligaSeleccionada, setLigaSeleccionada] = useState<number | null>(null);
  const [metodoSeleccionado, setMetodoSeleccionado] = useState<string>("");

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

        // Extraer ligas únicas desde los partidos analizados
        const ligasUnicas = Array.from(
          new Set<string>(data.map((p) => JSON.stringify(p.partido.liga)))
        ).map((ligaJson) => JSON.parse(ligaJson) as Liga);

        setLigas(ligasUnicas);
        setLigaSeleccionada(null);
      });
  }, [metodoSeleccionado]);

  console.log(
    "➡️ URL final:",
    `${API_URL}/api/partidos-analisis/${encodeURIComponent(
      metodoSeleccionado
    )}/`
  );

  const partidosFiltrados = partidos.filter(
    (p) => p.partido.liga.id === ligaSeleccionada
  );

  return (
    <div className="flex gap-6">
      <MetodosSidebar
        metodoSeleccionado={metodoSeleccionado}
        onSeleccionar={setMetodoSeleccionado}
      />

      <div className="flex-1">
        {metodoSeleccionado ? (
          <>
            <label className="block mb-2 font-semibold">
              Selecciona una liga:
            </label>
            <select
              className="border px-3 py-2 rounded mb-6"
              value={ligaSeleccionada ?? ""}
              onChange={(e) =>
                setLigaSeleccionada(
                  e.target.value ? Number(e.target.value) : null
                )
              }
            >
              <option value="">-- Elige una liga --</option>
              {ligas.map((l) => (
                <option key={l.id} value={l.id}>
                  {l.nombre}
                </option>
              ))}
            </select>

            {ligaSeleccionada ? (
              partidosFiltrados.length > 0 ? (
                <table className="w-full border text-sm">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="text-left px-2 py-1">Fecha</th>
                      <th className="text-left px-2 py-1">Partido</th>
                      <th className="text-left px-2 py-1">Cuota estimada</th>
                      <th className="text-left px-2 py-1">Cuota casa</th>
                      <th className="text-left px-2 py-1">% Valor</th>
                    </tr>
                  </thead>
                  <tbody>
                    {partidosFiltrados.map((p) => (
                      <tr key={p.id} className="border-t">
                        <td className="px-2 py-1">
                          {new Date(p.partido.fecha).toLocaleDateString()}
                        </td>
                        <td className="px-2 py-1">
                          {p.partido.equipo_local} vs{" "}
                          {p.partido.equipo_visitante}
                        </td>
                        <td className="px-2 py-1">{p.cuota_estim_real}</td>
                        <td className="px-2 py-1">{p.cuota_casa_apuestas}</td>
                        <td className="px-2 py-1">{p.valor_estimado}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p className="text-gray-500">No hay partidos para esta liga.</p>
              )
            ) : (
              <p className="text-gray-500">
                Selecciona una liga para ver los partidos.
              </p>
            )}
          </>
        ) : (
          <p className="text-gray-500">Selecciona un método para comenzar.</p>
        )}
      </div>
    </div>
  );
}
