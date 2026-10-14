"""Question Miner: finds what rival pages answer, as questions to test the page against."""
from app.core.config import get_settings
from app.schemas.state import AuditState, Question, QueryState
from app.services import llm, tinyfish
from app.services.text import same_site

SYSTEM = (
    "You extract the concrete questions a buyer or visitor would want answered, which the given page "
    "text answers (price, availability, specs, hours, location, policies, comparisons...)."
)


def pick_rivals(state: AuditState, limit: int) -> list[tuple[str, str, int]]:
    """Returns (rival_url, query, position) for the best queries, skipping the user's own site."""
    chosen: list[QueryState] = []
    if state.target_query:
        chosen += [q for q in state.queries if q.q.lower() == state.target_query.lower()]
    rest = [q for q in state.queries if q not in chosen and q.top_results]
    rest.sort(key=lambda q: (q.your_rank == 1, q.intent == "learn"))  # not-winning, commercial first
    chosen += rest[: max(0, 3 - len(chosen))]
    rivals: dict[str, tuple[str, str, int]] = {}
    for q in chosen:
        for hit in q.top_results:
            outranks = q.your_rank == 0 or hit.position < q.your_rank
            if not same_site(hit.url, state.url) and hit.url not in rivals and outranks:
                rivals[hit.url] = (hit.url, q.q, hit.position)
            if len(rivals) >= limit:
                return list(rivals.values())
    return list(rivals.values())


def run(state: AuditState, rival_pages: dict[str, str]) -> list[tuple[str, str, int]]:
    cfg = get_settings()
    rivals = pick_rivals(state, cfg.max_rivals)
    for url, _, _ in rivals:
        page = tinyfish.fetch_page(url)
        if page.text and not page.blocked:
            rival_pages[url] = page.text
    questions: list[Question] = []
    seen: set[str] = set()
    for url, text in rival_pages.items():
        prompt = (
            f"Page text:\n{text[: cfg.page_text_limit // 3]}\n\n"
            'Return {"questions": [str]} with up to 6 questions this page answers.'
        )
        for q in llm.complete_json(SYSTEM, prompt, state.llm_tokens)["questions"]:
            if q.lower() not in seen:
                seen.add(q.lower())
                questions.append(Question(q=q, source_url=url))
    state.questions = questions[: cfg.max_questions]
    return rivals
