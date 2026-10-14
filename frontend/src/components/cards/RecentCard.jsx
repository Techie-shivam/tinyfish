import { loadRecent } from "../../recent";

const ago = (t) => {
  const m = Math.round((Date.now() - t) / 60000);
  return m < 1 ? "just now" : m < 60 ? `${m} min ago` : m < 1440 ? `${Math.round(m / 60)} h ago` : `${Math.round(m / 1440)} d ago`;
};

export default function RecentCard({ onSubmit, busy }) {
  const items = loadRecent();
  return (
    <section className="card recent">
      <header>
        <small className="muted">Recent audits</small>
        <h2>Run one again</h2>
      </header>
      {items.length === 0 && <p className="muted">Pages you audit show up here.</p>}
      <ul>
        {items.map((r) => (
          <li key={r.url}>
            <div className="who">
              <span className="avatar" aria-hidden="true">{new URL(r.url).hostname.replace("www.", "")[0].toUpperCase()}</span>
              <div>
                <span className="host">{new URL(r.url).hostname.replace("www.", "")}</span>
                <small className="muted">{r.query ? `“${r.query}” · ` : ""}{ago(r.at)}</small>
              </div>
            </div>
            <button className="btn ghost small" disabled={busy} onClick={() => onSubmit(r.url, r.query || "")}>Re-audit</button>
          </li>
        ))}
      </ul>
    </section>
  );
}
