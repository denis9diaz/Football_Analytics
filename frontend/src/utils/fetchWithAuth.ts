export async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const access = localStorage.getItem("access");

  const authOptions = {
    ...options,
    headers: {
      ...(options.headers || {}),
      Authorization: `Bearer ${access}`,
      "Content-Type": "application/json",
    },
  };

  const response = await fetch(url, authOptions);

  if (response.status === 401) {
    // Token expirado o inválido: limpiar pero NO redirigir
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    localStorage.removeItem("username");
    throw new Error("Unauthorized");
  }

  return response;
}
