from __future__ import annotations
import time
import requests
from pathlib import Path

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

PLANNING_AREA_DATASET_ID = "d_4765db0e87b9c86336792efe8a1f7a66"
MRT_EXITS_DATASET_ID = "d_b39d3a0871985372d7e1637193335da5"


def download_datagov_dataset(dataset_id: str, out_path: str, timeout: int = 30) -> None:
    poll_url = f"https://api-open.data.gov.sg/v1/public/api/datasets/{dataset_id}/poll-download"

    # Step 1: request a download URL
    poll_resp = requests.get(poll_url, timeout=timeout)
    poll_resp.raise_for_status()
    poll_data = poll_resp.json()

    if "data" not in poll_data:
        raise ValueError(f"Unexpected poll-download response: {poll_data}")

    download_url = poll_data["data"].get("url")
    if not download_url:
        raise ValueError(f"No download URL returned for dataset {dataset_id}: {poll_data}")

    # Step 2: download the actual file
    file_resp = requests.get(download_url, timeout=timeout)
    file_resp.raise_for_status()

    with open(out_path, "wb") as f:
        f.write(file_resp.content)

    print(f"Saved {out_path}")


def main() -> None:
    download_datagov_dataset(
        PLANNING_AREA_DATASET_ID,
        str(RAW_DIR / "planning_areas.geojson")
    )

    download_datagov_dataset(
        MRT_EXITS_DATASET_ID,
        str(RAW_DIR / "mrt_exits.geojson")
    )


if __name__ == "__main__":
    main()