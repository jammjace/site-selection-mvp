from __future__ import annotations
import pandas as pd


def score_areas(df: pd.DataFrame, weights: dict[str, float]) -> pd.DataFrame:
    out = df.copy()

    out["total_score"] = (
        weights["demand"] * out["demand_score"]
        + weights["ageing"] * out["ageing_score"]
        + weights["affluence"] * out["affluence_score"]
        + weights["access"] * out["access_score"]
        + weights["medical"] * out["medical_score"]
        - weights["competition"] * out["competition_score"]
    )

    out = out.sort_values("total_score", ascending=False).reset_index(drop=True)
    return out