import pickle
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler

from .data_loader import load_train

MODEL_DIR = Path(__file__).parent.parent / "models"
RANDOM_STATE = 42
AUC_THRESHOLD = 0.75
F1_THRESHOLD = 0.60

CATEGORICAL_COLS = [
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "poutcome",
]

NUMERICAL_COLS = [
    "age",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "emp_var_rate",
    "cons_price_index",
    "cons_conf_index",
    "lending_rate3m",
    "nr_employed",
]


def preprocess(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, dict]:
    """预处理:标签编码分类特征,标准化数值特征。返回 X, y, 编码器字典。"""
    df = df.copy()
    encoders: dict[str, LabelEncoder] = {}

    for col in CATEGORICAL_COLS:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

    y = df["subscribe"].map({"yes": 1, "no": 0}).values

    feature_cols = CATEGORICAL_COLS + NUMERICAL_COLS
    scaler = StandardScaler()
    X = scaler.fit_transform(df[feature_cols])

    return X, y, {"encoders": encoders, "scaler": scaler, "feature_cols": feature_cols}


def _get_xgb_classifier():
    """创建 XGBoost 分类器,兼容 xgboost >= 2.0 各版本。"""
    try:
        from xgboost import XGBClassifier

        return XGBClassifier(
            n_estimators=100,
            random_state=RANDOM_STATE,
            eval_metric="logloss",
            scale_pos_weight=None,  # will be computed dynamically
        )
    except ImportError:
        return None


def train_models(X: np.ndarray, y: np.ndarray) -> list[dict]:
    """训练三个候选模型,返回各模型元信息列表。"""
    scale_pos_weight = (len(y) - y.sum()) / max(y.sum(), 1)

    models = [
        (
            "LogisticRegression",
            LogisticRegression(
                max_iter=2000,
                random_state=RANDOM_STATE,
                class_weight="balanced",
            ),
        ),
        (
            "RandomForest",
            RandomForestClassifier(
                n_estimators=100,
                random_state=RANDOM_STATE,
                class_weight="balanced",
            ),
        ),
    ]

    xgb = _get_xgb_classifier()
    if xgb is not None:
        xgb.set_params(scale_pos_weight=scale_pos_weight)
        models.append(("XGBoost", xgb))

    results = []
    for name, model in models:
        auc_scores = cross_val_score(model, X, y, cv=5, scoring="roc_auc")
        f1_scores = cross_val_score(model, X, y, cv=5, scoring="f1")
        mean_auc = float(np.mean(auc_scores))
        mean_f1 = float(np.mean(f1_scores))
        model.fit(X, y)
        results.append(
            {
                "name": name,
                "model": model,
                "auc": round(mean_auc, 4),
                "f1": round(mean_f1, 4),
            }
        )
        if mean_auc < AUC_THRESHOLD:
            warnings.warn(f"WARNING: {name} AUC={mean_auc:.4f} < {AUC_THRESHOLD}")
        if mean_f1 < F1_THRESHOLD:
            warnings.warn(f"WARNING: {name} F1={mean_f1:.4f} < {F1_THRESHOLD}")

    return results


def select_best(results: list[dict]) -> dict:
    """按 AUC 降序选最优模型,AUC 相同时按 F1 降序。"""
    return max(results, key=lambda r: (r["auc"], r["f1"]))


def save_model(best: dict, preprocessors: dict) -> Path:
    """保存最优模型和预处理器到 models/ 目录。"""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODEL_DIR / "best_model.pkl"
    artifact = {
        "model": best["model"],
        "encoders": preprocessors["encoders"],
        "scaler": preprocessors["scaler"],
        "feature_cols": preprocessors["feature_cols"],
        "model_name": best["name"],
        "auc": best["auc"],
        "f1": best["f1"],
    }
    with open(model_path, "wb") as f:
        pickle.dump(artifact, f)
    return model_path


def run_training() -> dict:
    """完整训练流程:加载数据->预处理->训练->选最优->保存。返回结果摘要。"""
    print("=" * 50)
    print("Bank Marketing Subscription Model Training")
    print("=" * 50)

    df = load_train()
    print(f"Data loaded: {len(df)} records")

    X, y, preprocessors = preprocess(df)
    print(f"Features: {X.shape[1]}, Positive rate: {y.mean():.2%}")

    results = train_models(X, y)

    print("\nModel Evaluation:")
    print("-" * 40)
    best = select_best(results)
    for r in results:
        flag = " [BEST]" if r["name"] == best["name"] else ""
        print(f"  {r['name']:25s}  AUC={r['auc']:.4f}  F1={r['f1']:.4f}{flag}")

    print(f"\nBest model: {best['name']} (AUC={best['auc']:.4f}, F1={best['f1']:.4f})")

    path = save_model(best, preprocessors)
    print(f"Model saved: {path}")

    return {
        "best_model": best["name"],
        "auc": best["auc"],
        "f1": best["f1"],
        "model_path": str(path),
        "all_results": [
            {"name": r["name"], "auc": r["auc"], "f1": r["f1"]} for r in results
        ],
    }


if __name__ == "__main__":  # pragma: no cover
    run_training()
