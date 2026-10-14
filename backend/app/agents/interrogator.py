"""Interrogator: answers each question from the fetched text only, requiring a verbatim quote."""
from app.core.config import get_settings
from app.schemas.state import Answer, AuditState
from app.services import llm
from app.services.text import normalize

SYSTEM = (
    "Answer questions using ONLY the page text provided; never use outside knowledge. "
    "A question is answered only if the text states the answer; give a verbatim quote from the text."
)


def ask(state: AuditState, text: str, qs: list[str]) -> dict[str, str]:
    """One interrogation pass; returns {question: verified_quote} for answered questions."""
    prompt = (
        f"Page text:\n{text}\n\nQuestions: {qs}\n"
        'Return {"answers": [{"q": str, "answered": bool, "quote": str}]}.'
    )
    haystack = normalize(text)
    out: dict[str, str] = {}
    for a in llm.complete_json(SYSTEM, prompt, state.llm_tokens, key="answers"):
        if not isinstance(a, dict) or "q" not in a:
            continue
        quote = (a.get("quote") or "").strip()
        if a.get("answered") and quote and normalize(quote) in haystack:  # reject unverifiable quotes
            out[a["q"]] = quote
    return out


def run(state: AuditState) -> None:
    if not state.questions:
        raise RuntimeError("No questions to ask (Question Miner found none)")
    cfg = get_settings()
    if not state.fetch.text:
        state.answers = [Answer(q=q.q, answered=False, source_url=q.source_url) for q in state.questions]
        return
    text = state.fetch.text[: cfg.page_text_limit]
    qs = [q.q for q in state.questions]
    try:
        passes = [ask(state, text, qs) for _ in range(cfg.interrogation_passes)]
    except Exception as exc:  # noqa: BLE001 - keep the audit going without answers
        state.answers = [Answer(q=q.q, answered=False, source_url=q.source_url) for q in state.questions]
        raise RuntimeError(f"LLM unavailable, answers skipped: {exc}") from exc
    for q in state.questions:
        quotes = [p.get(q.q) for p in passes]
        ok = all(quotes)  # must hold across every pass to count as answered
        state.answers.append(Answer(
            q=q.q, answered=ok, evidence_quote=(quotes[0] or "") if ok else "", source_url=q.source_url,
        ))
