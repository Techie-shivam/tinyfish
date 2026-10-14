"""Shared JSON state every agent reads from and writes to (PRD: Shared state)."""
from typing import Literal

from pydantic import BaseModel, Field

Cause = Literal["js_injected", "in_image_or_pdf", "collapsed_element", "blocked", "not_on_page"]
Intent = Literal["buy", "compare", "learn"]


class FetchState(BaseModel):
    status: int = 0
    text: str = ""
    blocked: bool = False
    block_reason: str = ""
    tokens: int = 0
    final_url: str = ""
    title: str = ""
    links: list[str] = []
    image_links: list[str] = []


class RenderState(BaseModel):
    text: str = ""  # visible text after load
    expanded_text: str = ""  # extra text revealed by opening tabs/accordions
    images_without_alt: int = 0
    error: str = ""


class SearchHit(BaseModel):
    position: int
    title: str
    url: str
    snippet: str = ""


class QueryState(BaseModel):
    q: str
    intent: Intent = "learn"
    your_rank: int = 0  # 0 = not in results
    top_results: list[SearchHit] = []


class Question(BaseModel):
    q: str
    source_url: str


class Answer(BaseModel):
    q: str
    answered: bool
    evidence_quote: str = ""
    source_url: str = ""


class Gap(BaseModel):
    fact: str
    cause: Cause
    fix: str
    evidence: str


class RivalCheck(BaseModel):
    url: str
    query: str
    position: int
    readability: float | None = None  # share of rendered lines Fetch can see
    blocked: bool = False
    error: str = ""


class AuditState(BaseModel):
    url: str
    target_query: str = ""
    fetch: FetchState = Field(default_factory=FetchState)
    render: RenderState = Field(default_factory=RenderState)
    readability: float | None = None
    queries: list[QueryState] = []
    questions: list[Question] = []
    answers: list[Answer] = []
    gaps: list[Gap] = []
    rivals: list[RivalCheck] = []
    timings: dict[str, float] = {}
    llm_tokens: dict[str, int] = {"input": 0, "output": 0}
