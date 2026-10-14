export default function AgentsStrip({ job, wide }) {
  const done = job.agents.filter((a) => a.status === "done").length;
  return (
    <section className={`card agents ${wide ? "wide" : ""}`} aria-live="polite">
      <h2>{done} of {job.agents.length} agents done</h2>
      <ul>
        {job.agents.map((a) => (
          <li key={a.name} className={a.status} title={a.detail}>
            <span className="dot" />
            <span>{a.name}</span>
            {a.status === "failed" && <small>{a.detail}</small>}
          </li>
        ))}
      </ul>
    </section>
  );
}
