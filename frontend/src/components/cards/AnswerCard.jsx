export default function AnswerCard({ job }) {
  const answers = job.state.answers;
  const ok = answers.filter((a) => a.answered).length;
  return (
    <section className="card answers">
      <header>
        <small className="muted">Answerability</small>
        <h2>{answers.length ? `${ok} of ${answers.length} questions answered` : "No questions mined"}</h2>
      </header>
      <ul>
        {answers.slice(0, 7).map((a, i) => (
          <li key={i} className={a.answered ? "ok" : "miss"} title={a.evidence_quote || `Asked of ${a.source_url}`}>
            <span className="q">{a.q}</span>
            <span className={`pill ${a.answered ? "good" : "bad"}`}>{a.answered ? "Answered" : "Missing"}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
