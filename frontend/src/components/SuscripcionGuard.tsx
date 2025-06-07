import { useEffect, useState } from "react";
import { SuscripcionProvider } from "./SuscripcionContext";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const [autorizado, setAutorizado] = useState(false);
  const [comprobado, setComprobado] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("access");

    if (!token) {
      window.location.href = "/login";
      return;
    }

    fetch(`${import.meta.env.PUBLIC_API_URL}/api/suscripcion/estado/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then(async (res) => {
        if (!res.ok) {
          if (res.status === 401) {
            window.location.href = "/login";
          } else {
            window.location.href = "/planes";
          }
          return;
        }

        const data = await res.json();
        if (data.activa) {
          setAutorizado(true);
        } else {
          window.location.href = "/planes";
        }
      })
      .catch((err) => {
        console.error("Error al verificar suscripción:", err);
        window.location.href = "/login";
      })
      .finally(() => {
        setComprobado(true);
      });
  }, []);

  if (!comprobado || !autorizado) return null;

  return (
    <SuscripcionProvider>
      {children}
    </SuscripcionProvider>
  );
}
