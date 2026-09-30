const API_BASE = process.env.EXPO_PUBLIC_API_BASE || "https://expense-api-production-0879.up.railway.app";

export async function apiFetch(path, options = {}, token = null) {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {})
    }
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.detail || "API error");

  return data;
}
