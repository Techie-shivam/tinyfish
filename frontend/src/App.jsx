import { useEffect, useRef, useState } from "react";
import { getAudit, startAudit } from "./api";
import AuditForm from "./components/AuditForm.jsx";
import Hero from "./components/Hero.jsx";
import Progress from "./components/Progress.jsx";
import Report from "./components/Report.jsx";

export default function App() {
  const [job, setJob] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const timer = useRef(null);

  useEffect(() => () => clearTimeout(timer.current), []);

  const poll = (id) => {
    timer.current = setTimeout(async () => {
      try {
        const next = await getAudit(id);
        setJob(next);
        if (next.status === "queued" || next.status === "running") return poll(id);
        setBusy(false);
      } catch (e) {
        setError(e.message);
        setBusy(false);
      }
    }, 1500);
  };

  const submit = async (url, query) => {
    clearTimeout(timer.current);
    setError("");
    setJob(null);
    setBusy(true);
    try {
      const created = await startAudit(url, query);
      setJob(created);
      poll(created.id);
    } catch (e) {
      setError(e.message);
      setBusy(false);
    }
  };

  return (
    <main className="page">
      <Hero />
      <AuditForm onSubmit={submit} busy={busy} />
      {error && <p className="error" role="alert">{error}</p>}
      {job && <Progress job={job} />}
      {job?.status === "failed" && <p className="error" role="alert">{job.error || "The audit failed. Try again."}</p>}
      {job?.report && <Report job={job} />}
    </main>
  );
}
