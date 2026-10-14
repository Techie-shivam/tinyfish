async function request(path, options) {
  const res = await fetch(path, options);
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

export const markdownUrl = (id) => `/api/audits/${id}/report.md`;
