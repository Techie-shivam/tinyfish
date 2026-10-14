const pct = (v) => Math.round((v ?? 0) * 100);

export default function SurvivalCard({ job }) {
  const { state, report } = job;
  const bars = [{ label: "You", v: state.readability ?? 0, you: true }].concat(
    state.rivals.filter((r) => r.readability != null)
      .map((r) => ({ label: `#${r.position} ${new URL(r.url).hostname.replace("www.", "")}`, v: r.readability })),
  );
  const lost = state.elements.filter((e) => !e.survived);
  return (
    <section className="card survival">
      <header>
        <small className="muted">Content survival</small>
        <h2>What survives Fetch</h2>
      </header>
      <div className="survival-body">
        <div className="big">
          <b>{state.readability == null ? "n/a" : `${pct(state.readability)}%`}</b>
          <span className="muted">of visible text is readable by AI tools</span>
          <p className="note">{report.visibility_note}</p>
        </div>
        <div className="bars" role="img" aria-label="Readability of your page versus outranking pages">
          {bars.map((b) => (
            <div className="bar" key={b.label}>
              <div className="track"><div className={`fill ${b.you ? "you" : ""}`} style={{ height: `${Math.max(pct(b.v), 4)}%` }} /></div>
              <span className="val">{pct(b.v)}%</span>
              <span className="lbl" title={b.label}>{b.label}</span>
            </div>
          ))}
        </div>
      </div>
      {lost.length > 0 && (
        <ul className="lost">
          {lost.slice(0, 4).map((e, i) => (
            <li key={i}><span className="tag">{e.kind}</span> {e.text.slice(0, 90)}</li>
          ))}
        </ul>
      )}
    </section>
  );
}
