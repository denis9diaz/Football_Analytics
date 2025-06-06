import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

interface Liga {
  id: number;
  nombre: string;
  codigo_pais: string;
  pais: string;
  codigo_iso_pais: string;
  nivel?: number | null;
}

const Ligas: React.FC = () => {
  const [ligas, setLigas] = useState<Liga[]>([]);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchLigas = async () => {
      try {
        const API_URL = import.meta.env.PUBLIC_API_URL;
        const response = await fetch(`${API_URL}/api/ligas/?v=${Date.now()}`);
        if (!response.ok) {
          throw new Error("Error fetching ligas");
        }

        const rawData = await response.json();
        console.log("🧪 Crudo del backend:", rawData[0]);

        const data: Liga[] = rawData.map((liga: any) => ({
          ...liga,
          nivel: Number.isFinite(Number(liga.nivel))
            ? Number(liga.nivel)
            : null,
        }));

        const sorted = data.sort((a, b) => {
          const paisA = (a.pais || a.codigo_pais || "").trim().toLowerCase();
          const paisB_local = (b.pais || b.codigo_pais || "")
            .trim()
            .toLowerCase();
          const comparePais = paisA.localeCompare(paisB_local);
          if (comparePais !== 0) return comparePais;

          const nivelA = a.nivel ?? 99;
          const nivelB = b.nivel ?? 99;
          return nivelA - nivelB;
        });

        console.log("🔍 Orden final de ligas:");
        sorted.forEach((l) => {});

        setLigas(sorted);
      } catch (err: any) {
        setError(err.message);
      }
    };

    fetchLigas();
  }, []);

  const getFlagSrc = (codigo: string) => {
    if (codigo.toLowerCase() === "int") {
      return "/world.webp";
    }
    return `https://flagcdn.com/w20/${codigo.toLowerCase()}.png`;
  };

  const handleLigaClick = (ligaId: number, ligaNombre: string) => {
    window.location.href = `/equipos?ligaId=${ligaId}&ligaNombre=${encodeURIComponent(
      ligaNombre
    )}`;
  };

  return (
    <div className="min-h-screen py-8 mt-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">Ligas</h1>

        {error ? (
          <p className="text-red-500">Error: {error}</p>
        ) : ligas.length === 0 ? (
          <p className="text-gray-500">Cargando ligas...</p>
        ) : (
          <div className="flex flex-col gap-2">
            {ligas.map((liga) => (
              <div
                key={liga.id}
                onClick={() => handleLigaClick(liga.id, liga.nombre)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-100 text-sm font-semibold text-gray-800 rounded cursor-pointer hover:bg-blue-200"
              >
                <img
                  src={getFlagSrc(liga.codigo_iso_pais || "")}
                  alt={liga.codigo_iso_pais}
                  className="w-5 h-[14px] object-cover"
                />
                <span>
                  {(liga.pais || liga.codigo_pais).toUpperCase()} —{" "}
                  {liga.nombre}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Ligas;
