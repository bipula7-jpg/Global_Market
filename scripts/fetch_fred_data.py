"""
SIGNAL — FRED data fetcher

Pulls the 10Y-2Y spread, 10Y-3M spread, and the effective Fed Funds Rate
from the St. Louis Fed's FRED API and writes them to data/fred.json for
the frontend to display.

These specifically replace TradingView mini-chart widgets that used
"FRED:T10Y2Y" / "FRED:T10Y3M" / "FRED:FEDFUNDS" as symbols — TradingView's
free embeddable widgets don't actually resolve that prefix, which is why
that section was blank. FRED's own API is the reliable fix.

Requires a free FRED API key, passed via the FRED_API_KEY environment
variable (set this as a GitHub Actions repository secret — never commit
the key itself to the repo).
"""

import json
import os
import sys
from datetime import datetime, timezone

import requests

FRED_API_KEY = os.environ.get("FRED_API_KEY")
BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

SERIES = {
    "t10y2y": {"id": "T10Y2Y", "label": "10Y-2Y Spread"},
    "t10y3m": {"id": "T10Y3M", "label": "10Y-3M Spread"},
    "fedfunds": {"id": "FEDFUNDS", "label": "Effective Fed Funds Rate"},
}

OUTPUT_PATH = "data/fred.json"


def fetch_series(series_id: str) -> dict:
    """Return {status, value, change, date} for one FRED series.
    Never raises — a failure here is captured in the dict so one bad
    series can't take down the whole run."""
    try:
        params = {
            "series_id": series_id,
            "api_key": FRED_API_KEY,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 10,  # a few extra in case the latest rows are '.' (no data that day)
        }
        resp = requests.get(BASE_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") not in (None, ".", "")]
        if not obs:
            return {"status": "error", "error": "no valid observations returned"}

        latest = float(obs[0]["value"])
        latest_date = obs[0]["date"]

        if len(obs) < 2:
            return {"status": "partial", "value": round(latest, 4), "change": None, "date": latest_date}

        prev = float(obs[1]["value"])
        return {
            "status": "ok",
            "value": round(latest, 4),
            "change": round(latest - prev, 4),
            "date": latest_date,
        }
    except Exception as exc:  # noqa: BLE001 — deliberately broad; one bad series must not stop the run
        return {"status": "error", "error": str(exc)}


def main() -> None:
    if not FRED_API_KEY:
        print("FRED_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "FRED (Federal Reserve Bank of St. Louis)",
    }

    any_success = False
    for key, meta in SERIES.items():
        result = fetch_series(meta["id"])
        output[key] = {**result, "label": meta["label"], "series_id": meta["id"]}
        if result.get("status") in ("ok", "partial"):
            any_success = True

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Wrote {OUTPUT_PATH} (any_success={any_success})")
    if not any_success:
        sys.exit(1)


if __name__ == "__main__":
    main()
