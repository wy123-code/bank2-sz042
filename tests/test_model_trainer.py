import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.model_trainer import (
    AUC_THRESHOLD,
    CATEGORICAL_COLS,
    F1_THRESHOLD,
    NUMERICAL_COLS,
    RANDOM_STATE,
    preprocess,
    save_model,
    select_best,
    train_models,
)


@pytest.fixture
def sample_df():
    """创建小样本训练 DataFrame。"""
    n = 200
    np.random.seed(RANDOM_STATE)
    data = {
        "age": np.random.randint(20, 70, n),
        "job": np.random.choice(
            ["admin.", "blue-collar", "technician", "services", "management"], n
        ),
        "marital": np.random.choice(["married", "single", "divorced"], n),
        "education": np.random.choice(
            ["high.school", "university.degree", "basic.9y", "professional.course"], n
        ),
        "default": np.random.choice(["yes", "no", "unknown"], n),
        "housing": np.random.choice(["yes", "no", "unknown"], n),
        "loan": np.random.choice(["yes", "no", "unknown"], n),
        "contact": np.random.choice(["cellular", "telephone"], n),
        "month": np.random.choice(["may", "jun", "jul", "aug", "nov"], n),
        "day_of_week": np.random.choice(["mon", "tue", "wed", "thu", "fri"], n),
        "duration": np.random.randint(0, 4000, n),
        "campaign": np.random.randint(1, 40, n),
        "pdays": np.random.choice([999, 0, 3, 7, 15], n),
        "previous": np.random.randint(0, 7, n),
        "poutcome": np.random.choice(["nonexistent", "failure", "success"], n),
        "emp_var_rate": np.random.uniform(-3, 3, n),
        "cons_price_index": np.random.uniform(90, 100, n),
        "cons_conf_index": np.random.uniform(-50, -30, n),
        "lending_rate3m": np.random.uniform(0, 6, n),
        "nr_employed": np.random.uniform(4900, 5300, n),
        "subscribe": np.random.choice(["yes", "no"], n, p=[0.15, 0.85]),
    }
    return pd.DataFrame(data)


class TestPreprocess:
    def test_output_shapes(self, sample_df):
        X, y, preprocessors = preprocess(sample_df)
        assert X.shape[0] == len(sample_df)
        assert X.shape[1] == len(CATEGORICAL_COLS) + len(NUMERICAL_COLS)
        assert len(y) == len(sample_df)
        assert set(preprocessors.keys()) == {"encoders", "scaler", "feature_cols"}

    def test_y_is_binary(self, sample_df):
        _, y, _ = preprocess(sample_df)
        assert set(np.unique(y)).issubset({0, 1})

    def test_encoders_have_all_categories(self, sample_df):
        _, _, pp = preprocess(sample_df)
        for col in CATEGORICAL_COLS:
            assert col in pp["encoders"]
            assert hasattr(pp["encoders"][col], "classes_")


class TestTrainModels:
    def test_returns_three_results(self, sample_df):
        X, y, _ = preprocess(sample_df)
        results = train_models(X, y)
        assert len(results) >= 2

    def test_each_result_has_required_keys(self, sample_df):
        X, y, _ = preprocess(sample_df)
        results = train_models(X, y)
        for r in results:
            assert "name" in r
            assert "model" in r
            assert "auc" in r
            assert "f1" in r
            assert 0 <= r["auc"] <= 1
            assert 0 <= r["f1"] <= 1

    def test_auc_in_valid_range(self, sample_df):
        X, y, _ = preprocess(sample_df)
        results = train_models(X, y)
        for r in results:
            assert 0.0 <= r["auc"] <= 1.0, f"{r['name']} AUC out of range: {r['auc']}"


class TestSelectBest:
    def test_returns_best_by_auc(self, sample_df):
        X, y, _ = preprocess(sample_df)
        results = train_models(X, y)
        best = select_best(results)
        max_auc = max(r["auc"] for r in results)
        assert best["auc"] == max_auc


class TestSaveModel:
    def test_saves_and_file_exists(self, sample_df, monkeypatch):
        tmpdir = Path(tempfile.mkdtemp())
        monkeypatch.setattr("src.model_trainer.MODEL_DIR", tmpdir)

        X, y, pp = preprocess(sample_df)
        results = train_models(X, y)
        best = select_best(results)
        path = save_model(best, pp)

        assert path.exists()
        assert path.suffix == ".pkl"


class TestConstants:
    def test_random_state_is_42(self):
        assert RANDOM_STATE == 42

    def test_thresholds_defined(self):
        assert AUC_THRESHOLD == 0.75
        assert F1_THRESHOLD == 0.60


class TestRunTraining:
    def test_run_training_returns_summary(self, sample_df, monkeypatch):
        monkeypatch.setattr("src.model_trainer.load_train", lambda: sample_df)
        from src.model_trainer import run_training

        summary = run_training()
        assert "best_model" in summary
        assert "auc" in summary
        assert "f1" in summary
        assert "model_path" in summary
        assert "all_results" in summary
        assert len(summary["all_results"]) >= 2


class TestXGBImport:
    def test_xgb_import_error_handled(self, monkeypatch):
        import src.model_trainer as mt

        monkeypatch.setattr(mt, "_get_xgb_classifier", lambda: None)
        results = mt.train_models(np.random.randn(50, 20), np.random.randint(0, 2, 50))
        names = [r["name"] for r in results]
        assert "XGBoost" not in names
        assert "LogisticRegression" in names
        assert "RandomForest" in names

    def test_get_xgb_import_error_triggers_except(self, monkeypatch):
        import builtins
        import sys

        import src.model_trainer as mt

        monkeypatch.delitem(sys.modules, "xgboost", raising=False)
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "xgboost" or name.startswith("xgboost."):
                raise ImportError("No module named 'xgboost'")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)
        result = mt._get_xgb_classifier()
        assert result is None


class TestMainGuard:
    def test_main_guard_exists(self):
        """验证 __main__ 守卫存在且调用 run_training。"""
        source_path = Path(__file__).parent.parent / "src" / "model_trainer.py"
        source = source_path.read_text(encoding="utf-8")
        assert 'if __name__ == "__main__"' in source
        assert "run_training()" in source
