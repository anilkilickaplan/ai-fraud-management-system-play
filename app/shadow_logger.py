from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import SHADOW_LOG_PATH, get_supabase_key, get_supabase_url

_shadow_file_logger = logging.getLogger("shadow_fraud")
_supabase_client: Any = None


def compute_business_decision(
    fraud_probability_percent: float, amount: float
) -> dict[str, Any]:
    """
    p < 30: APPROVE; 30 <= p <= 70: REVIEW + $5 manual cost; p > 70: REJECT + prevented_loss = amount * 1.5.
    """
    p = fraud_probability_percent
    if p < 30:
        return {
            "decision": "APPROVE",
            "prevented_loss": 0.0,
            "manual_review_cost": 0.0,
        }
    if p <= 90:
        return {
            "decision": "REVIEW",
            "prevented_loss": 0.0,
            "manual_review_cost": 5.0,
        }
    return {
        "decision": "REJECT",
        "prevented_loss": round(float(amount) * 1.5, 4),
        "manual_review_cost": 0.0,
    }


def _init_supabase_client() -> None:
    global _supabase_client
    url = get_supabase_url()
    key = get_supabase_key()
    if not url or not key:
        _supabase_client = None
        return
    try:
        from supabase import create_client

        _supabase_client = create_client(url, key)
    except Exception as exc:
        _shadow_file_logger.warning("Supabase client init failed: %s", exc)
        _supabase_client = None


def setup_shadow_logging(log_file: Path | None = None) -> None:
    path = log_file or SHADOW_LOG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    if not any(isinstance(h, logging.FileHandler) for h in _shadow_file_logger.handlers):
        fh = logging.FileHandler(path, encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(message)s"))
        _shadow_file_logger.addHandler(fh)
        _shadow_file_logger.setLevel(logging.INFO)
    _init_supabase_client()


def _insert_fraud_log_row(row: dict[str, Any]) -> None:
    if _supabase_client is None:
        return
    try:
        _supabase_client.table("fraud_logs").insert(row).execute()
    except Exception as exc:
        _shadow_file_logger.warning("Supabase fraud_logs insert failed: %s", exc)


def log_shadow_fraud_assessment(
    *,
    fraud_probability_percent: float,
    event_id: str | None,
    payment_intent_id: str | None,
    extra: dict[str, Any] | None = None,
) -> None:
    merged = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event_id": event_id,
        "payment_intent_id": payment_intent_id,
        "fraud_probability_percent": round(fraud_probability_percent, 4),
        **(extra or {}),
    }
    amount = float(merged.get("amount") or 0.0)
    impact = compute_business_decision(fraud_probability_percent, amount)
    payload: dict[str, Any] = {**merged, **impact}
    line = json.dumps(payload, ensure_ascii=False)
    print(f"[SHADOW] Fraud Probability: {fraud_probability_percent:.2f}/100 | {line}")
    _shadow_file_logger.info(line)
    _insert_fraud_log_row(payload)
