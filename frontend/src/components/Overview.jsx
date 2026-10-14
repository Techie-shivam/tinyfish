import { useState } from "react";
import { EMPTY_JOB } from "../emptyJob";
import AgentsStrip from "./cards/AgentsStrip.jsx";
import AnswerCard from "./cards/AnswerCard.jsx";
import BenchmarkCard from "./cards/BenchmarkCard.jsx";
import CrawlCard from "./cards/CrawlCard.jsx";
import FixesCard from "./cards/FixesCard.jsx";
import RecentCard from "./cards/RecentCard.jsx";
import StatTiles from "./cards/StatTiles.jsx";
import SurvivalCard from "./cards/SurvivalCard.jsx";
import VerifyCard from "./cards/VerifyCard.jsx";

function AuditForm({ onSubmit, busy }) {
  const [url, setUrl] = useState("");
  const [query, setQuery] = useState("");
  const handle = (e) => {
    e.preventDefault();
    const u = url.trim();
    onSubmit(/^https?:\/\//i.test(u) ? u : `https://${u}`, query.trim());
  };
  return (
    <form className="audit-form" onSubmit={handle}>
      <input aria-label="Page URL" required placeholder="https://yourshop.com/pricing" value={url}
        onChange={(e) => setUrl(e.target.value)} />
      <input aria-label="Target search query (optional)" placeholder="Target query (optional)" value={query}
        onChange={(e) => setQuery(e.target.value)} />
      <button className="btn" type="submit" disabled={busy || !url.trim()}>{busy ? "Auditing…" : "New audit"}</button>
    </form>
  );
}

export default function Overview({ job, busy, onSubmit }) {
  const ready = Boolean(job?.report);
  const view = ready ? job : EMPTY_JOB;
  const running = job && !ready && job.status !== "failed";
  return (
    <main className="dash">
      <section className="head">
        <div>
          <h1>AI Readability<br />Overview</h1>
          <p className="muted">{job ? job.state.url : "See what AI tools can and can’t read on any live page."}</p>
          {ready && <p className="verdict-line">{job.report.verdict}</p>}
        </div>
        <AuditForm onSubmit={onSubmit} busy={busy} />
      </section>

      {running && <AgentsStrip job={job} wide />}

      <div className={`grid ${ready ? "" : "dim"}`}>
        <div className="left">
          <div className="row two-one">
            <SurvivalCard job={view} />
            <AnswerCard job={view} />
          </div>
          <div className="row one-one">
            <BenchmarkCard job={view} />
            <CrawlCard job={view} />
          </div>
        </div>
        <div className="right">
          <StatTiles job={view} />
          <FixesCard job={view} />
          {ready ? <VerifyCard job={job} /> : <RecentCard onSubmit={onSubmit} busy={busy} />}
        </div>
      </div>
      {ready && <RecentCard onSubmit={onSubmit} busy={busy} />}
    </main>
  );
}
