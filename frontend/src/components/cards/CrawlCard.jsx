export default function CrawlCard({ job }) {
  const { crawl, structured } = job.state;
  const names = ["robots.txt", "sitemap.xml", "llms.txt", "JSON-LD", "Meta description", "GPTBot", "ClaudeBot", "PerplexityBot", "Google-Extended"];
  const cells = job.idle ? names.map((name) => ({ name, ok: null })) : [
    { name: "robots.txt", ok: crawl.robots_found },
    { name: "sitemap.xml", ok: crawl.sitemap_found },
    { name: "llms.txt", ok: crawl.llms_found },
    { name: "JSON-LD", ok: structured.json_ld_types.length > 0 },
    { name: "Meta description", ok: structured.has_description },
    ...Object.entries(crawl.bots).map(([name, ok]) => ({ name, ok })),
  ];
  return (
    <section className="card crawl">
      <header>
        <small className="muted">Crawl access and structured data</small>
        <h2>{job.idle ? "Waiting for an audit" : `${cells.filter((c) => !c.ok).length} of ${cells.length} checks failing`}</h2>
      </header>
      <div className="heat">
        {cells.map((c) => (
          <div key={c.name} className={`cell ${c.ok === null ? "idle" : c.ok ? "ok" : "bad"}`}>
            <span className="swatch" aria-hidden="true" />
            <span className="name">{c.name}</span>
            <span className="sr">{c.ok ? "passing" : "failing"}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
