import { useState } from "react";
import { verifyFixes } from "../../api";

export default function VerifyCard({ job }) {
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const run = async () => {
    setBusy(true);
    setError("");
    try {
      setResult(await verifyFixes(job.id));
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const pct = (v) => (v == null ? "n/a" : `${Math.round(v * 100)}%`);
  return (
    <section className="card verify">
      <div className="line">
        <div>
          <small className="muted">Closed loop</small>
          <h2>Applied the fixes?</h2>
        </div>
        <button className="btn" onClick={run} disabled={busy}>{busy ? "Re-checking…" : "Re-check live page"}</button>
      </div>
      {error && <p className="error">{error}</p>}
      {result && (
        <p className="note">
          Readability {pct(result.readability_before)} → {pct(result.readability_after)}.
          {" "}{result.closed.length} gap(s) closed, {result.still_open.length} still open, {result.new.length} new.
        </p>
      )}
    </section>
  );
}
