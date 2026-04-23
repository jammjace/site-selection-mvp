from __future__ import annotations
import pandas as pd


def clean_area_name(name: str) -> str:
    if pd.isna(name):
        return ""
    return (
        str(name)
        .strip()
        .upper()
        .replace("&", "AND")
    )


def minmax_scale(series: pd.Series) -> pd.Series:
    series = pd.to_numeric(series, errors="coerce").fillna(0)
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series([50.0] * len(series), index=series.index)
    return 100 * (series - min_val) / (max_val - min_val)


def zfill_missing(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df