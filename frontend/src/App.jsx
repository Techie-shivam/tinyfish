import { useEffect, useRef, useState } from "react";
import { getAudit, startAudit } from "./api";
import Evidence from "./components/Evidence.jsx";
import Findings from "./components/Findings.jsx";
import Overview from "./components/Overview.jsx";
import TopBar from "./components/TopBar.jsx";

const TABS = ["Overview", "Findings", "Evidence"];

export default function App() {
  const [job, setJob] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [tab, setTab] = useState("Overview");
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
    <div className="shell">
      <TopBar tabs={TABS} tab={tab} onTab={setTab} job={job} />
      {error && <p className="error" role="alert">{error}</p>}
      {job?.status === "failed" && <p className="error" role="alert">{job.error || "The audit failed. Try again."}</p>}
      {tab === "Overview" && <Overview job={job} busy={busy} onSubmit={submit} />}
      {tab === "Findings" && <Findings job={job} />}
      {tab === "Evidence" && <Evidence job={job} />}
    </div>
  );
}
