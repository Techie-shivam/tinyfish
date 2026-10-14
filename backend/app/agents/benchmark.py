"""Competitor gap benchmark: structure and coverage of outranking pages versus the target page."""
import re

from app.schemas.state import AuditState, BenchRow

FEATURES = {
    "Pricing stated": lambda t: bool(re.search(r"[$€£₹]\s?\d|\d+\s?(usd|eur|inr)\b|\bpric(e|ing)\b", t, re.I)),
    "FAQ / question headings": lambda t: bool(re.search(r"^#+ .*\?|\bfaq\b|frequently asked", t, re.I | re.M)),
    "Comparison table": lambda t: bool(re.search(r"^\|.+\|\s*$", t, re.M)),
    "Contact or location": lambda t: bool(re.search(r"@\w+\.\w+|\bcontact\b|\baddress\b|\bphone\b", t, re.I)),
    "Customer reviews / proof": lambda t: bool(re.search(r"\breview|testimonial|rated|★|stars?\b", t, re.I)),
    "Detailed content (500+ words)": lambda t: len(t.split()) >= 500,
    "Multiple subheadings (4+)": lambda t: len(re.findall(r"^#{2,4} ", t, re.M)) >= 4,
}


def run(state: AuditState, rival_pages: dict[str, str]) -> None:
    if not rival_pages:
        raise RuntimeError("No rival pages could be fetched to benchmark against")
    page = state.fetch.text
    state.benchmark = [
        BenchRow(feature=name, you=check(page),
                 rivals_with=sum(check(t) for t in rival_pages.values()), rivals_total=len(rival_pages))
        for name, check in FEATURES.items()
    ]
