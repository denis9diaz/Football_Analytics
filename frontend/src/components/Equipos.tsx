import React, { useEffect, useState } from "react";

interface Racha {
  condicion: string;
  contexto: string;
  cantidad: number;
  liga_id: number;
}

interface EquipoData {
  equipo: string;
  rachas_actuales: Racha[];
  rachas_historicas: Racha[];
}

const CONDICION_LABELS: Record<string, string> = {
  gol_ht: "Over 0.5 HT",
  tts: "TTS",
  btts: "BTTS",
  over_1_5_marcados: "Over 1.5 Home",
  over_1_5_recibidos: "Over 1.5 Home",
  over_1_5: "Over 1.5",
  over_2_5: "Over 2.5",
  ganar: "Home To Win",
  perder: "Away Lose",
};

const CONDICION_ORDEN = [
  "gol_ht",
  "tts",
  "btts",
  "over_1_5_marcados",
  "over_1_5_recibidos",
  "over_1_5",
  "over_2_5",
  "ganar",
  "perder",
];

const CONTEXTOS = ["local", "visitante", "ambos"];

const Equipos: React.FC = () => {
  const [equipos, setEquipos] = useState<EquipoData[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [contextoSeleccionado, setContextoSeleccionado] =
    useState<string>("local");
  const [nombreLiga, setNombreLiga] = useState<string>("");

  const cargarEquipos = () => {
    const params = new URLSearchParams(window.location.search);
    const ligaId = params.get("ligaId");
    const ligaNombre = params.get("ligaNombre");
    if (ligaNombre) {
      setNombreLiga(decodeURIComponent(ligaNombre));
    }

    if (!ligaId) {
      setError("Liga no especificada");
      setLoading(false);
      return;
    }

    const fetchEquipos = async () => {
      try {
        const API_URL = import.meta.env.PUBLIC_API_URL;
        const response = await fetch(`${API_URL}/api/ligas/${ligaId}/equipos/`);
        if (!response.ok) {
          throw new Error("Error fetching equipos");
        }

        const data = await response.json();

        const filtrados: EquipoData[] = data.map((equipo: EquipoData) => {
          const actuales = equipo.rachas_actuales.filter(
            (r) => r.liga_id?.toString() === ligaId
          );
          const historicas = equipo.rachas_historicas.filter(
            (r) => r.liga_id?.toString() === ligaId
          );

          const clavesActuales = new Set(
            actuales.map((r) => `${r.condicion}-${r.contexto}`)
          );

          const historicasFiltradas = historicas.filter((r) =>
            clavesActuales.has(`${r.condicion}-${r.contexto}`)
          );

          return {
            equipo: equipo.equipo,
            rachas_actuales: actuales,
            rachas_historicas: historicasFiltradas,
          };
        });

        setEquipos(filtrados);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchEquipos();
  };

  useEffect(() => {
    cargarEquipos();

    const handlePopState = () => {
      if (window.location.pathname === "/ligas") {
        window.location.href = "/ligas";
      }
    };

    window.addEventListener("popstate", handlePopState);
    return () => {
      window.removeEventListener("popstate", handlePopState);
    };
  }, []);

  return (
    <div className="min-h-screen py-8 mt-8 px-2 sm:px-4">
      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={() => window.history.back()}
          className="text-blue-600 hover:text-blue-800 text-lg cursor-pointer"
        >
          <i className="fas fa-arrow-left mr-1 cursor-pointer"></i> Volver
        </button>
      </div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800">
          {nombreLiga || "Equipos"}
        </h1>
      </div>
      <div className="mb-4 flex flex-wrap gap-2 items-center">
        {CONTEXTOS.map((ctx) => (
          <button
            key={ctx}
            className={`px-4 py-2 rounded text-sm font-semibold border cursor-pointer ${
              contextoSeleccionado === ctx
                ? "bg-blue-600 text-white"
                : "bg-gray-200 text-gray-700"
            }`}
            onClick={() => setContextoSeleccionado(ctx)}
          >
            {ctx.charAt(0).toUpperCase() + ctx.slice(1)}
          </button>
        ))}

        <select
          className="ml-4 px-4 py-2 rounded text-sm border cursor-pointer bg-gray-200 text-gray-700"
          onChange={(e) => {
            const selectedTeam = e.target.value;
            if (selectedTeam === "") {
              cargarEquipos(); // Reload all teams
            } else {
              setEquipos((prev) => {
                const allTeams = equipos;
                return allTeams.filter((equipo) => equipo.equipo === selectedTeam);
              });
            }
          }}
        >
          <option value="">Todos los equipos</option>
          {equipos.map((equipo) => (
            <option key={equipo.equipo} value={equipo.equipo}>
              {equipo.equipo}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <p className="text-gray-500">Cargando equipos...</p>
      ) : error ? (
        <p className="text-red-500">Error: {error}</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-[400px] w-full text-sm text-left border border-gray-200 rounded bg-[#fefefe]">
            <thead className="text-xs text-gray-500 bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-2 py-2 w-[120px] border-r border-gray-200">
                  Equipo
                </th>
                <th className="px-2 py-2 w-[150px] border-r border-gray-200">
                  Racha
                </th>
                <th className="px-2 py-2 w-[50px] text-center border-r border-gray-200">
                  Actual
                </th>
                <th className="px-2 py-2 w-[50px] text-center">Histórica</th>
              </tr>
            </thead>
            <tbody>
              {equipos.map((equipo, idx) => {
                const rachasFiltradas = CONDICION_ORDEN.map((condicion) => {
                  const actual = equipo.rachas_actuales.find(
                    (r) =>
                      r.contexto === contextoSeleccionado &&
                      r.condicion === condicion
                  );
                  const historica = equipo.rachas_historicas.find(
                    (r) =>
                      r.contexto === contextoSeleccionado &&
                      r.condicion === condicion
                  );
                  if (!actual && !historica) return null;
                  return {
                    condicion,
                    actual: actual?.cantidad ?? "-",
                    historica: historica?.cantidad ?? "-",
                  };
                }).filter(Boolean);

                return rachasFiltradas.map((r, i) => (
                  <tr
                    key={`${idx}-${i}`}
                    className={`border-b border-gray-200 last:border-b-0 transition-colors ${
                      i === 0 ? "" : "hover:bg-gray-100"
                    }`}
                  >
                    {i === 0 ? (
                      <td
                        className="px-2 py-2 font-medium text-gray-800 whitespace-nowrap bg-white hover:bg-gray-50 border-r border-gray-200"
                        rowSpan={rachasFiltradas.length}
                      >
                        {equipo.equipo}
                      </td>
                    ) : null}
                    <td className="px-2 py-2 text-gray-700 hover:bg-gray-50 border-r border-gray-200">
                      {CONDICION_LABELS[r!.condicion] || r!.condicion}
                    </td>
                    <td className="px-2 py-2 text-center text-gray-700 hover:bg-gray-50 border-r border-gray-200">
                      {r!.actual}
                    </td>
                    <td className="px-2 py-2 text-center text-gray-700 hover:bg-gray-50">
                      {r!.historica}
                    </td>
                  </tr>
                ));
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Equipos;
