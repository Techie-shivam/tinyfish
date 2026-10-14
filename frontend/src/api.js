// Empty in local dev (Vite proxies /api); set VITE_API_URL to the Render URL in production.
const BASE = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");

async function request(path, options) {
  const res = await fetch(BASE + path, options);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = Array.isArray(body.detail) ? "Enter a full URL, like https://example.com" : body.detail;
    throw new Error(detail || `Request failed (${res.status})`);
  }
  return res;
}

export async function startAudit(url, targetQuery) {
  const res = await request("/api/audits", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, target_query: targetQuery }),
  });
  return res.json();
}

export async function getAudit(id) {
  return (await request(`/api/audits/${id}`)).json();
}

export const markdownUrl = (id) => `${BASE}/api/audits/${id}/report.md`;

export async function verifyFixes(id) {
  return (await request(`/api/audits/${id}/verify`, { method: "POST" })).json();
}
