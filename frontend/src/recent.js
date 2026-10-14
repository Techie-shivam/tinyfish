const KEY = "auditor.recent";

export function loadRecent() {
  try {
    return JSON.parse(localStorage.getItem(KEY)) || [];
  } catch {
    return [];
  }
}

export function saveRecent(url, query) {
  try {
    const next = [{ url, query, at: Date.now() }, ...loadRecent().filter((r) => r.url !== url)].slice(0, 6);
    localStorage.setItem(KEY, JSON.stringify(next));
  } catch {
    /* storage unavailable: history is a convenience only */
  }
}
