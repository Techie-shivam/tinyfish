"""Query Discovery: proposes labelled queries and finds the page's rank for each."""
from concurrent.futures import ThreadPoolExecutor

from app.core.config import get_settings
from app.schemas.state import AuditState, QueryState
from app.services import llm, tinyfish
from app.services.text import domain, same_site

SYSTEM = (
    "You are an SEO analyst. Given a web page, list search queries a real person would type "
    "to find this page's product/service/topic. Label each intent: buy, compare or learn."
)


def _rank(state: AuditState, q: QueryState) -> QueryState:
    try:
        q.top_results = tinyfish.search(q.q)[:10]
    except Exception:  # noqa: BLE001 - one failed search must not sink the audit
        return q
    for hit in q.top_results:
        if same_site(hit.url, state.url):
            q.your_rank = hit.position
            break
    return q


def _fallback_queries(state: AuditState) -> list[QueryState]:
    """Deterministic queries from the title and domain when the LLM is unavailable."""
    base = (state.fetch.title or domain(state.url).split(".")[0]).split("|")[0].split(" - ")[0].strip()
    seeds = [(base, "learn"), (f"{base} price", "buy"), (f"buy {base} online", "buy"),
             (f"best {base}", "compare"), (f"{base} reviews", "compare"), (f"{base} offers", "buy")]
    return [QueryState(q=q, intent=i) for q, i in seeds if q.strip()]


def run(state: AuditState) -> None:
    n = get_settings().max_queries
    text = (state.render.text or state.fetch.text)[:3000]
    prompt = (
        f"URL: {state.url}\nTitle: {state.fetch.title}\nPage text:\n{text}\n\n"
        f'Return {{"queries": [{{"q": str, "intent": "buy|compare|learn"}}]}} with {n} queries.'
    )
    try:
        data = llm.complete_json(SYSTEM, prompt, state.llm_tokens, key="queries")
        queries = [QueryState(q=d["q"], intent=d.get("intent", "learn")) for d in data[:n] if isinstance(d, dict) and d.get("q")]
    except Exception:  # noqa: BLE001 - fall back to queries built from the page itself
        queries = []
    if not queries:
        queries = _fallback_queries(state)[:n]
    if state.target_query and state.target_query.lower() not in {q.q.lower() for q in queries}:
        queries.insert(0, QueryState(q=state.target_query, intent="buy"))
    with ThreadPoolExecutor(max_workers=6) as pool:
        state.queries = list(pool.map(lambda q: _rank(state, q), queries))
