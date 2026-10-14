"""Report Writer: assembles the report; drops any finding it cannot back with evidence."""
from app.schemas.api import Finding, Report
from app.schemas.state import AuditState
from app.services import llm

SYSTEM = (
    "You are a web-visibility consultant. Pick up to 5 fixes ranked by impact and effort. "
    "Each fix must reference one item id from the list and include a concrete snippet "
    "(JSON-LD, a rewritten sentence or HTML) the owner can paste. No generic advice."
)


def _visibility_note(state: AuditState) -> str:
    own = state.readability
    rivals = [r for r in state.rivals if r.readability is not None]
    ranked = [q for q in state.queries if q.your_rank]
    if own is None or not rivals:
        return "Not enough rival data to say whether readability explains the ranking gap."
    avg = sum(r.readability for r in rivals) / len(rivals)
    base = f"Your page: {own:.0%} of visible text readable by Fetch; {len(rivals)} outranking rival(s) average {avg:.0%}."
    if own >= 0.9:
        return base + " Readability is not the bottleneck; content and authority explain the gap (indicative)."
    if avg - own >= 0.15:
        return base + " Rivals are more readable, so readability likely contributes to the gap (indicative)."
    if ranked or own < 0.9:
        return base + " Rivals are about as unreadable yet rank higher, so readability is not the main bottleneck (indicative)."
    return base


def _fixes(state: AuditState, items: dict[str, Finding]) -> list[Finding]:
    if not items:
        return []
    listing = "\n".join(f"{k}: {f.title} | {f.evidence[:150]}" for k, f in items.items())
    prompt = f'URL: {state.url}\nItems:\n{listing}\nReturn {{"fixes": [{{"ref": id, "title": str, "fix": str}}]}}.'
    out: list[Finding] = []
    try:
        for fx in llm.complete_json(SYSTEM, prompt, state.llm_tokens, key="fixes")[:5]:
            src = items.get(fx.get("ref")) if isinstance(fx, dict) else None
            if src and src.evidence and fx.get("title") and fx.get("fix"):  # evidence rule
                out.append(Finding(title=fx["title"], detail=src.detail, evidence=src.evidence, fix=str(fx["fix"])))
    except Exception:  # noqa: BLE001 - fall through to the deterministic fixes
        pass
    if not out:  # LLM unavailable: use the fixes the agents already attached to each finding
        out = [f for f in items.values() if f.fix and f.evidence][:5]
    return out


def run(state: AuditState) -> Report:
    cant_read = [
        Finding(title=g.fact, detail=f"Cause: {g.cause.replace('_', ' ')}", evidence=g.evidence, fix=g.fix)
        for g in state.gaps if g.evidence
    ]
    cant_answer = [
        Finding(title=a.q, detail="Rival answers this; your page does not.", evidence=f"Asked of: {a.source_url}")
        for a in state.answers if not a.answered and a.source_url
    ]
    visibility = [
        Finding(
            title=q.q,
            detail=f"Intent: {q.intent}. " + (f"Your rank: #{q.your_rank}" if q.your_rank else "Not in top 10"),
            evidence="Top results: " + "; ".join(f"#{h.position} {h.url}" for h in q.top_results[:3]),
        )
        for q in state.queries if q.top_results
    ]
    lost = [e for e in state.elements if not e.survived]
    survival = [
        Finding(title=f"{e.kind.capitalize()} not visible to Fetch", detail="Lost in extraction", evidence=e.text,
                fix="Put this content in server-rendered HTML text.")
        for e in lost
    ]
    hidden = [
        Finding(title="Instruction-like text aimed at AI readers" if h.injection else "Hidden text on the page",
                detail=f"Reason: {h.reason}", evidence=h.text,
                fix="Remove it. AI tools may treat hidden instructions as content or be misled by them.")
        for h in state.hidden_findings
    ]
    crawl = [
        Finding(title=f"{bot} is blocked by robots.txt", detail="AI crawler cannot fetch this page",
                evidence=f"robots.txt disallows {bot} for {state.url}",
                fix=f"Remove the Disallow rule for {bot}, or add 'User-agent: {bot}' with 'Allow: /'.")
        for bot, ok in state.crawl.bots.items() if not ok
    ]
    if not state.crawl.llms_found:
        crawl.append(Finding(title="No llms.txt", detail="AI tools get no curated summary of your site",
                             evidence="/llms.txt returned no content",
                             fix="Add /llms.txt with a short description and links to your key pages."))
    structured = [
        Finding(title=f"Missing {m}", detail="Machine-readable context is absent",
                evidence=f"JSON-LD types: {state.structured.json_ld_types or 'none'}; Open Graph: {state.structured.open_graph or 'none'}",
                fix=state.structured.snippet or "Add the missing tag to the page head.")
        for m in state.structured.missing
    ]
    benchmark = [
        Finding(title=f"{b.rivals_with} of {b.rivals_total} outranking pages have: {b.feature}",
                detail="Your page does not", evidence=f"Your page: no; outranking pages: {b.rivals_with}/{b.rivals_total}",
                fix=f"Add a section covering: {b.feature.lower()}.")
        for b in state.benchmark if not b.you and b.rivals_with >= max(1, b.rivals_total // 2)
    ]
    answered = sum(a.answered for a in state.answers)
    n_hidden = len([g for g in state.gaps if g.cause != "blocked"])
    verdict = f"{n_hidden} facts exist on the page but are invisible to AI tools."
    if state.answers:
        verdict = f"AI tools can answer {answered} of {len(state.answers)} buyer questions about this page. " + verdict
    if state.fetch.blocked:
        verdict = f"AI tools cannot read this page at all: {state.fetch.block_reason}"

    items: dict[str, Finding] = {f"gap{i}": f for i, f in enumerate(cant_read)}
    items.update({f"q{i}": f for i, f in enumerate(cant_answer)})
    items.update({f"c{i}": f for i, f in enumerate(crawl + structured + benchmark + hidden)})
    top = _fixes(state, dict(list(items.items())[:25]))
    appendix = [f"{f.title}: {f.evidence}" for f in cant_read + cant_answer]
    return Report(
        verdict=verdict, cant_read=cant_read, cant_answer=cant_answer, visibility=visibility,
        visibility_note=_visibility_note(state), top_fixes=top, survival=survival, survival_score=state.readability,
        hidden=hidden, crawl=crawl, structured=structured, benchmark=benchmark, appendix=appendix,
    )


def to_markdown(state: AuditState, rep: Report) -> str:
    def section(title: str, fs: list[Finding]) -> str:
        body = "\n".join(
            f"- **{f.title}** - {f.detail}\n  - Evidence: {f.evidence}" + (f"\n  - Fix: {f.fix}" if f.fix else "")
            for f in fs
        )
        return f"\n## {title}\n{body or '_Nothing found._'}\n"

    return (
        f"# AI-Readability Audit: {state.url}\n\n**{rep.verdict}**\n"
        + section("What AI can't read", rep.cant_read)
        + section("What AI can't answer", rep.cant_answer)
        + section("Content that did not survive Fetch", rep.survival)
        + section("Crawl access", rep.crawl)
        + section("Structured data", rep.structured)
        + section("Competitor gaps", rep.benchmark)
        + section("Hidden text and injection", rep.hidden)
        + section("Visibility", rep.visibility)
        + f"\n{rep.visibility_note}\n"
        + section("Top 5 fixes", rep.top_fixes)
    )
