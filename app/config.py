import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_PATH = PROJECT_ROOT / "ai_studio_code.csv"
SHADOW_LOG_PATH = PROJECT_ROOT / "logs" / "shadow_fraud.log"


def get_supabase_url() -> str | None:
    v = os.environ.get("SUPABASE_URL")
    return v.strip() if v else None


def get_supabase_key() -> str | None:
    """Prefer service role on server; fall back to anon public key."""
    v = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
    return v.strip() if v else None
