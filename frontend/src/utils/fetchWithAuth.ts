export async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const access = localStorage.getItem("access");

  const headers = new Headers(options.headers || {});
  headers.set("Authorization", `Bearer ${access}`);
  headers.set("Content-Type", "application/json");

  const authOptions: RequestInit = {
    ...options,
    headers,
  };

  const response = await fetch(url, authOptions);

  if (response.status === 401) {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    localStorage.removeItem("username");
    throw new Error("Unauthorized");
  }

  return response;
}
