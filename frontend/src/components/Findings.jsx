function Finding({ f }) {
  return (
    <details className="finding card">
      <summary>
        <span className="t">{f.title}</span>
        <span className="muted">{f.detail}</span>
      </summary>
      <blockquote>{f.evidence}</blockquote>
      {f.fix && <pre className="fix-code">{f.fix}</pre>}
    </details>
  );
}

const SECTIONS = [
  ["cant_read", "What AI can’t read"],
  ["survival", "Content that did not survive Fetch"],
  ["cant_answer", "What AI can’t answer"],
  ["benchmark", "Competitor gaps"],
  ["crawl", "Crawl access"],
  ["structured", "Structured data"],
  ["hidden", "Hidden text and injection"],
  ["visibility", "Visibility"],
];

export default function Findings({ job }) {
  if (!job?.report) return <p className="empty card">Findings appear here once an audit finishes.</p>;
  return (
    <main className="findings">
      <p className="verdict">{job.report.verdict}</p>
      {SECTIONS.map(([key, title]) => (
        <section key={key}>
          <h2>{title} <span className="count">{job.report[key].length}</span></h2>
          {job.report[key].length === 0 ? <p className="muted">Nothing found.</p>
            : job.report[key].map((f, i) => <Finding key={i} f={f} />)}
        </section>
      ))}
    </main>
  );
}
