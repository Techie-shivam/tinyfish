export default function StatTiles({ job }) {
  const { state, report } = job;
  const answered = state.answers.filter((a) => a.answered).length;
  const blockedBots = Object.values(state.crawl.bots).filter((ok) => !ok).length;
  const tiles = [
    { label: "Text AI can read", value: state.readability == null ? "n/a" : `${Math.round(state.readability * 100)}%`, tone: state.readability >= 0.9 ? "good" : "bad" },
    { label: "Questions answered", value: `${answered}/${state.answers.length}`, tone: answered === state.answers.length ? "good" : "bad" },
    { label: "Facts hidden from AI", value: report.cant_read.length, tone: report.cant_read.length ? "bad" : "good" },
    { label: "AI bots blocked", value: blockedBots, tone: blockedBots ? "bad" : "good" },
  ];
  return (
    <div className="tiles">
      {tiles.map((t) => (
        <section className="card tile" key={t.label}>
          <small className="muted">{t.label}</small>
          <b>{t.value}</b>
          <span className={`pill ${t.tone}`}>{t.tone === "good" ? "Healthy" : "Needs work"}</span>
        </section>
      ))}
    </div>
  );
}
