# Problem statement: Given a clinic strategy, where in Singapore should I open next?

# MVP:
A Streamlit app that:

ranks Singapore planning areas for a premium eye clinic using a brand-inspired scoring model with 4 preset modes:
1. McDonald’s
2. Starbucks
3 .Luckin
4. Q&M

# Inputs:
clinic type
strategy mode
weights

# Outputs:
top 5 recommended areas
score by factor
explanation for each area

# 4 presets (chosen based on popularity)
## McDonald’s-style
- coverage
- accessibility
- broad residential demand

## Starbucks-style
- visibility
- premium catchment
- high-traffic nodes

## Luckin-style
- convenience
- dense network
- fast access / commuter-heavy

## Q&M-style
- neighborhood healthcare
- repeat visits
- residential convenience

# Folder structure 
site-selection-mvp/
├─ app.py
├─ requirements.txt
├─ README.md
├─ data/
│  ├─ raw/
│  │  ├─ planning_areas.geojson
│  │  ├─ mrt_exits.geojson
│  │  ├─ demographics_planning_area.csv
│  │  ├─ competitors.csv
│  ├─ processed/
│  │  ├─ area_features.csv
│  │  └─ singapore_planning_areas_scored.geojson
├─ src/
│  ├─ scoring.py
│  ├─ presets.py
│  ├─ explain.py
│  ├─ utils.py
│  └─ prepare_data.py
