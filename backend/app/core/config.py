from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    tinyfish_api_key: str = ""
    anthropic_api_key: str = ""
    llm_model: str = "claude-sonnet-5-5"

    max_rivals: int = 3
    max_queries: int = 12
    max_questions: int = 15
    interrogation_passes: int = 2
    page_text_limit: int = 30000  # chars of page text sent to the LLM
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
