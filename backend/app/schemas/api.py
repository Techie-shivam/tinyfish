from typing import Literal

from pydantic import BaseModel, HttpUrl

from app.schemas.state import AuditState


class AuditRequest(BaseModel):
    url: HttpUrl
    target_query: str = ""


class AgentProgress(BaseModel):
    name: str
    status: Literal["pending", "running", "done", "failed"] = "pending"
    detail: str = ""


class Finding(BaseModel):
    title: str
    detail: str
    evidence: str
    fix: str = ""


class Report(BaseModel):
    verdict: str
    cant_read: list[Finding] = []
    cant_answer: list[Finding] = []
    visibility: list[Finding] = []
    visibility_note: str = ""
    survival: list[Finding] = []
    survival_score: float | None = None
    hidden: list[Finding] = []
    crawl: list[Finding] = []
    structured: list[Finding] = []
    benchmark: list[Finding] = []
    top_fixes: list[Finding] = []
    appendix: list[str] = []


class AuditJob(BaseModel):
    id: str
    status: Literal["queued", "running", "done", "failed"] = "queued"
    error: str = ""
    agents: list[AgentProgress] = []
    state: AuditState
    report: Report | None = None
