import { markdownUrl } from "../api";

function Finding({ f }) {
  return (
    <details className="finding">
      <summary>
        <span className="finding-title">{f.title}</span>
        <span className="finding-detail">{f.detail}</span>
      </summary>
      <blockquote className="evidence">{f.evidence}</blockquote>
      {f.fix && <p className="fix"><b>Fix:</b> {f.fix}</p>}
    </details>
  );
}

function Section({ title, items, empty }) {
  return (
    <section className="section">
      <h2>{title}</h2>
      {items.length ? items.map((f, i) => <Finding key={i} f={f} />) : <p className="muted">{empty}</p>}
    </section>
  );
}

export default function Report({ job }) {
  const { report: r, state: s } = job;
  const rival = s.rivals.filter((x) => x.readability != null);
  const secs = Object.values(s.timings).reduce((a, b) => a + b, 0).toFixed(0);
  return (
    <article className="report">
      <p className="verdict">{r.verdict}</p>
      <div className="meta">
        <span>{secs}s total</span>
        <span>{s.llm_tokens.input + s.llm_tokens.output} LLM tokens</span>
        <a href={markdownUrl(job.id)} download={`audit-${job.id}.md`}>Download Markdown</a>
        <button type="button" onClick={() => window.print()}>Save as PDF</button>
      </div>

      <Section title="What AI can’t read" items={r.cant_read}
        empty="Fetch sees everything a visitor sees on this page." />
      <Section title="What AI can’t answer" items={r.cant_answer}
        empty="This page answers every question the outranking pages answer." />

      <section className="section">
        <h2>Visibility</h2>
        <p className="note">{r.visibility_note}</p>
        {rival.length > 0 && (
          <ul className="bars">
            <li><span>Your page</span><meter value={s.readability ?? 0} max="1" /><b>{Math.round((s.readability ?? 0) * 100)}%</b></li>
            {rival.map((x) => (
              <li key={x.url}><span title={x.url}>#{x.position} {new URL(x.url).hostname}</span>
                <meter value={x.readability} max="1" /><b>{Math.round(x.readability * 100)}%</b></li>
            ))}
          </ul>
        )}
        {r.visibility.map((f, i) => <Finding key={i} f={f} />)}
      </section>

      <Section title="Top fixes" items={r.top_fixes} empty="No fixes needed." />
    </article>
  );
}
