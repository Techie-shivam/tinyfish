import { useEffect, useRef, useState } from "react";
import { getAudit, startAudit } from "./api";
import { saveRecent } from "./recent";
import Evidence from "./components/Evidence.jsx";
import Findings from "./components/Findings.jsx";
import Landing from "./components/Landing.jsx";
import Overview from "./components/Overview.jsx";
import TopBar from "./components/TopBar.jsx";

const TABS = ["Overview", "Findings", "Evidence"];
const readRoute = () => (window.location.hash === "#/app" ? "app" : "landing");

export default function App() {
  const [route, setRoute] = useState(readRoute);
  const [job, setJob] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [tab, setTab] = useState("Overview");
  const timer = useRef(null);

  useEffect(() => {
    const onHash = () => setRoute(readRoute());
    window.addEventListener("hashchange", onHash);
    return () => {
      window.removeEventListener("hashchange", onHash);
      clearTimeout(timer.current);
    };
  }, []);

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
    window.location.hash = "#/app";
    setTab("Overview");
    setError("");
    setJob(null);
    setBusy(true);
    saveRecent(url, query);
    try {
      const created = await startAudit(url, query);
      setJob(created);
      poll(created.id);
    } catch (e) {
      setError(e.message);
      setBusy(false);
    }
  };

  if (route === "landing") return <Landing onSubmit={submit} />;

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
