import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
from importlib import util

import pandas as pd

from src.predictor import PredictionError


def _make_mock_df():
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "age": [30, 45, 28, 50, 33],
            "job": ["admin.", "blue-collar", "technician", "admin.", "services"],
            "marital": ["married", "single", "married", "divorced", "single"],
            "education": [
                "high.school",
                "university.degree",
                "basic.9y",
                "high.school",
                "professional.course",
            ],
            "default": ["no", "no", "no", "yes", "no"],
            "housing": ["yes", "yes", "no", "yes", "no"],
            "loan": ["no", "no", "yes", "no", "no"],
            "contact": ["cellular", "cellular", "telephone", "cellular", "telephone"],
            "month": ["may", "jun", "jul", "aug", "sep"],
            "day_of_week": ["mon", "tue", "wed", "thu", "fri"],
            "duration": [120, 300, 60, 450, 90],
            "campaign": [1, 2, 1, 3, 1],
            "pdays": [999, 3, 999, 7, 999],
            "previous": [0, 1, 0, 2, 0],
            "poutcome": [
                "nonexistent",
                "success",
                "nonexistent",
                "failure",
                "nonexistent",
            ],
            "emp_var_rate": [1.4, -1.8, 1.1, -0.1, 0.5],
            "cons_price_index": [93.0, 94.5, 93.2, 95.1, 94.0],
            "cons_conf_index": [-36.0, -42.0, -38.0, -40.0, -37.0],
            "lending_rate3m": [3.5, 4.0, 5.0, 3.2, 4.5],
            "nr_employed": [5100.0, 5000.0, 5200.0, 5050.0, 5150.0],
            "subscribe": ["no", "yes", "no", "yes", "no"],
        }
    )


def _mock_columns(n):
    """返回 n 个 MagicMock,支持 with 上下文。"""
    return [MagicMock() for _ in range(n)]


def _load_page(page_name: str):
    page_path = Path(__file__).parent.parent / "src" / "pages" / page_name
    spec = util.spec_from_file_location(page_name[:-3], page_path)
    module = util.module_from_spec(spec)
    sys.modules[page_name[:-3]] = module
    spec.loader.exec_module(module)
    return module


class TestDataAnalysisPage:
    def test_page_loads_with_data(self, monkeypatch):
        mock_df = _make_mock_df()
        monkeypatch.setattr("src.data_loader.load_train", lambda: mock_df)

        with (
            patch("streamlit.set_page_config"),
            patch("streamlit.title") as mock_title,
            patch("streamlit.caption"),
            patch("streamlit.markdown"),
            patch("streamlit.columns", side_effect=_mock_columns),
            patch("streamlit.metric"),
            patch("streamlit.plotly_chart"),
            patch("streamlit.dataframe"),
            patch("streamlit.warning"),
            patch("streamlit.stop", side_effect=SystemExit),
        ):
            try:
                _load_page("01_数据分析.py")
            except SystemExit:
                pass
            mock_title.assert_called_once()

    def test_page_stops_when_no_data(self, monkeypatch):
        monkeypatch.setattr(
            "src.data_loader.load_train",
            lambda: (_ for _ in ()).throw(FileNotFoundError("训练数据未找到")),
        )
        with (
            patch("streamlit.set_page_config"),
            patch("streamlit.warning"),
            patch("streamlit.stop", side_effect=SystemExit) as mock_stop,
        ):
            try:
                _load_page("01_数据分析.py")
            except SystemExit:
                pass
            mock_stop.assert_called_once()

    def test_overview_metrics_displayed(self, monkeypatch):
        mock_df = _make_mock_df()
        monkeypatch.setattr("src.data_loader.load_train", lambda: mock_df)

        with (
            patch("streamlit.set_page_config"),
            patch("streamlit.title"),
            patch("streamlit.caption"),
            patch("streamlit.markdown"),
            patch("streamlit.columns", side_effect=_mock_columns),
            patch("streamlit.metric") as mock_metric,
            patch("streamlit.plotly_chart"),
            patch("streamlit.dataframe"),
            patch("streamlit.warning"),
            patch("streamlit.stop"),
        ):
            _load_page("01_数据分析.py")
            assert mock_metric.call_count == 5


class TestPredictionPage:
    def test_page_loads_with_model_ready(self):
        mock_predictor = MagicMock()
        mock_predictor.model_info = {
            "model_name": "RandomForest",
            "auc": 0.89,
            "f1": 0.52,
        }
        with (
            patch("src.predictor.get_predictor", return_value=mock_predictor),
            patch("streamlit.set_page_config"),
            patch("streamlit.title") as mock_title,
            patch("streamlit.caption"),
            patch("streamlit.columns", side_effect=_mock_columns),
            patch("streamlit.metric"),
            patch("streamlit.markdown"),
            patch("streamlit.error"),
            patch("streamlit.info"),
            patch("streamlit.stop", side_effect=SystemExit),
            patch("streamlit.form_submit_button", return_value=False),
            patch("streamlit.number_input", return_value=40),
            patch("streamlit.selectbox", return_value="已婚"),
            patch("streamlit.slider", return_value=0.0),
            patch("streamlit.form"),
        ):
            try:
                _load_page("02_在线预测.py")
            except SystemExit:
                pass
            mock_title.assert_called()

    def test_page_shows_error_when_model_missing(self):
        with (
            patch(
                "src.predictor.get_predictor",
                side_effect=PredictionError("模型文件未找到"),
            ),
            patch("streamlit.set_page_config"),
            patch("streamlit.title"),
            patch("streamlit.caption"),
            patch("streamlit.error") as mock_error,
            patch("streamlit.info"),
            patch("streamlit.stop", side_effect=SystemExit) as mock_stop,
        ):
            try:
                _load_page("02_在线预测.py")
            except SystemExit:
                pass
            mock_error.assert_called_once()
            mock_stop.assert_called_once()

    def test_page_title_contains_correct_text(self):
        mock_predictor = MagicMock()
        mock_predictor.model_info = {
            "model_name": "RandomForest",
            "auc": 0.89,
            "f1": 0.52,
        }
        with (
            patch("src.predictor.get_predictor", return_value=mock_predictor),
            patch("streamlit.set_page_config"),
            patch("streamlit.title") as mock_title,
            patch("streamlit.caption"),
            patch("streamlit.columns", side_effect=_mock_columns),
            patch("streamlit.metric"),
            patch("streamlit.markdown"),
            patch("streamlit.error"),
            patch("streamlit.info"),
            patch("streamlit.stop"),
            patch("streamlit.form_submit_button", return_value=False),
            patch("streamlit.number_input", return_value=40),
            patch("streamlit.selectbox", return_value="已婚"),
            patch("streamlit.slider", return_value=0.0),
            patch("streamlit.form"),
            patch("streamlit.success"),
            patch("streamlit.warning"),
            patch("streamlit.progress"),
            patch("streamlit.expander"),
            patch("streamlit.json"),
        ):
            _load_page("02_在线预测.py")
            args = mock_title.call_args[0][0]
            assert "在线预测" in args

    def test_form_submission_triggers_prediction(self):
        mock_predictor = MagicMock()
        mock_predictor.model_info = {
            "model_name": "RandomForest",
            "auc": 0.89,
            "f1": 0.52,
        }
        mock_predictor.predict.return_value = {
            "subscribe": "yes",
            "subscribe_cn": "预计会认购",
            "probability": 0.72,
            "confidence": 72.0,
        }
        with (
            patch("src.predictor.get_predictor", return_value=mock_predictor),
            patch("streamlit.set_page_config"),
            patch("streamlit.title"),
            patch("streamlit.caption"),
            patch("streamlit.columns", side_effect=_mock_columns),
            patch("streamlit.metric"),
            patch("streamlit.markdown"),
            patch("streamlit.error"),
            patch("streamlit.info"),
            patch("streamlit.stop"),
            patch("streamlit.form_submit_button", return_value=True),
            patch("streamlit.number_input", return_value=40),
            patch("streamlit.selectbox", return_value="已婚"),
            patch("streamlit.slider", return_value=0.0),
            patch("streamlit.form"),
            patch("streamlit.success") as mock_success,
            patch("streamlit.warning") as mock_warning,
            patch("streamlit.progress"),
            patch("streamlit.expander"),
            patch("streamlit.json"),
        ):
            _load_page("02_在线预测.py")
            mock_predictor.predict.assert_called_once()
            mock_success.assert_called_once()
            mock_warning.assert_not_called()

    def test_form_submission_shows_warning_for_no_prediction(self):
        mock_predictor = MagicMock()
        mock_predictor.model_info = {
            "model_name": "RandomForest",
            "auc": 0.89,
            "f1": 0.52,
        }
        mock_predictor.predict.return_value = {
            "subscribe": "no",
            "subscribe_cn": "预计不会认购",
            "probability": 0.28,
            "confidence": 72.0,
        }
        with (
            patch("src.predictor.get_predictor", return_value=mock_predictor),
            patch("streamlit.set_page_config"),
            patch("streamlit.title"),
            patch("streamlit.caption"),
            patch("streamlit.columns", side_effect=_mock_columns),
            patch("streamlit.metric"),
            patch("streamlit.markdown"),
            patch("streamlit.error"),
            patch("streamlit.info"),
            patch("streamlit.stop"),
            patch("streamlit.form_submit_button", return_value=True),
            patch("streamlit.number_input", return_value=40),
            patch("streamlit.selectbox", return_value="已婚"),
            patch("streamlit.slider", return_value=0.0),
            patch("streamlit.form"),
            patch("streamlit.success") as mock_success,
            patch("streamlit.warning") as mock_warning,
            patch("streamlit.progress"),
            patch("streamlit.expander"),
            patch("streamlit.json"),
        ):
            _load_page("02_在线预测.py")
            mock_warning.assert_called_once()
            mock_success.assert_not_called()
