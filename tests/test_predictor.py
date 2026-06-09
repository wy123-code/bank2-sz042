import pickle
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler

from src.predictor import PredictionError, Predictor


FEATURE_COLS = [
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


@pytest.fixture
def model_path():
    """创建包含模拟模型文件的临时目录。"""
    tmpdir = Path(tempfile.mkdtemp())
    model_file = tmpdir / "best_model.pkl"

    encoders = {}
    for col in [
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
    ]:
        le = LabelEncoder()
        le.fit(
            [
                "admin.",
                "married",
                "high.school",
                "no",
                "yes",
                "cellular",
                "may",
                "mon",
                "nonexistent",
            ]
        )
        encoders[col] = le

    scaler = StandardScaler()
    X_dummy = pd.DataFrame(np.random.randn(50, len(FEATURE_COLS)), columns=FEATURE_COLS)
    scaler.fit(X_dummy)

    rf = RandomForestClassifier(n_estimators=10, random_state=42)
    X_train = pd.DataFrame(
        np.random.randn(100, len(FEATURE_COLS)), columns=FEATURE_COLS
    )
    y_train = np.random.randint(0, 2, 100)
    rf.fit(X_train, y_train)

    artifact = {
        "model": rf,
        "encoders": encoders,
        "scaler": scaler,
        "feature_cols": FEATURE_COLS,
        "model_name": "RandomForest",
        "auc": 0.89,
        "f1": 0.52,
    }
    with open(model_file, "wb") as f:
        pickle.dump(artifact, f)

    return model_file


class TestPredictor:
    def test_load_success(self, model_path):
        p = Predictor(model_path)
        p.load()
        assert p._loaded

    def test_load_file_not_found(self):
        p = Predictor(Path("/nonexistent/model.pkl"))
        with pytest.raises(PredictionError, match="模型文件未找到"):
            p.load()

    def test_model_info(self, model_path):
        p = Predictor(model_path)
        info = p.model_info
        assert info["model_name"] == "RandomForest"
        assert info["auc"] == 0.89

    def test_predict_returns_expected_keys(self, model_path):
        p = Predictor(model_path)
        features = {
            "age": 40,
            "job": "admin.",
            "marital": "married",
            "education": "high.school",
            "default": "no",
            "housing": "yes",
            "loan": "no",
            "contact": "cellular",
            "month": "may",
            "day_of_week": "mon",
            "duration": 300,
            "campaign": 2,
            "pdays": 999,
            "previous": 0,
            "poutcome": "nonexistent",
            "emp_var_rate": 1.0,
            "cons_price_index": 93.0,
            "cons_conf_index": -38.0,
            "lending_rate3m": 4.0,
            "nr_employed": 5100.0,
        }
        result = p.predict(features)
        assert "subscribe" in result
        assert result["subscribe"] in ("yes", "no")
        assert "probability" in result
        assert 0 <= result["probability"] <= 1
        assert "confidence" in result
        assert 0 <= result["confidence"] <= 100

    def test_predict_handles_missing_fields(self, model_path):
        p = Predictor(model_path)
        result = p.predict({"age": 40})
        assert result["subscribe"] in ("yes", "no")

    def test_predict_handles_unknown_category(self, model_path):
        p = Predictor(model_path)
        result = p.predict(
            {
                "age": 40,
                "job": "astronaut",
                "marital": "married",
                "education": "high.school",
                "default": "no",
                "housing": "yes",
                "loan": "no",
                "contact": "cellular",
                "month": "may",
                "day_of_week": "mon",
                "duration": 300,
                "campaign": 2,
                "pdays": 999,
                "previous": 0,
                "poutcome": "nonexistent",
                "emp_var_rate": 1.0,
                "cons_price_index": 93.0,
                "cons_conf_index": -38.0,
                "lending_rate3m": 4.0,
                "nr_employed": 5100.0,
            }
        )
        assert result["subscribe"] in ("yes", "no")

    def test_predict_reloads_if_not_loaded(self, model_path):
        p = Predictor(model_path)
        assert not p._loaded
        p.predict({"age": 40})
        assert p._loaded


class TestGetPredictor:
    def test_returns_predictor_instance(self, model_path, monkeypatch):
        import src.predictor as sp

        monkeypatch.setattr(sp, "MODEL_PATH", model_path)
        # reset global singleton
        monkeypatch.setattr(sp, "_global_predictor", None)
        p = sp.get_predictor()
        assert p._loaded
        assert p.model_info["model_name"] == "RandomForest"

    def test_reuses_singleton(self, model_path, monkeypatch):
        import src.predictor as sp

        monkeypatch.setattr(sp, "MODEL_PATH", model_path)
        monkeypatch.setattr(sp, "_global_predictor", None)
        p1 = sp.get_predictor()
        p2 = sp.get_predictor()
        assert p1 is p2
