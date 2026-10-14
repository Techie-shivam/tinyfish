import json
import re

import anthropic

from app.core.config import get_settings



def _client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=get_settings().anthropic_api_key or None)


def complete_json(system: str, prompt: str, usage: dict[str, int] | None = None, max_tokens: int = 4000):
    """Ask the LLM for JSON only; returns parsed data. Adds token counts to `usage`."""
    msg = _client().messages.create(
        model=get_settings().llm_model, max_tokens=max_tokens,
        system=system + "\nRespond with valid JSON only, no prose or code fences.",
        messages=[{"role": "user", "content": prompt}],
    )
    if usage is not None:
        usage["input"] += msg.usage.input_tokens
        usage["output"] += msg.usage.output_tokens
    raw = "".join(b.text for b in msg.content if b.type == "text").strip()
    raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.M).strip()
    return json.loads(raw)
