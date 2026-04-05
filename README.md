# AI Fraud Management System

**Backend API for ML-driven fraud detection in shadow mode** — Random Forest scoring, Stripe webhooks, structured logging, and optional Supabase integration. Pairs with a separate [dashboard](https://github.com/anilkilickaplan/ai-fraud-control-center) (Lovable + Supabase) for analyst workflows and labeling.

---

## Overview

This project demonstrates how a **rule-based fraud stack** can evolve into a **machine-learning decision engine** without forcing a risky big-bang cutover. The API scores transactions and records outcomes in **shadow mode** (observe and learn before committing to automated blocks), so product and risk teams can measure impact before changing customer-facing behavior.

---

## The problem

Fraud systems sit at the intersection of **revenue**, **customer trust**, and **operations**. Decisions are rarely “correct vs. wrong” — they are trade-offs:

| Trade-off | What it means |
|-----------|----------------|
| **Fraud loss** | Letting fraud through costs real money (modeled here as a multiple of transaction amount). |
| **False positives** | Blocking good customers erodes lifetime value and support load. |
| **Operational overhead** | Manual review has a fixed cost per case and does not scale linearly with volume. |

The product framing is explicit: **optimize economic outcomes**, not model accuracy in isolation.

---

## Product approach

- **Shadow mode first** — Score and log predictions alongside existing rules; compare outcomes without changing authorization in production until stakeholders are confident.
- **Stripe-native hooks** — Webhooks align scoring with real payment events so the pipeline reflects how money actually moves.
- **Analyst-in-the-loop** — A labeling path (via the dashboard + Supabase) turns human decisions into **ground truth** for model improvement rather than one-off overrides.

---

## Architecture & tech stack

| Layer | Role |
|-------|------|
| **ML** | Scikit-learn **Random Forest** trained on historical transaction-style data. |
| **API** | **FastAPI** (Python) — webhooks, health checks, shadow logging. |
| **Data** | **Supabase (PostgreSQL)** — persistence and labeling where integrated. |
| **UI** | **Lovable** (React / Vite) — financial impact views and human-in-the-loop flows — [source: `ai-fraud-control-center`](https://github.com/anilkilickaplan/ai-fraud-control-center). |

---

## Human-in-the-loop & continuous improvement

When an analyst **confirms or rejects** a suspicious transaction in the dashboard, **`actual_label`** is updated in Supabase. A periodic **retrain** job (e.g. weekly) can consume those labels to **reduce drift** and adapt to new fraud patterns — closing the loop between operations and the model.

---

## Dashboard (frontend)

The interactive **control center** lives in a dedicated repository:

**[github.com/anilkilickaplan/ai-fraud-control-center](https://github.com/anilkilickaplan/ai-fraud-control-center)**

Use it to showcase the full product story: UI + data + this backend as the scoring and integration layer.

---

## Local development

**Run the API**

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # add Supabase keys if using Supabase
uvicorn app.main:app --reload
```

**Run tests**

```bash
python test_model.py
```

---

## First-time Git push (optional)

If this repo is new on your machine, create an empty remote repository, then:

```bash
git remote add origin https://github.com/<YOUR_USER>/<YOUR_REPO>.git
git branch -M main
git push -u origin main
```
