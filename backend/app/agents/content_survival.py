"""Content survival: which rendered elements (tables, tabs, accordions, images) survive Fetch extraction."""
from app.schemas.state import AuditState, ElementCheck
from app.services.text import normalize


def _survived(kind: str, text: str, haystack: str) -> bool:
    if kind == "image":
        return False  # text inside an image never survives extraction
    parts = [normalize(p) for p in text.replace("\t", "\n").split("\n") if len(p.strip()) >= 6] or [normalize(text)]
    probes = parts[:3] if len(parts) > 1 else [normalize(text)[:80]]
    return sum(p[:80] in haystack for p in probes) >= max(1, len(probes) // 2)


def run(state: AuditState) -> None:
    haystack = normalize(state.fetch.text)
    checks = [ElementCheck(kind=e["kind"], text=e["text"], survived=_survived(e["kind"], e["text"], haystack))
              for e in state.render.elements if len(e["text"].strip()) >= 6]
    state.elements = checks
