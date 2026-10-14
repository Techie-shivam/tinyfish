"""Hidden-text and injection scan: hidden/off-screen text and instruction-like strings aimed at AI readers."""
import re

from app.schemas.state import AuditState, HiddenFinding

INJECTION = re.compile(
    r"ignore (all |any )?(previous|prior|above) (instructions|prompts)|you are (now )?(an? )?(ai|assistant|language model)"
    r"|system prompt|do not (tell|reveal|mention)|disregard (the )?(above|previous)|when summari[sz]ing|as an ai",
    re.I,
)


def run(state: AuditState) -> None:
    findings: list[HiddenFinding] = []
    for h in state.render.hidden:
        inj = bool(INJECTION.search(h["text"]))
        # Collapsed/menu text is common; keep only deceptive hiding or instruction-like text.
        if inj or h["reason"] != "display none":
            findings.append(HiddenFinding(text=h["text"], reason=h["reason"], injection=inj))
    for m in INJECTION.finditer(state.fetch.text):
        ctx = state.fetch.text[max(0, m.start() - 60): m.end() + 80].replace("\n", " ")
        if not any(ctx[:40] in f.text for f in findings):
            findings.append(HiddenFinding(text=ctx, reason="instruction-like text in fetched content", injection=True))
    state.hidden_findings = findings[:15]
