import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

from app.config import DEFAULT_DATA_PATH, PROJECT_ROOT, SHADOW_LOG_PATH
from app.model.service import init_model
from app.shadow_logger import setup_shadow_logging
from app.webhooks.stripe import router as stripe_webhook_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv(PROJECT_ROOT / ".env")
    data_path = Path(os.environ.get("FRAUD_DATA_PATH", str(DEFAULT_DATA_PATH)))
    init_model(data_path)
    setup_shadow_logging(SHADOW_LOG_PATH)
    yield


app = FastAPI(title="Fraud Shadow API", lifespan=lifespan)
app.include_router(stripe_webhook_router, prefix="/webhook", tags=["webhooks"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
