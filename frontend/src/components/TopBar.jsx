export default function TopBar({ tabs, tab, onTab, job }) {
  const state = job?.status ?? "idle";
  const label = { idle: "Ready", queued: "Queued", running: "Auditing", done: "Report ready", failed: "Failed" }[state];
  return (
    <nav className="topbar">
      <a className="brand-link" href="#/" aria-label="Back to home"><svg className="logo" viewBox="0 0 40 40" aria-hidden="true">
        <path d="M4 14c4-5 8-5 12 0s8 5 12 0 6-3 8-1M4 22c4-5 8-5 12 0s8 5 12 0 6-3 8-1M4 30c4-5 8-5 12 0s8 5 12 0 6-3 8-1"
          fill="none" stroke="currentColor" strokeWidth="3.2" strokeLinecap="round" />
      </svg></a>
      <div className="pill-nav" role="tablist">
        {tabs.map((t) => (
          <button key={t} role="tab" aria-selected={tab === t} className={tab === t ? "on" : ""} onClick={() => onTab(t)}>
            {t}
          </button>
        ))}
      </div>
      <div className={`status ${state}`}><span className="dot" />{label}</div>
    </nav>
  );
}
