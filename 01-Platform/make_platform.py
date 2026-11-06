"""Build the LTA-Against Air Pollution Platform: all v2 stops (Find stop map), three of them demo stops.

Reads only ../02-Data (copies of the week9 / week10 sources, so this folder builds on its own):
       stop_dataset_v2.csv        (week10/02_prototypes)   prototype, shelter, zone, rear depth ...
       stop_metrics_v1.geojson    (week10/01_metrics)      traffic bearing, stop side, SVY21 point
       crops/<stop_idx>.jpg       (week10/01_metrics/crops) satellite crops (embedded)
       svi_match.csv              (week9/scrap)            outdoor Street View panoramas per stop
       stop_bus_types.json        (fetch_stop_bus_types.py) bus types seen at each stop (DataMall BusArrival)
       stop_location_fixes_v1.csv (week10/01_metrics)      LTA DataMall check: drops stops out of service, current names,
                                                           checked pole moves
       baseline_fixes.json        (week10 workbench)       baseline reviewed per stop, written by serve_workbench.py
       data_fixes.json            (this folder)            corrections made in the platform, on top of the baseline
Writes LTA-Against Air Pollution Platform.html  (from platform_template.html)

Usage: python make_platform.py
"""
import base64
import csv
import json
import math
from pathlib import Path

from PIL import Image
from pyproj import Transformer

import os

HERE = Path(__file__).resolve().parent
# week12 builds on the week11 data (no copy of 02-Data here); a local ../02-Data wins when present
DATA = next(p for p in (HERE.parent / "02-Data", HERE.parent.parent / "week11" / "02-Data") if p.exists())
CROPS_HREF = Path(os.path.relpath(DATA / "crops", HERE)).as_posix()   # crops linked from the built page

NAME = "LTA-Against Air Pollution Platform"
# demo stops: stop_idx -> (demo operation, in-place variant)
DEMO = {
    "P021": ("split", ""),          # Blk 662A (22501), Boon Lay
    "P040": ("inplace", "R1"),      # NTUC FairPrice (17239), Clementi
    "P039": ("inplace", "R1+R2"),   # BLK 329 (17169), Clementi
}
# stop_dataset_v2 fields the platform uses (same list as week10/03_editor/make_editor.py)
KEEP = [
    "stop_idx", "bus_stop_id", "station", "stop_name", "road_name", "prototype", "operation_ladder",
    "decisive_reason", "lateral", "longitudinal_ok", "free_end", "walk_route", "rear_space", "rear_obstacle",
    "rear_depth_m", "green_type", "shelter_src", "shelter_s_from", "shelter_s_to", "shelter_auto_from",
    "shelter_auto_to", "berths", "stop_zone_len_m", "stop_type_now", "bay_depth_m", "under_viaduct",
    "load_index", "n_services", "pv_wkday_peak_hr", "osm_lanes", "kerb_from_axis_m",
    "through_kerb_from_axis_m", "d_road_axis_m", "bollards_30m", "ne_downwind", "sw_downwind",
    "d_signal_m",
]
Z = 20      # OneMap zoom used by week10/01_metrics/site_geometry.py for the crops
LAT = 1.35  # metres per pixel hardly changes across Singapore


def sv_panos(idx, panos, pick=None):
    """Matched outdoor panoramas per stop; the page builds the links and aims each view at the current shelter.
    pick: role -> sample_id re-matched for a moved pole (blank = none, the page then links by coordinates)."""
    out = {}
    for role in "CUD":
        p = panos.get(pick[role] if pick is not None else idx + role)
        if p and p.get("pano_lat"):
            out[role] = {"pano": p["panoid"], "lat": round(float(p["pano_lat"]), 7), "lon": round(float(p["pano_lon"]), 7)}
    return out


def main():
    geo = json.loads((DATA / "stop_metrics_v1.geojson").read_text(encoding="utf-8"))
    pts = {f["properties"]["stop_idx"]: f for f in geo["features"]}
    rows = list(csv.DictReader((DATA / "stop_dataset_v2.csv").open(encoding="utf-8-sig")))
    types_path = DATA / "stop_bus_types.json"
    bus_types = json.loads(types_path.read_text()) if types_path.exists() else {}
    svi = DATA / "svi_match.csv"
    panos = {x["sample_id"]: x for x in csv.DictReader(svi.open(encoding="utf-8-sig"))} if svi.exists() else {}
    loc_path = DATA / "stop_location_fixes_v1.csv"
    loc = {x["stop_idx"]: x for x in csv.DictReader(loc_path.open(encoding="utf-8-sig"))} if loc_path.exists() else {}
    stops, sat = [], {}
    mpp = 156543.03 * math.cos(math.radians(LAT)) / 2 ** Z
    to_wgs = Transformer.from_crs(3414, 4326, always_xy=True)
    for r in rows:
        lf = loc.get(r["stop_idx"], {})
        if lf.get("action") == "discard":
            print(f"{r['stop_idx']} skipped: {lf['note']}")
            continue
        d = {k: r.get(k, "") for k in KEEP}
        d["demo_op"], d["demo_variant"] = DEMO.get(r["stop_idx"], ("", ""))
        if lf.get("name_new"):
            d["stop_name_old"], d["stop_name"] = d["stop_name"], lf["name_new"]
        if lf.get("action") == "move":      # pole on the DataMall point; the shelter stays where it was labelled
            d["pole_ds_m"] = float(lf["ds_m"])
            if lf.get("shelter_s_from_new"):
                d["shelter_s_from"], d["shelter_s_to"] = lf["shelter_s_from_new"], lf["shelter_s_to_new"]
        bt = bus_types.get(r["stop_idx"], {})
        d["bus_types"] = sorted(bt.get("types") or ["SD", "DD"], key=["SD", "DD", "BD"].index)
        d["bus_services"] = {n: v["types"] for n, v in bt.get("services", {}).items()}
        f = pts.get(r["stop_idx"])
        if f:
            p = f["properties"]
            d["direction"] = p.get("direction")
            d["stop_side"] = p.get("stop_side") or "left"
            d["x3414"], d["y3414"] = f["geometry"]["coordinates"][:2]
            lon, lat = to_wgs.transform(d["x3414"], d["y3414"])
            d["lat"], d["lon"] = round(lat, 7), round(lon, 7)
            d["sv"] = sv_panos(r["stop_idx"], panos, {k: lf[f"sv_{k}"] for k in "CUD"} if lf.get("action") == "move" else None)
            d["map_url"] = f"https://www.google.com/maps/@{lat:.6f},{lon:.6f},45m/data=!3m1!1e3"
        stops.append(d)
        crop = DATA / "crops" / f"{r['stop_idx']}.jpg"
        if crop.exists():
            w = round(Image.open(crop).size[0] * mpp, 3)
            # demo stops embedded; the others linked, relative to the page (week11/02-Data/crops from week12)
            sat[r["stop_idx"]] = ({"src": "data:image/jpeg;base64," + base64.b64encode(crop.read_bytes()).decode(), "w": w}
                                  if r["stop_idx"] in DEMO else {"href": f"{CROPS_HREF}/{r['stop_idx']}.jpg", "w": w})
    stops.sort(key=lambda d: (d["stop_idx"] not in DEMO, list(DEMO).index(d["stop_idx"]) if d["stop_idx"] in DEMO else 0, d["stop_idx"]))
    # baseline from the week-10 workbench, then the platform's own corrections on top (field by field)
    fixes = {}
    for path in (DATA / "baseline_fixes.json", HERE / "data_fixes.json"):
        if path.exists():
            for k, v in json.loads(path.read_text(encoding="utf-8")).items():
                if k in {d["stop_idx"] for d in stops}:
                    fixes[k] = {**fixes.get(k, {}), **v}
    # archive carried into every browser address: all archive exports (*archive*.json) in this folder or exports/,
    # merged by id (newer file wins); the page adds each entry once
    arcs = sorted([*HERE.glob("*archive*.json"), *(HERE / "exports").glob("*archive*.json")], key=lambda p: p.stat().st_mtime)
    seed_by_id = {}
    for p in arcs:
        j = json.loads(p.read_text(encoding="utf-8"))
        for a in (j if isinstance(j, list) else [j]):
            if isinstance(a, dict) and a.get("id") and a.get("els") is not None and a.get("stop_idx"):
                seed_by_id[a["id"]] = a
    seed = sorted(seed_by_id.values(), key=lambda a: a.get("ts", ""), reverse=True)
    if arcs:
        print(f"archive seed: {len(seed)} item(s) from {', '.join(p.name for p in arcs)}")
    tpl = (HERE / "platform_template.html").read_text(encoding="utf-8")
    html = (tpl.replace("/*__DATA__*/[]", json.dumps(stops, ensure_ascii=False))
               .replace("/*__SAT__*/{}", json.dumps(sat))
               .replace("/*__FIXES__*/{}", json.dumps(fixes, ensure_ascii=False))
               .replace("/*__ARCHIVE__*/[]", json.dumps(seed, ensure_ascii=False).replace("</", "<\\/")))
    out = HERE / f"{NAME}.html"
    out.write_text(html, encoding="utf-8")
    print(f"{out}  ({len(stops)} stops, demo: {', '.join(d['stop_idx'] + ' ' + '/'.join(d['bus_types']) for d in stops if d['demo_op'])})")


if __name__ == "__main__":
    main()
