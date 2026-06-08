import tempfile
from pathlib import Path

import pandas as pd
import pytest


def _create_temp_train_csv() -> tuple[Path, pd.DataFrame]:
    """在临时目录创建 train.csv,返回目录路径和原始 DataFrame。"""
    data = pd.DataFrame(
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
            "subscribe": ["no", "yes", "no", "yes", "no"],
        }
    )
    tmpdir = Path(tempfile.mkdtemp())
    data.to_csv(tmpdir / "train.csv", index=False)
    return tmpdir, data


def _create_temp_test_csv() -> tuple[Path, pd.DataFrame]:
    """在临时目录创建 test.csv,返回目录路径和原始 DataFrame。"""
    data = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "age": [35, 42, 29],
        }
    )
    tmpdir = Path(tempfile.mkdtemp())
    data.to_csv(tmpdir / "test.csv", index=False)
    return tmpdir, data


def test_load_train_raises_when_file_not_found(monkeypatch):
    monkeypatch.setattr("src.data_loader.DATA_DIR", Path("/nonexistent"))
    from src.data_loader import load_train

    with pytest.raises(FileNotFoundError, match="训练数据未找到"):
        load_train()


def test_load_test_raises_when_file_not_found(monkeypatch):
    monkeypatch.setattr("src.data_loader.DATA_DIR", Path("/nonexistent"))
    from src.data_loader import load_test

    with pytest.raises(FileNotFoundError, match="测试数据未找到"):
        load_test()


def test_load_test_reads_csv(monkeypatch):
    tmpdir, _ = _create_temp_test_csv()
    monkeypatch.setattr("src.data_loader.DATA_DIR", tmpdir)
    from src.data_loader import load_test

    df = load_test()
    assert len(df) == 3
    assert "age" in df.columns


def test_load_train_reads_csv(monkeypatch):
    tmpdir, _ = _create_temp_train_csv()
    monkeypatch.setattr("src.data_loader.DATA_DIR", tmpdir)
    from src.data_loader import load_train

    df = load_train()
    assert len(df) == 5
    assert "subscribe" in df.columns
    assert "age" in df.columns


def test_basic_stats(monkeypatch):
    tmpdir, _ = _create_temp_train_csv()
    monkeypatch.setattr("src.data_loader.DATA_DIR", tmpdir)
    from src.data_loader import get_basic_stats, load_train

    df = load_train()
    stats = get_basic_stats(df)
    assert stats["total_records"] == 5
    assert stats["subscribe_yes"] == 2
    assert stats["subscribe_no"] == 3
    assert stats["subscribe_rate"] == 40.0


def test_basic_stats_no_subscribe_column():
    df = pd.DataFrame({"id": [1, 2], "age": [30, 40]})
    from src.data_loader import get_basic_stats

    stats = get_basic_stats(df)
    assert stats["subscribe_yes"] == 0
    assert stats["subscribe_rate"] == 0.0


def test_get_feature_stats_skips_id(monkeypatch):
    tmpdir, _ = _create_temp_train_csv()
    monkeypatch.setattr("src.data_loader.DATA_DIR", tmpdir)
    from src.data_loader import get_feature_stats, load_train

    df = load_train()
    stats_df = get_feature_stats(df)
    assert "id" not in stats_df["字段名"].values
    assert "age" in stats_df["字段名"].values


def test_get_feature_stats_cn_names(monkeypatch):
    tmpdir, _ = _create_temp_train_csv()
    monkeypatch.setattr("src.data_loader.DATA_DIR", tmpdir)
    from src.data_loader import get_feature_stats, load_train

    df = load_train()
    stats_df = get_feature_stats(df)
    cn_names = stats_df["特征"].tolist()
    assert "年龄" in cn_names
    assert "职业" in cn_names
