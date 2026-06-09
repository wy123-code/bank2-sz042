import pickle
from pathlib import Path

import pandas as pd

MODEL_DIR = Path(__file__).parent.parent / "models"
MODEL_PATH = MODEL_DIR / "best_model.pkl"


class PredictionError(Exception):
    """预测异常。"""

    pass


class Predictor:
    """银行营销认购预测器。"""

    def __init__(self, model_path: Path | None = None):
        self._model_path = model_path or MODEL_PATH
        self._loaded = False
        self._model = None
        self._encoders = None
        self._scaler = None
        self._feature_cols = None
        self._model_name = None
        self._auc = None
        self._f1 = None

    def load(self):
        """加载模型文件。"""
        if not self._model_path.exists():
            raise PredictionError(
                f"模型文件未找到: {self._model_path}。请先运行 python -m src.model_trainer"
            )
        with open(self._model_path, "rb") as f:
            artifact = pickle.load(f)
        self._model = artifact["model"]
        self._encoders = artifact["encoders"]
        self._scaler = artifact["scaler"]
        self._feature_cols = artifact["feature_cols"]
        self._model_name = artifact["model_name"]
        self._auc = artifact["auc"]
        self._f1 = artifact["f1"]
        self._loaded = True

    @property
    def model_info(self) -> dict:
        if not self._loaded:
            self.load()
        return {
            "model_name": self._model_name,
            "auc": self._auc,
            "f1": self._f1,
        }

    def predict(self, features: dict) -> dict:
        """对单条特征字典进行预测,返回预测结果和概率。"""
        if not self._loaded:
            self.load()

        # 构建 DataFrame
        df = pd.DataFrame([features])
        for col in self._feature_cols:
            if col not in df.columns:
                df[col] = 0

        # 标签编码分类特征
        for col, le in self._encoders.items():
            if col in df.columns:
                raw_val = str(df[col].iloc[0])
                if raw_val in le.classes_:
                    df[col] = le.transform([raw_val])[0]
                else:
                    df[col] = 0

        # 标准化
        X = self._scaler.transform(df[self._feature_cols])

        proba = float(self._model.predict_proba(X)[0, 1])
        pred = int(proba >= 0.5)

        return {
            "subscribe": "yes" if pred == 1 else "no",
            "subscribe_cn": "预计会认购" if pred == 1 else "预计不会认购",
            "probability": round(proba, 4),
            "confidence": round(max(proba, 1 - proba) * 100, 1),
        }


_global_predictor: Predictor | None = None


def get_predictor() -> Predictor:
    """获取全局单例预测器。"""
    global _global_predictor
    if _global_predictor is None:
        _global_predictor = Predictor()
        _global_predictor.load()
    return _global_predictor
