"""Central configuration for sql-insights-agent.

Values come from environment variables / .env. Importing this module must
never fail when python-dotenv is missing — dotenv is optional.
"""
import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # dotenv is optional; plain env vars still work
    pass


class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    z_threshold: float = float(os.getenv("Z_THRESHOLD", "2.5"))
    iqr_multiplier: float = float(os.getenv("IQR_MULTIPLIER", "1.5"))
    input_path: str = os.getenv("INPUT_PATH", "data/sample_metrics.csv")
    output_path: str = os.getenv("OUTPUT_PATH", "examples/sample_report.md")


settings = Settings()


def llm_enabled() -> bool:
    """True only when an OpenAI key is configured (optional LLM rewrite path)."""
    return bool(settings.openai_api_key)
