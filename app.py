from __future__ import annotations
import json
import pandas as pd
import geopandas as gpd
import streamlit as st
import pydeck as pdk
import matplotlib.pyplot as plt

from src.presets import PRESETS
from src.scoring import score_areas
from src.explain import explain_row

st.set_page_config(page_title="Premium Eye Clinic Locator", layout="wide")

AREA_FEATURES_PATH = "data/processed/area_features.csv"
AREA_GEOJSON_PATH = "data/processed/singapore_planning_areas_scored.geojson"


@st.cache_data
def load_data() -> tuple[pd.DataFrame, gpd.GeoDataFrame]:
    df = pd.read_csv(AREA_FEATURES_PATH)
    gdf = gpd.read_file(AREA_GEOJSON_PATH)
    return df, gdf


st.title("Premium Eye Clinic Locator — Singapore")
st.caption("Planning-area recommender for a premium eye clinic branch")

df, gdf = load_data()

st.sidebar.header("Strategy")
preset_name = st.sidebar.selectbox(
    "Choose site-selection mode",
    options=list(PRESETS.keys()),
    index=4,
)
base_weights = PRESETS[preset_name].copy()

st.sidebar.subheader("Adjust weights")
demand_w = st.sidebar.slider("Demand", 0.0, 1.0, float(base_weights["demand"]), 0.01)
ageing_w = st.sidebar.slider("Ageing", 0.0, 1.0, float(base_weights["ageing"]), 0.01)
affluence_w = st.sidebar.slider("Affluence", 0.0, 1.0, float(base_weights["affluence"]), 0.01)
access_w = st.sidebar.slider("Access", 0.0, 1.0, float(base_weights["access"]), 0.01)
medical_w = st.sidebar.slider("Medical adjacency", 0.0, 1.0, float(base_weights["medical"]), 0.01)
competition_w = st.sidebar.slider("Competition penalty", 0.0, 1.0, float(base_weights["competition"]), 0.01)

weights = {
    "demand": demand_w,
    "ageing": ageing_w,
    "affluence": affluence_w,
    "access": access_w,
    "medical": medical_w,
    "competition": competition_w,
}

scored = score_areas(df, weights)
scored["explanation"] = scored.apply(explain_row, axis=1)

top_n = st.slider("Top areas to show", 5, 20, 10)

col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("Top recommended planning areas")
    st.dataframe(
        scored[
            [
                "planning_area",
                "total_score",
                "demand_score",
                "ageing_score",
                "affluence_score",
                "access_score",
                "medical_score",
                "competition_score",
                "explanation",
            ]
        ].head(top_n),
        use_container_width=True,
        hide_index=True,
    )

with col2:
    st.subheader("Top 10 score chart")
    fig, ax = plt.subplots(figsize=(8, 5))
    chart_df = scored.head(10).sort_values("total_score")
    ax.barh(chart_df["planning_area"], chart_df["total_score"])
    ax.set_xlabel("Total score")
    ax.set_ylabel("Planning area")
    st.pyplot(fig)

st.subheader("Map")

map_df = gdf.merge(
    scored[["planning_area", "total_score"]],
    on="planning_area",
    how="left"
)

map_df["fill_color"] = map_df["total_score"].fillna(0).apply(
    lambda x: [int(min(255, x * 2.2)), int(max(30, 255 - x * 2)), 80, 140]
)

geojson_data = json.loads(map_df.to_json())

layer = pdk.Layer(
    "GeoJsonLayer",
    geojson_data,
    opacity=0.6,
    stroked=True,
    filled=True,
    extruded=False,
    wireframe=True,
    get_fill_color="properties.fill_color",
    get_line_color=[80, 80, 80],
    pickable=True,
)

view_state = pdk.ViewState(latitude=1.3521, longitude=103.8198, zoom=10, pitch=0)

tooltip = {
    "html": "<b>{planning_area}</b><br/>Score: {total_score}",
    "style": {"backgroundColor": "white", "color": "black"}
}

st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip))

st.subheader("Top 5 recommendations")
for _, row in scored.head(5).iterrows():
    st.markdown(f"**{row['planning_area']}** — {row['total_score']:.2f}")
    st.write(row["explanation"])

st.subheader("Assumptions")
st.markdown(
    """
- Planning-area level only, not parcel-level.
- Competition data is manually curated.
- This estimates opportunity, not guaranteed revenue.
- Rent and actual unit availability are not included in v1.
"""
)