"""Interrogator: answers each question from the fetched text only, requiring a verbatim quote."""
from app.core.config import get_settings
from app.schemas.state import Answer, AuditState
from app.services import llm
from app.services.text import normalize

SYSTEM = (
    "Answer questions using ONLY the page text provided; never use outside knowledge. "
    "A question is answered only if the text states the answer; give a verbatim quote from the text."
)


def _pass(state: AuditState, text: str) -> dict[str, str]:
    """One interrogation pass; returns {question: verified_quote} for answered questions."""
    qs = [q.q for q in state.questions]
    prompt = (
        f"Page text:\n{text}\n\nQuestions: {qs}\n"
        'Return {"answers": [{"q": str, "answered": bool, "quote": str}]}.'
    )
    haystack = normalize(text)
    out: dict[str, str] = {}
    for a in llm.complete_json(SYSTEM, prompt, state.llm_tokens)["answers"]:
        quote = (a.get("quote") or "").strip()
        if a.get("answered") and quote and normalize(quote) in haystack:  # reject unverifiable quotes
            out[a["q"]] = quote
    return out


def run(state: AuditState) -> None:
    cfg = get_settings()
    if not state.questions or not state.fetch.text:
        state.answers = [Answer(q=q.q, answered=False, source_url=q.source_url) for q in state.questions]
        return
    text = state.fetch.text[: cfg.page_text_limit]
    passes = [_pass(state, text) for _ in range(cfg.interrogation_passes)]
    for q in state.questions:
        quotes = [p.get(q.q) for p in passes]
        ok = all(quotes)  # must hold across every pass to count as answered
        state.answers.append(Answer(
            q=q.q, answered=ok, evidence_quote=(quotes[0] or "") if ok else "", source_url=q.source_url,
        ))
