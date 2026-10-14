import { useState } from "react";

const AGENTS = [
  ["Fetcher and Visitor", "Load your page in a real browser and fetch it the way an AI tool does, then diff the two."],
  ["Missing-Facts", "Labels every lost fact with one cause: JavaScript, image or PDF, collapsed tab, or a bot block."],
  ["Query Discovery", "Finds the searches that should lead to you, and where you rank for each."],
  ["Question Miner", "Reads the pages that outrank you and collects the questions they answer."],
  ["Interrogator", "Answers those questions from your page text only, and must quote its proof."],
  ["Skeptic", "Tries to disprove every finding before it reaches the report."],
  ["Crawl Access", "Checks robots.txt, sitemap.xml, llms.txt and eight AI crawlers."],
  ["Structured Data", "Checks JSON-LD and Open Graph, then writes the snippet you are missing."],
];

const STEPS = [
  ["Paste a URL", "Any public page. A target search query is optional; we pick three if you skip it."],
  ["Agents compare readers", "A browser sees the page like a visitor. Fetch sees it like an AI tool. Rivals get the same test."],
  ["Fix it the same day", "Every finding comes with a quote as proof and a ready fix. Re-check the live page to confirm."],
];

export default function Landing({ onSubmit }) {
  const [url, setUrl] = useState("");
  const [query, setQuery] = useState("");
  const go = (e) => {
    e.preventDefault();
    const u = url.trim();
    onSubmit(/^https?:\/\//i.test(u) ? u : `https://${u}`, query.trim());
  };
  return (
    <div className="landing">
      <nav className="land-nav">
        <a className="brand" href="#/">
          <svg className="logo" viewBox="0 0 40 40" aria-hidden="true">
            <path d="M4 14c4-5 8-5 12 0s8 5 12 0 6-3 8-1M4 22c4-5 8-5 12 0s8 5 12 0 6-3 8-1M4 30c4-5 8-5 12 0s8 5 12 0 6-3 8-1"
              fill="none" stroke="currentColor" strokeWidth="3.2" strokeLinecap="round" />
          </svg>
          Readability Auditor
        </a>
        <div className="land-links">
          <a href="#how">How it works</a>
          <a href="#agents">Agents</a>
          <a className="btn small" href="#/app">Open dashboard</a>
        </div>
      </nav>

      <header className="land-hero">
        <h1>Your page has two readers.<br />Only one sees everything.</h1>
        <p className="lede">
          Paste a URL. We load it in a real browser, fetch it the way AI tools do, and show you the prices, tabs and
          facts that vanish on the way, and what that costs you in search.
        </p>
        <form className="hero-form" onSubmit={go}>
          <input aria-label="Page URL" required placeholder="https://yourshop.com/pricing" value={url}
            onChange={(e) => setUrl(e.target.value)} />
          <input aria-label="Target query (optional)" placeholder="Target query (optional)" value={query}
            onChange={(e) => setQuery(e.target.value)} />
          <button className="btn" type="submit" disabled={!url.trim()}>Audit this page</button>
        </form>

        <div className="split-demo" aria-hidden="true">
          <div className="side">
            <small>A visitor sees</small>
            <p>Pro plan <b>$49 / month</b></p>
            <p>Open Mon–Sat, 9am–6pm</p>
            <p>4.8 stars from 2,310 reviews</p>
          </div>
          <div className="side ai">
            <small>AI tools read</small>
            <p>Pro plan <i className="redact" /></p>
            <p>Open <i className="redact wide" /></p>
            <p><i className="redact full" /></p>
          </div>
        </div>
      </header>

      <section id="how" className="land-section">
        <h2>How it works</h2>
        <ol className="steps">
          {STEPS.map(([t, d], i) => (
            <li className="card" key={t}>
              <span className="rank">{i + 1}</span>
              <h3>{t}</h3>
              <p className="muted">{d}</p>
            </li>
          ))}
        </ol>
      </section>

      <section id="agents" className="land-section">
        <h2>Eight agents, one report</h2>
        <ul className="agent-grid">
          {AGENTS.map(([t, d]) => (
            <li className="card" key={t}>
              <h3>{t}</h3>
              <p className="muted">{d}</p>
            </li>
          ))}
        </ul>
      </section>

      <section className="land-cta card">
        <h2>Find out what AI can’t read on your page</h2>
        <p className="muted">It takes about two minutes and every finding comes with proof.</p>
        <a className="btn" href="#/app">Open the dashboard</a>
      </section>
    </div>
  );
}
