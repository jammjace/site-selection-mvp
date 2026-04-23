from __future__ import annotations
import pandas as pd


def explain_row(row: pd.Series) -> str:
    reasons = []

    if row["affluence_score"] >= 75:
        reasons.append("strong premium-income catchment")
    if row["access_score"] >= 75:
        reasons.append("good MRT accessibility")
    if row["ageing_score"] >= 70:
        reasons.append("older resident profile supports eye-care demand")
    if row["medical_score"] >= 65:
        reasons.append("close to medical ecosystem")
    if row["competition_score"] <= 35:
        reasons.append("competition is still manageable")

    if not reasons:
        reasons.append("balanced profile across demand, access, and premium potential")

    return "; ".join(reasons)