"""Classical molecular baselines for Milestone 1."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, Ridge

from moltrustbench.chem import fingerprint_array


@dataclass
class TrainedModel:
    model_id: str
    task_type: str
    backend: str
    estimator: object
    allow_fallback: bool


def infer_task_type(y: pd.Series) -> str:
    values = y.dropna().unique()
    if len(values) <= 2 and set(values).issubset({0, 1, 0.0, 1.0, False, True}):
        return "classification"
    return "regression"


def featurize(smiles: list[str], *, allow_fallback: bool = False) -> np.ndarray:
    return fingerprint_array(smiles, allow_fallback=allow_fallback, n_bits=1024)


def fit_classical_model(
    train_df: pd.DataFrame,
    *,
    model_id: str,
    label_col: str = "label",
    allow_fallback: bool = False,
) -> TrainedModel:
    x_train = featurize(train_df["standard_smiles"].tolist(), allow_fallback=allow_fallback)
    y_train = train_df[label_col].astype(float)
    task_type = infer_task_type(y_train)
    if model_id == "morgan_logreg":
        if task_type != "classification":
            estimator = Ridge(alpha=1.0)
            backend = "sklearn_ridge_logreg_regression_fallback"
        else:
            estimator = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=0)
            backend = "sklearn_logistic_regression"
    elif model_id == "morgan_ridge":
        estimator = Ridge(alpha=1.0)
        backend = "sklearn_ridge"
    elif model_id == "morgan_xgb":
        try:
            from xgboost import XGBClassifier, XGBRegressor

            if task_type == "classification":
                estimator = XGBClassifier(n_estimators=50, max_depth=3, learning_rate=0.08, eval_metric="logloss", random_state=0)
            else:
                estimator = XGBRegressor(n_estimators=50, max_depth=3, learning_rate=0.08, random_state=0)
            backend = "xgboost"
        except Exception:
            estimator = GradientBoostingClassifier(random_state=0) if task_type == "classification" else GradientBoostingRegressor(random_state=0)
            backend = "sklearn_gradient_boosting_xgb_fallback"
    else:
        raise ValueError(f"Unknown model id: {model_id}")

    estimator.fit(x_train, y_train)
    return TrainedModel(model_id=model_id, task_type=task_type, backend=backend, estimator=estimator, allow_fallback=allow_fallback)


def predict_model(model: TrainedModel, df: pd.DataFrame) -> pd.DataFrame:
    x = featurize(df["standard_smiles"].tolist(), allow_fallback=model.allow_fallback)
    if model.task_type == "classification" and hasattr(model.estimator, "predict_proba"):
        pred = model.estimator.predict_proba(x)[:, 1]
    else:
        pred = model.estimator.predict(x)
    out = df[["source_name", "task_name", "row_id", "split", "label", "standard_smiles", "exact_exposed", "scaffold_exposed", "max_nn_similarity_before_cutoff"]].copy()
    out["prediction"] = pred
    out["model_id"] = model.model_id
    out["model_backend"] = model.backend
    out["task_type"] = model.task_type
    return out
