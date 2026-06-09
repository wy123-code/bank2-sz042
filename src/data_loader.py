from pathlib import Path

import pandas as pd

from .utils import get_feature_cn

DATA_DIR = Path(__file__).parent.parent / "data"


def load_train() -> pd.DataFrame:
    """加载训练数据。"""
    path = DATA_DIR / "train.csv"
    if not path.exists():
        raise FileNotFoundError(f"训练数据未找到: {path}")
    df = pd.read_csv(path)
    return df


def load_test() -> pd.DataFrame:
    """加载测试数据(无标签)。"""
    path = DATA_DIR / "test.csv"
    if not path.exists():
        raise FileNotFoundError(f"测试数据未找到: {path}")
    df = pd.read_csv(path)
    return df


def get_basic_stats(df: pd.DataFrame) -> dict:
    """返回数据基本统计信息。"""
    total = len(df)
    sub_yes = (
        int(df["subscribe"].value_counts().get("yes", 0))
        if "subscribe" in df.columns
        else 0
    )
    sub_no = total - sub_yes if "subscribe" in df.columns else total
    sub_rate = (
        round(sub_yes / total * 100, 1)
        if total > 0 and "subscribe" in df.columns
        else 0.0
    )
    return {
        "total_records": total,
        "num_features": len(df.columns) - 1,  # exclude id
        "subscribe_yes": sub_yes,
        "subscribe_no": sub_no,
        "subscribe_rate": sub_rate,
    }


def get_feature_stats(df: pd.DataFrame) -> pd.DataFrame:
    """返回每个特征的缺失率、唯一值数、数据类型等统计。"""
    rows = []
    for col in df.columns:
        if col == "id":
            continue
        missing = df[col].isna().sum()
        missing_rate = round(missing / len(df) * 100, 2)
        unique = df[col].nunique()
        dtype = str(df[col].dtype)
        cn_name = get_feature_cn(col)
        rows.append(
            {
                "特征": cn_name,
                "字段名": col,
                "缺失数": missing,
                "缺失率(%)": missing_rate,
                "唯一值数": unique,
                "数据类型": dtype,
            }
        )
    return pd.DataFrame(rows)
