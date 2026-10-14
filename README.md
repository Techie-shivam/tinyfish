# AI-Readability & Visibility Auditor

Paste any live URL and find out what AI search and fetch tools can and cannot read on that page, which buyer questions they fail to answer, and how that affects the page's visibility in search.

Built for the TinyFish x DTU buildathon (Technical track, Agentic App / Skill).

## The problem

AI tools see a page differently from a human. Prices injected by JavaScript, facts inside images, content in collapsed tabs and bot walls all make a page unreadable to them. Most SEO tools give generic advice and never connect readability to how the page actually ranks.

## What it does

Fourteen steps (eight core agents plus supporting checks) share one JSON audit state and produce a short, evidence-backed report.

| Agent | Job |
| --- | --- |
| Fetcher | Fetches the page the way an AI tool extracts it (TinyFish Fetch) |
| Visitor | Renders the page in a real browser, opens tabs and accordions, records hidden text |
| Missing-Facts | Diffs rendered text against fetched text and labels each lost fact with one cause |
| Content Survival | Reports which tables, tabs, accordions and images do not survive extraction |
| Query Discovery | Proposes labelled queries and finds the page's rank for each (TinyFish Search) |
| Question Miner | Collects the questions that outranking pages answer |
| Interrogator | Answers each question from the fetched text only, and must give a verbatim quote |
| Skeptic | Tries to disprove findings and re-asks unanswered questions to catch unstable answers |
| Benchmark | Compares structure and coverage with the outranking pages |
| Control Group | Runs the same rendered-vs-fetched check on rivals |
| Crawl Access | Checks robots.txt, sitemap.xml, llms.txt and eight AI crawlers |
| Structured Data | Checks JSON-LD and Open Graph, and writes the missing snippet |
| Hidden Scan | Flags hidden or off-screen text and instruction-like strings aimed at AI readers |
| Report Writer | Assembles the report and drops any finding without evidence |

**Gap causes.** Every lost fact gets exactly one cause: JavaScript-injected, in an image or PDF, in a collapsed element, blocked, or not on the page. Each cause has its own fix.

**Evidence rule.** Every finding carries a quote or data point. Interrogator answers only count if the quote appears in the fetched text and holds across repeated runs.

**Closed loop.** After the owner applies a fix, the dashboard can re-check the live page and show which gaps closed.

**Fallbacks.** If the LLM is busy or a step fails, the audit continues with deterministic fallbacks (queries from the page title, a generic buyer checklist, fixes from the findings) so a report is always produced.

## Architecture

```
frontend (React + Vite)  --/api-->  backend (FastAPI)
                                      |-- agents/    one module per agent
                                      |-- services/  TinyFish, Gemini, text utils, pipeline
                                      '-- schemas/   shared audit state and API models
```

- **TinyFish Fetch** reads the audited page and the rival pages.
- **TinyFish Search** finds queries, ranks and rivals.
- **TinyFish Browser** provides the remote browser for the Visitor. If it fails, the Visitor retries in local Chromium.
- **Gemini** drives query discovery, question mining, interrogation and fix writing.

## Getting started

### Prerequisites

- Python 3.12
- Node.js 20 or later
- A TinyFish API key from [agent.tinyfish.ai/api-keys](https://agent.tinyfish.ai/api-keys)
- A Gemini API key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### Backend

```powershell
cd backend
py -3.12 -m venv .   # skip if the venv already exists
Scripts\python.exe -m pip install -r requirements.txt
Scripts\python.exe -m playwright install chromium
copy .env.example .env   # then add your keys
Scripts\python.exe -m uvicorn app.main:app --reload
```

The API runs on http://localhost:8000.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The dev server proxies `/api` to the backend.

### Configuration

Set these in `backend/.env`:

| Variable | Purpose | Default |
| --- | --- | --- |
| `TINYFISH_API_KEY` | TinyFish Search, Fetch and Browser | required |
| `GEMINI_API_KEY` | LLM calls | required |
| `LLM_MODEL` | Gemini model name | `gemini-flash-latest` |

Limits such as `MAX_RIVALS`, `MAX_QUERIES`, `MAX_QUESTIONS` and `INTERROGATION_PASSES` are in `backend/app/core/config.py` and can also be set as environment variables.

## API

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/audits` | Start an audit. Body: `{"url": "...", "target_query": "..."}` (query optional) |
| GET | `/api/audits/{id}` | Job status, per-agent progress, raw state and report |
| GET | `/api/audits/{id}/report.md` | Report as Markdown |
| POST | `/api/audits/{id}/verify` | Re-check the live page and report which gaps closed |
| GET | `/health` | Health check |

Example:

```powershell
curl -X POST http://localhost:8000/api/audits -H "content-type: application/json" `
  -d '{"url":"https://example.com","target_query":"standing desk"}'
```

## Project structure

```
backend/
  app/
    agents/     fetcher, visitor, missing_facts, content_survival, query_discovery, ...
    api/        FastAPI routes
    core/       settings
    schemas/    audit state and API models
    services/   tinyfish, llm, http, text, pipeline, verify
  tests/
frontend/
  src/
    components/ landing page, dashboard, findings, evidence
    components/cards/  dashboard cards
reports/        saved example reports
```

## Testing

```powershell
cd backend
Scripts\python.exe -m pytest
```

## Limitations

- Rival comparison uses three to five pages, so the readability-versus-ranking finding is indicative, not proof.
- Text inside images is flagged but not read (no OCR).
- Sites that block bots are reported as blocked, which is the finding.
- Audit history in the dashboard is stored in the browser, and audit jobs live in backend memory, so they reset on server restart.
- A full audit takes about two to four minutes and uses TinyFish and Gemini credits.

## Roadmap

- MCP tool wrapper so other agents can call the auditor
- Vision pass to read text inside images
- Scheduled re-audits that alert when a deploy breaks AI readability
