# AI-Readability & Visibility Auditor

Paste a URL; seven agents compare what a browser renders with what TinyFish Fetch extracts, mine rival questions via Search, and produce an evidence-backed report.

## Run

```powershell
# backend (needs backend\.env, see .env.example)
cd backend
Scripts\python.exe -m pip install -r requirements.txt
Scripts\python.exe -m playwright install chromium   # only for the local-browser fallback
Scripts\python.exe -m uvicorn app.main:app --reload

# frontend
cd frontend
npm install
npm run dev     # http://localhost:5173
```

## Layout

- `backend/app/agents/` - Fetcher, Visitor, Missing-Facts, Query Discovery, Question Miner, Interrogator, Control Group, Report Writer
- `backend/app/services/` - TinyFish wrapper, LLM client, text utils, pipeline
- `backend/app/schemas/` - shared audit state and API models
- `frontend/src/` - React UI (form, live agent progress, report)
