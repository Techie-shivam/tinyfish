from types import SimpleNamespace

from app.agents import query_discovery, report_writer
from app.schemas.state import AuditState
from app.services import llm


def _fake(text):
    return lambda *a, **k: SimpleNamespace(text=text, usage_metadata=None)


def test_complete_json_accepts_bare_list_or_wrapped_object(monkeypatch):
    monkeypatch.setattr(llm, "_generate", _fake('[{"q": "a"}]'))
    assert llm.complete_json("s", "p", key="queries") == [{"q": "a"}]
    monkeypatch.setattr(llm, "_generate", _fake('{"queries": [{"q": "b"}]}'))
    assert llm.complete_json("s", "p", key="queries") == [{"q": "b"}]


def test_fallback_queries_use_title():
    state = AuditState(url="https://shop.example.com", target_query="fashion")
    state.fetch.title = "Example Shop | Fashion"
    assert query_discovery._fallback_queries(state)[0].q == "Example Shop"


def test_report_generates_without_llm(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("LLM down")

    monkeypatch.setattr(llm, "complete_json", boom)
    state = AuditState(url="https://x.com")
    state.crawl.bots = {"GPTBot": False}
    report = report_writer.run(state)
    assert report.top_fixes and "GPTBot" in report.top_fixes[0].title
