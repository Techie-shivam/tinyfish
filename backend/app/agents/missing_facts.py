"""Missing-Facts: labels every fact humans see but Fetch misses with a single cause."""
from app.schemas.state import AuditState, Gap
from app.services.text import missing_lines, readability

MAX_GAPS = 15
FIXES = {
    "js_injected": "Server-render this content so it is present in the initial HTML.",
    "collapsed_element": "Move this content into the page markup instead of loading it on tab/accordion interaction.",
    "in_image_or_pdf": "Put this information in plain HTML text (keep the image/PDF as a supplement).",
    "blocked": "Change the bot/access rule (WAF, captcha, robots) so AI fetchers can read the page.",
}


def run(state: AuditState) -> None:
    gaps: list[Gap] = []
    f, r = state.fetch, state.render
    if f.blocked:
        gaps.append(Gap(
            fact="The entire page", cause="blocked", fix=FIXES["blocked"],
            evidence=f.block_reason or "Fetch was blocked",
        ))
        state.gaps = gaps
        return
    if r.error:
        return
    state.readability = readability(r.text, f.text)
    for ln in missing_lines(r.text, f.text)[:MAX_GAPS]:
        gaps.append(Gap(fact=ln[:200], cause="js_injected", fix=FIXES["js_injected"], evidence=ln))
    for ln in missing_lines(r.expanded_text, f.text)[: max(0, MAX_GAPS - len(gaps))]:
        gaps.append(Gap(fact=ln[:200], cause="collapsed_element", fix=FIXES["collapsed_element"], evidence=ln))
    pdfs = [u for u in f.links if u.lower().split("?")[0].endswith(".pdf")]
    for pdf in pdfs[:3]:
        gaps.append(Gap(fact=f"Content in linked PDF {pdf.rsplit('/', 1)[-1]}", cause="in_image_or_pdf",
                        fix=FIXES["in_image_or_pdf"], evidence=f"Page links to PDF: {pdf}"))
    if r.images_without_alt:
        gaps.append(Gap(
            fact=f"{r.images_without_alt} large image(s) with no alt text", cause="in_image_or_pdf",
            fix=FIXES["in_image_or_pdf"] + " Add descriptive alt text.",
            evidence=f"{r.images_without_alt} images wider than 150px have no alt attribute",
        ))
    state.gaps = gaps
