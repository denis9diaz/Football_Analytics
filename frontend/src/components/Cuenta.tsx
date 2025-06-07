import React, { useEffect, useState } from "react";
import { fetchWithAuth } from "../utils/fetchWithAuth";

const API_URL = import.meta.env.PUBLIC_API_URL;

export default function CuentaForm() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [editMode, setEditMode] = useState(false);

  const [suscripcion, setSuscripcion] = useState<any | null>(null);
  const [modalVisible, setModalVisible] = useState(false);

  useEffect(() => {
    fetchWithAuth(`${API_URL}/api/auth/user/`)
      .then((res) => res.json())
      .then((data) => {
        setUsername(data.username);
        setEmail(data.email);
      })
      .catch((err) => console.error("Error al cargar usuario:", err));

    fetchWithAuth(`${API_URL}/api/suscripcion/`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => setSuscripcion(data))
      .catch((err) => console.error("Error al cargar suscripción:", err));
  }, []);

  const handleSave = async () => {
    if (!username.trim()) return;

    const res = await fetchWithAuth(`${API_URL}/api/auth/update-username/`, {
      method: "PATCH",
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
    <section className="max-w-3xl mx-auto px-4 py-12 mt-10 space-y-10">
      {/* PERFIL */}
      <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Perfil</h2>

        {/* Username */}
        <div className="mb-4">
          <label
            htmlFor="username"
            className="text-sm text-gray-600 block mb-1"
          >
            Nombre de usuario
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

        {/* Cambiar contraseña */}
        <div className="mt-6">
          <a
            href="/cambiar-contraseña"
            className="text-sm text-blue-600 hover:underline cursor-pointer"
          >
            Cambiar contraseña
          </a>
        </div>
      </div>

      {/* SUSCRIPCIÓN */}
      <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">
          Suscripción
        </h2>

        {suscripcion && (
          <h3 className="text-base font-medium text-gray-700 mb-3">
            Plan:{" "}
            <span className="text-green-600 capitalize mt-3">
              {suscripcion.plan}
            </span>
          </h3>
        )}

        {suscripcion ? (
          suscripcion.cancelada ? (
            <p className="text-sm text-gray-700 mb-3">
              Tu suscripción{" "}
              <strong>
                caducará el día {formatFecha(suscripcion.fecha_fin)}
              </strong>
              . Puedes seguir usando todas las funciones hasta entonces. Puedes
              reactivarla en cualquier momento pulsando{" "}
              <span
                onClick={() => setModalVisible(true)}
                className="text-blue-600 hover:underline cursor-pointer mt-3"
              >
                Gestionar suscripción
              </span>
              .
            </p>
          ) : (
            <p className="text-sm text-gray-700 mb-">
              Tu suscripción se renovará el día{" "}
              <strong>{formatFecha(suscripcion.fecha_fin)}</strong>
              <p
                onClick={() => setModalVisible(true)}
                className="text-blue-600 hover:underline cursor-pointer mt-5"
              >
                Gestionar suscripción
              </p>
            </p>
          )
        ) : (
          <p className="text-sm text-gray-700 mb-3">
            No estás suscrito.{" "}
            <a
              href="/planes"
              className="text-blue-600 hover:underline cursor-pointer"
            >
              Ver planes
            </a>
          </p>
        )}
      </div>

      {/* Modal */}
      {modalVisible && (
  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div className="bg-white rounded-xl p-6 max-w-md w-full shadow-xl text-center">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">
        {suscripcion?.cancelada
          ? "Reactivar suscripción"
          : "Cancelar suscripción"}
      </h2>

      <p className="text-sm text-gray-700 mb-6 text-left">
        {suscripcion?.cancelada ? (
          <>Confirma que deseas reactivar tu cuenta.</>
        ) : (
          <>Al cancelar tu suscripción, perderás el acceso a 
            todas las funciones premium.
            <br />
            Seguirás teniendo acceso hasta que caduque tu
            suscripción.
            <br />
            Puedes reactivarla en cualquier momento.
            <br />
            <br />
            ¿Deseas cancelar?
          </>
        )}
      </p>

      <div className="flex justify-center gap-4">
        <button
          onClick={async () => {
            const endpoint = suscripcion?.cancelada
              ? "reactivar"
              : "cancelar";
            const res = await fetchWithAuth(
              `${API_URL}/api/suscripcion/${endpoint}/`,
              { method: "POST" }
            );
            if (res.ok) {
              setModalVisible(false);
              location.reload();
            }
          }}
          className={`px-4 py-2 text-sm rounded-md font-medium w-full cursor-pointer ${
            suscripcion?.cancelada
              ? "bg-green-600 text-white hover:bg-green-700"
              : "bg-red-600 text-white hover:bg-red-700"
          }`}
        >
          Confirmar
        </button>

        <button
          onClick={() => setModalVisible(false)}
          className="px-4 py-2 text-sm rounded-md border border-gray-300 text-gray-700 hover:bg-gray-100 w-full cursor-pointer"
        >
          Atrás
        </button>
      </div>
    </div>
  </div>
)}

    </section>
  );
}

function formatFecha(fecha: string) {
  const d = new Date(fecha);
  return d.toLocaleDateString("es-ES", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}
