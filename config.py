"""config.py — central settings loader for PR Risk Scorer.

All paths and secrets are read from the .env file (or environment variables).
No hardcoded paths anywhere in the codebase — always import from here.
"""

from pathlib import Path

from dotenv import load_dotenv
import os

# Load .env from the project root (the directory containing this file).
_ROOT = Path(__file__).parent
load_dotenv(_ROOT / ".env")


def _require(key: str) -> str:
    """Return the value of an env variable, raising clearly if missing."""
    value = os.getenv(key)
    if value is None:
        raise EnvironmentError(
            f"Required environment variable '{key}' is not set. "
            "Copy .env.example to .env and fill in the values."
        )
    return value


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_DIR: Path = Path(os.getenv("DATA_DIR", str(_ROOT / "data")))
MODELS_DIR: Path = Path(os.getenv("MODELS_DIR", str(_ROOT / "models" / "artefacts")))
INDEX_DIR: Path = Path(os.getenv("INDEX_DIR", str(_ROOT / "rag" / "index")))
AUDIT_DB_PATH: Path = Path(
    os.getenv("AUDIT_DB_PATH", str(_ROOT / "audit.db"))
)

# ---------------------------------------------------------------------------
# Secrets
# ---------------------------------------------------------------------------
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")  # empty → local fallback
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

# ---------------------------------------------------------------------------
# Model / retrieval settings
# ---------------------------------------------------------------------------
SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.75"))
