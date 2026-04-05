from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


NUMERIC_FEATURES = ["amount", "customer_age_days"]
CATEGORICAL_FEATURES = ["card_country", "ip_country", "email_type"]


def build_fraud_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", NUMERIC_FEATURES),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_FEATURES,
            ),
        ]
    )
    classifier = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
    )
    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )


def train_from_csv(csv_path: Path) -> Pipeline:
    df = pd.read_csv(csv_path)
    feature_cols = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    missing = [c for c in feature_cols + ["is_fraud"] if c not in df.columns]
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")

    X = df[feature_cols]
    y = df["is_fraud"].astype(int)

    pipeline = build_fraud_pipeline()
    pipeline.fit(X, y)
    return pipeline
