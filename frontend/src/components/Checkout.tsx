import React, { useEffect, useState } from "react";
import { showToast } from "../utils/toast";

const API_URL = import.meta.env.PUBLIC_API_URL;

export default function Checkout() {
  const [plan, setPlan] = useState("");

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const selectedPlan = urlParams.get("plan") || "";
    setPlan(selectedPlan);
  }, []);

  const confirmarSuscripcion = async () => {
    if (!plan) {
      showToast("Plan no especificado");
      return;
    }

    try {
      const res = await fetch(`${API_URL}/api/suscripcion/contratar/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access")}`,
        },
        body: JSON.stringify({ plan }),
      });

      const data = await res.json();

      if (res.ok) {
        showToast("Suscripción activada correctamente 🎉");
        window.location.href = "/cuenta";
      } else {
        showToast(data.detail || "Error al activar la suscripción");
      }
    } catch (err) {
      console.error(err);
      showToast("Error de red");
    }
  };

  return (
    <section className="max-w-xl mx-auto px-6 py-24 text-center">
      <div className="bg-white p-10 rounded-3xl shadow-md border border-blue-200 animate__animated animate__fadeIn">
        <h1 className="text-2xl font-bold text-blue-700 mb-4">
          Confirmar suscripción
        </h1>
        <p className="text-gray-700 mb-6">
          Vas a contratar el plan <strong className="capitalize">{plan}</strong>
          .
        </p>
        <button
          onClick={confirmarSuscripcion}
          className="bg-blue-700 text-white font-semibold px-6 py-3 rounded-lg hover:bg-blue-800 transition cursor-pointer"
        >
          Confirmar
        </button>
      </div>
    </section>
  );
}
