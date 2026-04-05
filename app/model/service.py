from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from app.model.train import CATEGORICAL_FEATURES, NUMERIC_FEATURES, train_from_csv

_service: FraudModelService | None = None


class FraudModelService:
    def __init__(self, pipeline: Pipeline) -> None:
        self._pipeline = pipeline

    def fraud_probability_percent(self, row: dict[str, Any]) -> float:
        """Return P(fraud) as a float in [0, 100]."""
        feature_cols = NUMERIC_FEATURES + CATEGORICAL_FEATURES
        X = pd.DataFrame([{k: row[k] for k in feature_cols}])
        proba = self._pipeline.predict_proba(X)[0]
        classes = self._pipeline.named_steps["classifier"].classes_
        fraud_idx = int(np.where(classes == 1)[0][0])
        return float(proba[fraud_idx] * 100.0)


def init_model(csv_path: Path | None = None) -> None:
    global _service
    path = csv_path or Path(__file__).resolve().parent.parent.parent / "ai_studio_code.csv"
    pipeline = train_from_csv(path)
    _service = FraudModelService(pipeline)


def get_model_service() -> FraudModelService:
    if _service is None:
        raise RuntimeError("Model not initialized; call init_model() during startup.")
    return _service
