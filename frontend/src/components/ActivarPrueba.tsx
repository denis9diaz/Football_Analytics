import React, { useEffect, useState } from "react";
import { fetchWithAuth } from "../utils/fetchWithAuth";
import "animate.css";

const ActivarPrueba: React.FC = () => {
  const [estado, setEstado] = useState<
    "cargando" | "suscrito" | "no_suscrito" | "activando" | "exito" | "error"
  >("cargando");
  const [mensaje, setMensaje] = useState("");

  const API_URL = import.meta.env.PUBLIC_API_URL;

  useEffect(() => {
    const comprobarSuscripcion = async () => {
      try {
        const res = await fetchWithAuth(`${API_URL}/api/suscripcion/estado/`);
        const data = await res.json();

        if (res.ok && data.activa) {
          setEstado("suscrito");
        } else {
          setEstado("no_suscrito");
        }
      } catch (err) {
        console.error("❌ Error al comprobar suscripción:", err);
        setMensaje("Error al verificar suscripción.");
        setEstado("error");
      }
    };

    comprobarSuscripcion();
  }, []);

  const activar = async () => {
    setEstado("activando");
    try {
      const res = await fetchWithAuth(`${API_URL}/api/suscripcion/contratar/`, {
        method: "POST",
        body: JSON.stringify({ plan: "prueba" }),
      });

      console.log("📨 Activación - status:", res.status);

      if (!res.ok) {
        const contentType = res.headers.get("Content-Type") || "";

        if (contentType.includes("application/json")) {
          const data = await res.json();
          console.warn("⚠️ Error al activar prueba (JSON):", data);
          setMensaje(data.detail || "Error al activar la prueba.");
        } else if (contentType.includes("text/html")) {
          const html = await res.text();
          console.warn(
            "⚠️ Respuesta no JSON, contenido HTML:",
            html.slice(0, 200)
          );
          setMensaje("Error inesperado del servidor.");
        } else {
          setMensaje("Error desconocido.");
        }

        setEstado("error");
      } else {
        console.log("✅ Prueba activada correctamente.");
        setEstado("exito");
        setTimeout(() => {
          window.location.href = "/analisis";
        }, 2000);
      }
    } catch (err) {
      console.error("❌ Error de conexión al activar:", err);
      setMensaje("Error de conexión.");
      setEstado("error");
    }
  };

  return (
    <div className="max-w-xl mx-auto mt-25">
      <div className="bg-white shadow-lg rounded-lg p-6 animate__animated animate__fadeIn">
        <h1 className="text-2xl font-bold mb-4 text-blue-600">
          Prueba gratuita
        </h1>
        <p className="text-gray-600 mb-2">
          Después de 3 días la suscripción pasará a ser mensual y se te cobrarán
          19,90€.
        </p>
        <p className="text-gray-600 mb-6">
          Cancela en cualquier momento desde "Mi cuenta".
        </p>

        {estado === "cargando" && <p className="text-gray-500">Cargando...</p>}

        {estado === "suscrito" && (
          <p className="text-green-600 font-medium">
            Ya tienes una suscripción activa.
          </p>
        )}

        {estado === "no_suscrito" && (
          <div className="flex justify-center mt-6">
            <button
              onClick={activar}
              className="bg-blue-600 text-lg font-semibold text-white px-6 py-2 rounded hover:bg-blue-700 transition cursor-pointer"
            >
              Activar prueba de 3 días
            </button>
          </div>
        )}

        {estado === "activando" && (
          <p className="text-gray-500 mt-4">Activando prueba...</p>
        )}

        {estado === "exito" && (
          <p className="text-green-600 mt-4 font-medium">
            ¡Prueba activada correctamente! Redirigiendo...
          </p>
        )}

        {estado === "error" && (
          <div className="text-red-600 mt-4">
            <p>{mensaje}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ActivarPrueba;
