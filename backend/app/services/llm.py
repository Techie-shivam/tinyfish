import json
import re
import time
from functools import lru_cache

from google import genai
from google.genai import errors, types

from app.core.config import get_settings


@lru_cache
def _client() -> genai.Client:
    return genai.Client(api_key=get_settings().gemini_api_key or None)


RETRY_CODES = {429, 500, 503}
FALLBACK_MODEL = "gemini-flash-lite-latest"


def _generate(model: str, system: str, prompt: str, max_tokens: int):
    cfg = types.GenerateContentConfig(
        system_instruction=system, response_mime_type="application/json",
        max_output_tokens=max_tokens, temperature=0.2,
    )
    for attempt in range(4):
        try:
            return _client().models.generate_content(model=model, contents=prompt, config=cfg)
        except errors.APIError as exc:
            if exc.code not in RETRY_CODES or attempt == 3:
                raise
            time.sleep(2 ** attempt * 2)  # 2s, 4s, 8s


def complete_json(system: str, prompt: str, usage: dict[str, int] | None = None, max_tokens: int = 4000,
                  key: str | None = None):
    """Ask Gemini for JSON only; returns parsed data. Retries busy errors, then tries a lighter model."""
    model = get_settings().llm_model
    try:
        resp = _generate(model, system, prompt, max_tokens)
    except errors.APIError as exc:
        if exc.code not in RETRY_CODES or model == FALLBACK_MODEL:
            raise
        resp = _generate(FALLBACK_MODEL, system, prompt, max_tokens)
    if usage is not None and resp.usage_metadata:
        usage["input"] += resp.usage_metadata.prompt_token_count or 0
        usage["output"] += resp.usage_metadata.candidates_token_count or 0
    raw = re.sub(r"^```(?:json)?|```$", "", (resp.text or "").strip(), flags=re.M).strip()
    data = json.loads(raw)
    if key is None:
        return data
    if isinstance(data, dict):  # {"queries": [...]} or any single list value
        data = data.get(key) or next((v for v in data.values() if isinstance(v, list)), [])
    return data if isinstance(data, list) else []
