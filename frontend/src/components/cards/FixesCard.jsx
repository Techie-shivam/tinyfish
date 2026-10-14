import { useState } from "react";

export default function FixesCard({ job }) {
  const fixes = job.report.top_fixes;
  const [open, setOpen] = useState(0);
  return (
    <section className="card fixes">
      <header>
        <small className="muted">Do this first</small>
        <h2>Top fixes</h2>
      </header>
      {fixes.length === 0 && <p className="muted">No fixes needed.</p>}
      <ul>
        {fixes.map((f, i) => (
          <li key={i} className={open === i ? "open" : ""}>
            <button type="button" onClick={() => setOpen(open === i ? -1 : i)} aria-expanded={open === i}>
              <span className="rank">{i + 1}</span>
              <span className="t">{f.title}</span>
              <span className="pill warn">Fix</span>
            </button>
            {open === i && (
              <div className="detail">
                <pre className="fix-code">{f.fix}</pre>
                <blockquote>{f.evidence}</blockquote>
              </div>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}
