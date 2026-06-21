const API_BASE_URL = "http://localhost:8000";

/**
 * Thin fetch wrapper that injects the JWT auth header and parses JSON.
 * NOTE: token is read from localStorage for this academic MVP;
 * for production, prefer httpOnly cookies to reduce XSS risk.
 */
async function apiRequest(path, { method = "GET", body = null } = {}) {
  const token = localStorage.getItem("access_token");
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `API error: ${response.status}`);
  }
  if (response.status === 204) return null;
  return response.json();
}
