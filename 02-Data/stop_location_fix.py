"""Check the 88 kept stops against LTA DataMall BusStops (current) and write the location / name corrections.

Reads  ../02_prototypes/stop_dataset_v2.csv, stop_metrics_v1.geojson (LTA point used so far, SVY21)
       ../../week9/scrap/svi_match.csv (outdoor panoramas matched in week 9)
       DataMall BusStops (key: week9/00_ridership/DataMall.lta_key or env LTA_ACCOUNT_KEY, never printed)
Writes stop_location_fixes_v1.csv – one row per stop:
  action   keep     POLE_SOURCE = "gis": the pole (s = 0) stays on the week-9 point (static GIS layer
                    BusStopLocation_Mar2026). Checked 2026-10-26 on the 74 hand-labelled shelters: against the GIS point
                    the roof's downstream end has a median of -1.0 m (LTA SDRE: 1.5 m before the pole), against the
                    DataMall point +4.9 m, with the DataMall point under the roof at 39/74 stops – DataMall places the
                    stop / shelter, the GIS point the pole
           move     POLE_SOURCE = "datamall": the pole is the DataMall point projected on the road line (ds along
                    traffic; dn reported, not applied); shelter s values shift by -ds so the shelter stays put
           discard  code no longer in DataMall (decision in `note`) – DataMall is the reference for which stops exist
  dm_roof_m  distance from the DataMall point to the labelled roof along the road (0 = within it); large values
             point at a shelter label to check
  note     crop check for stops MOVE_M or more apart
  dm_*     DataMall code / name / road / point;  name_new = DataMall name where it differs beyond letter case
  sv_C/U/D week-9 panorama sample_id: kept stops keep their own; moved stops take the nearest one (any stop's) to the
           corrected point and ±15 m along the road within SVI_M, blank = none, the page then links by coordinates

Usage: python stop_location_fix.py
"""
import csv
import json
import math
import os
from pathlib import Path

import requests
from pyproj import Transformer

HERE = Path(__file__).resolve().parent
WR = HERE.parents[1]
KEY = WR / "week9" / "00_ridership" / "DataMall.lta_key"
SVI = WR / "week9" / "scrap" / "svi_match.csv"
OUT = HERE / "stop_location_fixes_v1.csv"
POLE_SOURCE = "gis"   # "gis" (week-9 BusStopLocation point) or "datamall" – see action above
MOVE_M = 30        # points this far apart (m) were checked on the crop; see CHECKED
SVI_KEEP = 15      # pole moved less than this: the stop keeps its own week-9 panoramas
SVI_M = 20         # moved further: a week-9 panorama this close to a sample point serves it, else the page links by coordinates
# codes missing from DataMall, checked by hand on 2026-10-26 (satellite crop, week-9 SVI, DataMall stops nearby)
DISCARD = {
    "P070": "44401 not in DataMall and no services; its labelled shelter (49-61 m upstream) is P068's shelter – "
            "the stop is served as 44251 Bt Panjang Stn/Blk 604 (P068). Duplicate, dropped.",
    "P016": "22579 not in DataMall, no stop within 187 m. 2024 SVI shows a temporary stop beside the Boon Lay Int "
            "hoarding; removed. Dropped.",
    "P018": "22571 not in DataMall, no stop within 227 m; opposite of P016, same temporary stop pair. Dropped.",
}


# stops MOVE_M or more apart, checked on the satellite crops on 2026-10-26 (DataMall point drawn on the crop)
CHECKED = {
    "P005": "crop: DataMall point sits on the labelled shelter",
    "P072": "crop: DataMall point lies in the junction, off the kerb – check the shelter / pole on Street View",
}


def datamall():
    k = os.environ.get("LTA_ACCOUNT_KEY") or KEY.read_text(encoding="utf-8-sig").strip()
    out = []
    for skip in range(0, 10000, 500):
        r = requests.get("https://datamall2.mytransport.sg/ltaodataservice/BusStops", params={"$skip": skip},
                         headers={"AccountKey": k, "accept": "application/json"}, timeout=60)
        r.raise_for_status()
        v = r.json()["value"]
        out += v
        if len(v) < 500:
            break
    return {s["BusStopCode"].zfill(5): s for s in out}


def norm(s):
    return " ".join(s.upper().replace("/", " / ").replace("  ", " ").split()).replace(" / ", "/")


def main():
    dm = datamall()
    to_svy = Transformer.from_crs(4326, 3414, always_xy=True)
    to_wgs = Transformer.from_crs(3414, 4326, always_xy=True)
    geo = {f["properties"]["stop_idx"]: f for f in
           json.loads((HERE / "stop_metrics_v1.geojson").read_text(encoding="utf-8"))["features"]}
    rows = [r for r in csv.DictReader((HERE.parent / "02_prototypes" / "stop_dataset_v2.csv").open(encoding="utf-8-sig"))
            if r.get("discard") != "1"]
    panos = [(p, *to_svy.transform(float(p["pano_lon"]), float(p["pano_lat"])))
             for p in csv.DictReader(SVI.open(encoding="utf-8-sig")) if p.get("pano_lat")]
    out = []
    for r in rows:
        idx, f = r["stop_idx"], geo[r["stop_idx"]]
        x0, y0 = f["geometry"]["coordinates"][:2]
        th = math.radians(float(f["properties"].get("direction") or 0))
        side = -1 if f["properties"].get("stop_side") == "right" else 1
        u, n = (math.sin(th), math.cos(th)), (-math.cos(th) * side, math.sin(th) * side)   # traffic / footpath side
        s = dm.get(r["bus_stop_id"].zfill(5))
        rec = {"stop_idx": idx, "bus_stop_id": r["bus_stop_id"], "stop_name": r["stop_name"], "action": "keep",
               "dm_code": "", "dm_name": "", "dm_road": "", "dm_lat": "", "dm_lon": "", "dist_m": "", "ds_m": "", "dn_m": "",
               "name_new": "", "dm_roof_m": "", "shelter_s_from_new": "", "shelter_s_to_new": "", "sv_C": "", "sv_U": "", "sv_D": "", "note": ""}
        if idx in DISCARD or not s:
            rec.update(action="discard", note=DISCARD.get(idx, "code not in DataMall – check by hand"))
            out.append(rec)
            continue
        dx, dy = to_svy.transform(s["Longitude"], s["Latitude"])
        ex, ey = dx - x0, dy - y0
        ds, dn = ex * u[0] + ey * u[1], ex * n[0] + ey * n[1]
        rec.update(dm_code=s["BusStopCode"], dm_name=s["Description"], dm_road=s["RoadName"],
                   dm_lat=round(s["Latitude"], 7), dm_lon=round(s["Longitude"], 7), dist_m=round(math.hypot(ex, ey), 1),
                   ds_m=round(ds, 1), dn_m=round(dn, 1))
        if norm(s["Description"]) != norm(r["stop_name"]):
            rec["name_new"] = s["Description"].upper()
        why = CHECKED.get(idx, "crop does not settle it – check the shelter / pole on Street View") if math.hypot(ex, ey) >= MOVE_M else ""
        a, b = (r.get("shelter_s_from") or r.get("shelter_auto_from")), (r.get("shelter_s_to") or r.get("shelter_auto_to"))
        if a not in ("", None) and b not in ("", None):
            a, b = sorted([float(a), float(b)])
            rec["dm_roof_m"] = round(max(a - ds, ds - b, 0), 1)
        cx, cy = x0, y0
        if POLE_SOURCE == "datamall":
            rec["action"] = "move"
            cx, cy = x0 + ds * u[0], y0 + ds * u[1]          # pole moves along the road only
            for k in ("from", "to"):
                v = r.get(f"shelter_s_{k}") or r.get(f"shelter_auto_{k}")
                if v not in ("", None):
                    rec[f"shelter_s_{k}_new"] = round(float(v) - ds, 1)
        rec["note"] = (f"pole on DataMall point: {ds:+.1f} m" if POLE_SOURCE == "datamall" else
                       f"DataMall point {ds:+.1f} m along / {dn:+.1f} m across from the pole") + (f"; {why}" if why else "")
        # panoramas: a pole moved a little keeps its own; one moved further takes the nearest at the new pole and ±15 m
        for role, off in (("C", 0), ("U", -15), ("D", 15)):
            if POLE_SOURCE != "datamall" or abs(ds) < SVI_KEEP:
                rec[f"sv_{role}"] = idx + role if any(q[0]["sample_id"] == idx + role for q in panos) else ""
                continue
            px, py = cx + off * u[0] - 3 * n[0], cy + off * u[1] - 3 * n[1]
            best = min(panos, key=lambda q: math.hypot(q[1] - px, q[2] - py))
            if math.hypot(best[1] - px, best[2] - py) <= SVI_M:
                rec[f"sv_{role}"] = best[0]["sample_id"]
        lon, lat = to_wgs.transform(cx, cy)
        rec["lat_new"], rec["lon_new"] = round(lat, 7), round(lon, 7)
        rec["x3414_new"], rec["y3414_new"] = round(cx, 3), round(cy, 3)
        out.append(rec)
    keys = list(out[0].keys()) + [k for k in ("lat_new", "lon_new", "x3414_new", "y3414_new") if k not in out[0]]
    with OUT.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(out)
    for a in ("discard",):
        print(a, [(x["stop_idx"], x["dist_m"], x["ds_m"]) for x in out if x["action"] == a])
    print("renamed", [(x["stop_idx"], x["stop_name"], x["name_new"]) for x in out if x["name_new"]])
    print("no panorama:", [(x["stop_idx"], r) for x in out if x["action"] != "discard" for r in "CUD" if not x[f"sv_{r}"]])
    print("pole source:", POLE_SOURCE, "· DataMall point > 5 m off the labelled roof:", [(x["stop_idx"], x["dm_roof_m"]) for x in out if x["dm_roof_m"] not in ("", None) and float(x["dm_roof_m"]) > 5])
    print(OUT)


if __name__ == "__main__":
    main()
