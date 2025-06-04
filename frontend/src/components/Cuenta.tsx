import React, { useEffect, useState } from "react";

const API_URL = import.meta.env.PUBLIC_API_URL;

export default function CuentaForm() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [editMode, setEditMode] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("access");
    if (!token) {
      console.error("Token de acceso no encontrado en localStorage");
      return;
    }

    fetch(`${API_URL}/api/auth/user/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => {
        console.log("Respuesta de la API:", res);
        return res.json();
      })
      .then((data) => {
        console.log("Datos recibidos:", data);
        setUsername(data.username);
        setEmail(data.email);
      })
      .catch((err) => console.error("Error al cargar usuario:", err));
  }, []);

  const handleSave = async () => {
    const token = localStorage.getItem("access");
    if (!token || !username.trim()) return;

    const res = await fetch(`${API_URL}/api/auth/update-username/`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ username }),
    });

    if (res.ok) {
      setEditMode(false);
      localStorage.setItem("username", username);

      const event = new CustomEvent("usernameUpdated", {
        detail: { username },
      });
      window.dispatchEvent(event);

      const span = document.querySelector("#user-name");
      if (span) span.textContent = username;
    } else {
      const error = await res.text();
      console.error("Error actualizando username:", error);
    }
  };

  return (
    <section className="max-w-3xl mx-auto px-4 py-12 mt-10">
      <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Cuenta</h2>

        {/* Username */}
        <div className="mb-4">
          <label
            htmlFor="username"
            className="text-sm text-gray-600 block mb-1"
          >
            Nombre de usuario{" "}
          </label>
          <div className="flex items-center gap-2">
            <input
              id="username"
              type="text"
              value={username}
              readOnly={!editMode}
              onChange={(e) => setUsername(e.target.value)}
              className={`border border-gray-300 rounded-md px-3 py-2 text-sm w-[160px] focus:outline-none ${
                !editMode ? "select-none pointer-events-none text-gray-800" : ""
              }`}
            />
            {!editMode ? (
              <button
                className="text-gray-500 cursor-pointer hover:text-blue-600"
                onClick={() => setEditMode(true)}
              >
                <i className="fas fa-pen"></i>
              </button>
            ) : (
              <button
                onClick={handleSave}
                className="text-sm cursor-pointer text-white bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded-md"
              >
                Guardar
              </button>
            )}
          </div>
        </div>

        {/* Email */}
        <div className="mb-4">
          <label className="text-sm text-gray-600 block mb-1">
            Correo electrónico
          </label>
          <input
            id="email"
            type="email"
            value={email}
            readOnly
            className="border border-gray-200 bg-gray-100 rounded-md px-3 py-2 text-sm w-full select-none pointer-events-none text-gray-700 outline-none"
          />
        </div>

        <div className="mt-6">
          <a
            href="/cambiar-contraseña"
            className="text-sm text-blue-600 hover:underline"
          >
            Cambiar contraseña
          </a>
        </div>
      </div>
    </section>
  );
}
