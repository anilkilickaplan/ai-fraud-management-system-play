"""
Mock Stripe `payment_intent.succeeded` gönderir; uygulama shadow logunda [SHADOW] satırını basar.

Çalıştırma (proje kökü): python test_model.py
"""

from fastapi.testclient import TestClient

from app.main import app


def build_payload(
    *,
    amount: float = 450.00,
    card_country: str = "ES",
    ip_country: str = "TR",
    email_type: str = "common",
    customer_age_days: int = 2,
) -> dict:
    amount_cents = int(round(amount * 100))
    return {
        "id": "evt_test_shadow_1",
        "type": "payment_intent.succeeded",
        "data": {
            "object": {
                "id": "pi_test_123",
                "amount": amount_cents,
                "currency": "usd",
                "metadata": {
                    "card_country": card_country,
                    "ip_country": ip_country,
                    "email_type": email_type,
                    "customer_age_days": str(customer_age_days),
                },
            }
        },
    }


def main() -> None:
    with TestClient(app) as client:
        r = client.post("/webhook/stripe", json=build_payload())
        print("HTTP", r.status_code, r.json())


if __name__ == "__main__":
    main()
