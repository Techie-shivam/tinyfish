const LABEL = { pending: "Waiting", running: "Working", done: "Done", failed: "Failed" };

export default function Progress({ job }) {
  if (job.status === "done") return null;
  return (
    <section className="progress" aria-live="polite">
      <h2>Agents at work</h2>
      <ul>
        {job.agents.map((a) => (
          <li key={a.name} className={`agent ${a.status}`}>
            <span className="dot" aria-hidden="true" />
            <span className="agent-name">{a.name}</span>
            <span className="agent-status">{LABEL[a.status]}</span>
            {a.detail && <span className="agent-detail">{a.detail}</span>}
          </li>
        ))}
      </ul>
    </section>
  );
}
