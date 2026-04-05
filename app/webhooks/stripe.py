from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.model.service import get_model_service
from app.shadow_logger import log_shadow_fraud_assessment

router = APIRouter()


def _parse_int(value: str | None, default: int) -> int:
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _payment_intent_to_features(pi: dict[str, Any]) -> dict[str, Any]:
    """
    Map Stripe PaymentIntent fields + metadata to training feature names.
    Amount: major units (dataset uses e.g. 1250.50). Stripe uses minor units.
    Country / email / age: prefer metadata keys used for fraud signals.
    """
    amount_minor = int(pi.get("amount") or 0)
    currency = (pi.get("currency") or "usd").lower()
    zero_decimal = currency in {"bif", "clp", "djf", "gnf", "jpy", "kmf", "krw", "mga", "pyg", "rwf", "ugx", "vnd", "vuv", "xaf", "xof", "xpf"}
    if zero_decimal:
        amount = float(amount_minor)
    else:
        amount = amount_minor / 100.0

    raw_md = pi.get("metadata") or {}
    md = dict(raw_md) if not isinstance(raw_md, dict) else raw_md

    card_country = (md.get("card_country") or md.get("card_country_code") or "US").upper()
    ip_country = (md.get("ip_country") or card_country).upper()
    email_type = (md.get("email_type") or "common").lower()
    if email_type not in {"common", "professional", "disposable"}:
        email_type = "common"
    customer_age_days = _parse_int(md.get("customer_age_days"), 0)

    return {
        "amount": amount,
        "card_country": card_country,
        "ip_country": ip_country,
        "email_type": email_type,
        "customer_age_days": customer_age_days,
    }


@router.post("/stripe")
async def stripe_webhook(request: Request) -> dict[str, str]:
    # payload = await request.body()
    # sig_header = request.headers.get("stripe-signature")
    # if not sig_header:
    #     raise HTTPException(status_code=400, detail="Missing Stripe-Signature header")

    # try:
    #     event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    # except ValueError as e:
    #     raise HTTPException(status_code=400, detail=f"Invalid payload: {e}") from e
    # except SignatureVerificationError as e:
    #     raise HTTPException(status_code=400, detail=f"Invalid signature: {e}") from e

    event = await request.json()

    if event["type"] != "payment_intent.succeeded":
        return {"status": "ignored", "reason": f"event_type={event['type']}"}

    pi = event["data"]["object"]
    features = _payment_intent_to_features(pi)
    svc = get_model_service()
    fraud_pct = svc.fraud_probability_percent(features)

    log_shadow_fraud_assessment(
        fraud_probability_percent=fraud_pct,
        event_id=event.get("id"),
        payment_intent_id=pi.get("id"),
        extra={
            "amount": features["amount"],
            "card_country": features["card_country"],
            "ip_country": features["ip_country"],
            "email_type": features["email_type"],
            "customer_age_days": features["customer_age_days"],
        },
    )

    return {"status": "ok", "shadow_logged": "true"}
