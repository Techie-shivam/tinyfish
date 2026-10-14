import { useState } from "react";

export default function AuditForm({ onSubmit, busy }) {
  const [url, setUrl] = useState("");
  const [query, setQuery] = useState("");

  const handle = (e) => {
    e.preventDefault();
    const clean = /^https?:\/\//i.test(url.trim()) ? url.trim() : `https://${url.trim()}`;
    onSubmit(clean, query.trim());
  };

  return (
    <form className="form" onSubmit={handle}>
      <label>
        Page URL
        <input type="text" inputMode="url" required placeholder="https://yourshop.com/pricing"
          value={url} onChange={(e) => setUrl(e.target.value)} />
      </label>
      <label>
        Search query you want to rank for <span className="hint">(optional, we pick three if blank)</span>
        <input type="text" placeholder="e.g. best standing desk under $500"
          value={query} onChange={(e) => setQuery(e.target.value)} />
      </label>
      <button type="submit" disabled={busy || !url.trim()}>{busy ? "Auditing…" : "Audit this page"}</button>
    </form>
  );
}
