export default function BenchmarkCard({ job }) {
  const rows = job.state.benchmark;
  return (
    <section className="card bench">
      <header>
        <small className="muted">Competitor gap benchmark</small>
        <h2>What outranking pages include</h2>
      </header>
      {rows.length === 0 && <p className="muted">{job.idle ? "Compare your page with the pages that outrank it: pricing, FAQs, tables, proof." : "No rival pages could be fetched."}</p>}
      <ul>
        {rows.map((r) => {
          const share = r.rivals_total ? (r.rivals_with / r.rivals_total) * 100 : 0;
          return (
            <li key={r.feature}>
              <div className="line">
                <span>{r.feature}</span>
                <span className={`pill ${r.you ? "good" : "bad"}`}>{r.you ? "You have it" : "You lack it"}</span>
              </div>
              <div className="meter"><div style={{ width: `${share}%` }} /></div>
              <small className="muted">{r.rivals_with} of {r.rivals_total} rivals</small>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
