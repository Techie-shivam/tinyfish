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
    for fx in llm.complete_json(SYSTEM, prompt, state.llm_tokens)["fixes"][:5]:
        src = items.get(fx.get("ref"))
        if src and src.evidence:  # evidence rule
            out.append(Finding(title=fx["title"], detail=src.detail, evidence=src.evidence, fix=fx["fix"]))
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
    answered = sum(a.answered for a in state.answers)
    verdict = (
        f"AI tools can answer {answered} of {len(state.answers)} buyer questions about this page. "
        f"{len([g for g in state.gaps if g.cause != 'blocked'])} facts exist on the page but are invisible to them."
    )
    if state.fetch.blocked:
        verdict = f"AI tools cannot read this page at all: {state.fetch.block_reason}"

    items: dict[str, Finding] = {f"gap{i}": f for i, f in enumerate(cant_read)}
    items.update({f"q{i}": f for i, f in enumerate(cant_answer)})
    top = _fixes(state, dict(list(items.items())[:25]))
    appendix = [f"{f.title}: {f.evidence}" for f in cant_read + cant_answer]
    return Report(
        verdict=verdict, cant_read=cant_read, cant_answer=cant_answer, visibility=visibility,
        visibility_note=_visibility_note(state), top_fixes=top, appendix=appendix,
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
        + section("Visibility", rep.visibility)
        + f"\n{rep.visibility_note}\n"
        + section("Top 5 fixes", rep.top_fixes)
    )
