import React, { useState } from "react";
import Toast from "./Toast";

const API_URL = import.meta.env.PUBLIC_API_URL;

export default function ContactoForm() {
  const [toastMessage, setToastMessage] = useState("");
  const [showToast, setShowToast] = useState(false);

  const show = (message: string) => {
    setToastMessage(message);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = event.currentTarget;

    const name = (form.elements.namedItem("name") as HTMLInputElement)?.value;
    const email = (form.elements.namedItem("email") as HTMLInputElement)?.value;
    const message = (form.elements.namedItem("message") as HTMLTextAreaElement)
      ?.value;

    try {
      const response = await fetch(`${API_URL}/api/auth/contact/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, message }),
      });

      if (response.ok) {
        show("Mensaje enviado correctamente");
        form.reset();
      } else {
        const data = await response.json();
        show(data.detail || "Error al enviar el mensaje");
      }
    } catch (err) {
      show("Error de conexión con el servidor");
    }
  };

  return (
    <section
      className="max-w-5xl mx-auto px-4 py-16 text-center mt-8 animate__animated animate__fadeIn"
      style={{ animationDuration: "0.8s" }}
    >
      <div className="max-w-md mx-auto bg-gradient-to-br from-blue-50 to-white border border-blue-200 rounded-2xl shadow-md p-8 text-left">
        <h2 className="text-2xl font-bold text-blue-600 mb-8 text-center">
          Contáctanos
        </h2>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label
              htmlFor="name"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Nombre
            </label>
            <input
              type="text"
              id="name"
              name="name"
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-md bg-white focus:ring-blue-600 focus:border-blue-600"
            />
          </div>
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Correo Electrónico
            </label>
            <input
              type="email"
              id="email"
              name="email"
              spellCheck="false"
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-md bg-white focus:ring-blue-600 focus:border-blue-600"
            />
          </div>
          <div>
            <label
              htmlFor="message"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Mensaje
            </label>
            <textarea
              id="message"
              name="message"
              spellCheck="false"
              required
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-md bg-white focus:ring-blue-600 focus:border-blue-600"
            ></textarea>
          </div>
          <button
            type="submit"
            className="w-full bg-blue-600 text-white px-6 py-2 rounded font-semibold hover:bg-blue-700 transition"
          >
            Enviar
          </button>
        </form>
      </div>

      {showToast && (
        <div className="fixed w-full top-16 left-1/2 transform -translate-x-1/2 z-50">
          <Toast message={toastMessage} />
        </div>
      )}
    </section>
  );
}
