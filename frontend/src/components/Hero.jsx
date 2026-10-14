export default function Hero() {
  return (
    <header className="hero">
      <h1>Your page has two readers. Only one of them sees everything.</h1>
      <p className="lede">
        Paste a URL. We load it in a real browser, fetch it the way an AI tool does, and show the facts that
        disappear along the way, and what that costs you in search.
      </p>
      <div className="split" aria-hidden="true">
        <div className="split-side">
          <span className="split-label">A visitor sees</span>
          <p>Pro plan: <b>$49 / month</b></p>
          <p>Open Mon–Sat, 9am–6pm</p>
        </div>
        <div className="split-side ai">
          <span className="split-label">AI tools read</span>
          <p>Pro plan: <i className="redact" /></p>
          <p>Open <i className="redact wide" /></p>
        </div>
      </div>
    </header>
  );
}
