import { markdownUrl } from "../api";

export default function Evidence({ job }) {
  if (!job?.report) return <p className="empty card">Evidence appears here once an audit finishes.</p>;
  const { state } = job;
  const secs = Object.values(state.timings).reduce((a, b) => a + b, 0).toFixed(0);
  const tokens = state.llm_tokens.input + state.llm_tokens.output;
  return (
    <main className="findings">
      <div className="line">
        <p className="muted">{secs}s total · {tokens} LLM tokens · Skeptic dropped {state.skeptic.dropped_gaps ?? 0} gaps, flipped {state.skeptic.unstable_answers ?? 0} answers</p>
        <div className="actions">
          <a className="btn" href={markdownUrl(job.id)} download={`audit-${job.id}.md`}>Download Markdown</a>
          <button className="btn ghost" onClick={() => window.print()}>Save as PDF</button>
        </div>
      </div>
      <h2>Raw audit state</h2>
      <pre className="raw card">{JSON.stringify(state, null, 2)}</pre>
    </main>
  );
}
