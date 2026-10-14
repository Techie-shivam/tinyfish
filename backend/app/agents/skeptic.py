"""Skeptic: tries to disprove findings before the Report Writer sees them."""
from app.agents import interrogator
from app.schemas.state import AuditState
from app.services.text import normalize


def run(state: AuditState) -> None:
    dropped = flipped = 0
    seen = normalize(state.render.text + "\n" + state.render.expanded_text)
    kept = []
    for g in state.gaps:  # a "missing fact" must really be visible in the rendered page
        if g.cause in ("blocked", "in_image_or_pdf") or normalize(g.evidence) in seen:
            kept.append(g)
        else:
            dropped += 1
    state.gaps = kept
    unanswered = [a for a in state.answers if not a.answered]
    if unanswered and state.fetch.text:
        try:
            retry = interrogator.ask(state, state.fetch.text, [a.q for a in unanswered])
        except Exception:  # noqa: BLE001 - skeptic is best effort
            retry = {}
        for a in unanswered:  # answers that flip between runs are unstable, not real gaps
            if a.q in retry:
                a.answered, a.evidence_quote = True, retry[a.q]
                flipped += 1
    state.skeptic = {"dropped_gaps": dropped, "unstable_answers": flipped}
