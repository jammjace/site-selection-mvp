import os
import json
import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import shape

from src.utils import clean_area_name, minmax_scale, zfill_missing


PLANNING_AREAS_PATH = "data/raw/planning_areas.geojson"
MRT_EXITS_PATH = "data/raw/mrt_exits.geojson"
DEMOGRAPHICS_PATH = "data/raw/demographics_planning_area.csv"
COMPETITORS_PATH = "data/raw/competitors.csv"

OUT_CSV_PATH = "data/processed/area_features.csv"
OUT_GEOJSON_PATH = "data/processed/singapore_planning_areas_scored.geojson"


def fetch_planning_areas_from_onemap(year: int = 2019) -> gpd.GeoDataFrame:
    token = os.getenv("ONEMAP_API_TOKEN")
    if not token:
        raise ValueError("Missing ONEMAP_API_TOKEN environment variable.")

    url = f"https://www.onemap.gov.sg/api/public/popapi/getAllPlanningarea?year={year}"
    headers = {"Authorization": token}

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()

    if "SearchResults" not in data:
        raise ValueError(f"Unexpected response keys: {list(data.keys())}")

    rows = []
    for item in data["SearchResults"]:
        name = item.get("pln_area_n")
        geojson_str = item.get("geojson")

        if not name or not geojson_str:
            continue

        geom_dict = json.loads(geojson_str)

        rows.append({
            "planning_area": name,
            "geometry": shape(geom_dict)
        })

    if not rows:
        raise ValueError("No planning area rows could be parsed from OneMap response.")

    gdf = gpd.GeoDataFrame(rows, geometry="geometry", crs="EPSG:4326")
    return gdf




def main() -> None:
    # 1. Fetch planning areas from API and save raw copy
    planning = fetch_planning_areas_from_onemap(year=2019).to_crs(epsg=4326)
    planning.to_file(PLANNING_AREAS_PATH, driver="GeoJSON")
    planning["planning_area"] = planning["planning_area"].apply(clean_area_name)

    # 2. Load MRT exits
    mrt = gpd.read_file(MRT_EXITS_PATH).to_crs(epsg=4326)

    # 4. MRT exits -> count per planning area
    mrt_join = gpd.sjoin(
        mrt[["geometry"]],
        planning[["planning_area", "geometry"]],
        predicate="within",
        how="left"
    )
    mrt_counts = (
        mrt_join.groupby("planning_area")
        .size()
        .reset_index(name="mrt_exit_count")
    )

    # 5. Demographics
    demo = pd.read_csv(DEMOGRAPHICS_PATH)
    demo["planning_area"] = demo["planning_area"].apply(clean_area_name)

    # 6. Competitors
    comp = pd.read_csv(COMPETITORS_PATH)
    comp["planning_area"] = comp["planning_area"].apply(clean_area_name)

    competitor_counts = (
        comp.groupby("planning_area")
        .agg(
            competitor_count=("clinic_name", "count"),
            premium_competition_score=("premium_score", "sum")
        )
        .reset_index()
    )

    competitor_counts["medical_hub_proxy"] = competitor_counts["premium_competition_score"]

    # 7. Merge everything
    area = planning[["planning_area", "geometry"]].drop_duplicates().copy()
    area = area.merge(demo, on="planning_area", how="left")
    area = area.merge(mrt_counts, on="planning_area", how="left")
    area = area.merge(competitor_counts, on="planning_area", how="left")

    area = zfill_missing(
        area,
        [
            "population",
            "pct_seniors",
            "income_index",
            "mrt_exit_count",
            "competitor_count",
            "premium_competition_score",
            "medical_hub_proxy",
        ],
    )

    # 8. Feature engineering
    area["demand_raw"] = area["population"]
    area["ageing_raw"] = area["pct_seniors"]
    area["affluence_raw"] = area["income_index"]
    area["access_raw"] = area["mrt_exit_count"]
    area["medical_raw"] = area["medical_hub_proxy"]
    area["competition_raw"] = area["premium_competition_score"]

    # 9. Normalize
    area["demand_score"] = minmax_scale(area["demand_raw"])
    area["ageing_score"] = minmax_scale(area["ageing_raw"])
    area["affluence_score"] = minmax_scale(area["affluence_raw"])
    area["access_score"] = minmax_scale(area["access_raw"])
    area["medical_score"] = minmax_scale(area["medical_raw"])
    area["competition_score"] = minmax_scale(area["competition_raw"])

    # 10. Save outputs
    area.to_csv(OUT_CSV_PATH, index=False)
    area.to_file(OUT_GEOJSON_PATH, driver="GeoJSON")

    print(f"Saved {OUT_CSV_PATH}")
    print(f"Saved {OUT_GEOJSON_PATH}")


if __name__ == "__main__":
    main()