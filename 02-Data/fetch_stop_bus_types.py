"""Bus types (SD / DD / BD) and services calling at the demo stops, from LTA DataMall BusArrival v3.

Key: week9/00_ridership/DataMall.lta_key or env LTA_ACCOUNT_KEY (never printed / never written to outputs).
Each call returns the next three buses of every service, so one call per stop shows the types in service now;
run it a few times across the day to be safe – results are merged into stop_bus_types.json.
Usage: python fetch_stop_bus_types.py
"""
import json
import os
from datetime import datetime
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
KEY_FILE = HERE.parents[1] / "week9" / "00_ridership" / "DataMall.lta_key"
OUT = HERE / "stop_bus_types.json"
DEMO = {"P021": "22501", "P040": "17239", "P039": "17169"}


def main():
    k = os.environ.get("LTA_ACCOUNT_KEY") or KEY_FILE.read_text(encoding="utf-8-sig").strip()
    out = json.loads(OUT.read_text()) if OUT.exists() else {}
    for idx, code in DEMO.items():
        r = requests.get("https://datamall2.mytransport.sg/ltaodataservice/v3/BusArrival", params={"BusStopCode": code},
                         headers={"AccountKey": k, "accept": "application/json"}, timeout=60)
        r.raise_for_status()
        rec = out.setdefault(idx, {"bus_stop_id": code, "services": {}})
        for s in r.json().get("Services", []):
            svc = rec["services"].setdefault(s["ServiceNo"], {"operator": s.get("Operator"), "types": []})
            for nb in ("NextBus", "NextBus2", "NextBus3"):
                t = (s.get(nb) or {}).get("Type")
                if t and t not in svc["types"]:
                    svc["types"].append(t)
        rec["types"] = sorted({t for v in rec["services"].values() for t in v["types"]})
        rec["checked"] = datetime.now().isoformat(timespec="minutes")
        print(idx, code, rec["types"], {n: v["types"] for n, v in rec["services"].items()})
    OUT.write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
