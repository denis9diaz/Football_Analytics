import { createContext, useContext, useEffect, useState } from "react";

type SuscripcionContextType = {
  estaSuscrito: boolean | null;
};

const SuscripcionContext = createContext<SuscripcionContextType>({
  estaSuscrito: null,
});

export function SuscripcionProvider({ children }: { children: React.ReactNode }) {
  const [estaSuscrito, setEstaSuscrito] = useState<boolean | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("access");

    if (!token) {
      setEstaSuscrito(false);  // 👈 No logeado
      return;
    }

    fetch(`${import.meta.env.PUBLIC_API_URL}/api/suscripcion/estado/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => res.ok ? res.json() : Promise.resolve({ activa: false }))
      .then((data) => {
        setEstaSuscrito(!!data.activa); // 👈 true si activa, false si no
      })
      .catch(() => {
        setEstaSuscrito(false);  // 👈 error = no suscrito
      });
  }, []);

  return (
    <SuscripcionContext.Provider value={{ estaSuscrito }}>
      {children}
    </SuscripcionContext.Provider>
  );
}

export function useSuscripcion() {
  return useContext(SuscripcionContext);
}
