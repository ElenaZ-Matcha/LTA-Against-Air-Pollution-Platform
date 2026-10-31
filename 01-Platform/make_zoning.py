"""Build the standalone zoning editor: five zones per stop, edited on the platform's baseline.

Takes the stop data, satellite crops and data fixes already embedded in the platform build
(LTA-Against Air Pollution Platform.html, written by make_platform.py), so both pages use the same stops.
Writes zoning design.html  (from zoning_template.html). Run make_platform.py first when the data changes.

By default only the demo stop P021 (Blk 662A) goes in, which keeps the page small and fast;
--stops P021 P040 picks others, --all puts in every stop.

Usage: python make_zoning.py [--stops P021 ...] [--all]
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLATFORM = HERE / "LTA-Against Air Pollution Platform.html"
OUT = HERE / "zoning design.html"


def embedded(html, prefix):
    """JSON value written right after `prefix` in the platform build."""
    i = html.index(prefix) + len(prefix)
    value, _ = json.JSONDecoder().raw_decode(html, i)
    return value


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stops", nargs="+", default=["P021"])
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    html = PLATFORM.read_text(encoding="utf-8")
    stops = embedded(html, "const STOPS = ")
    sat = embedded(html, "const SAT = ")
    fixes = embedded(html, "const FIXES = ")
    if not args.all:
        keep = set(args.stops)
        stops = [s for s in stops if s["stop_idx"] in keep]
        missing = keep - {s["stop_idx"] for s in stops}
        if missing:
            raise SystemExit(f"not in the platform build: {', '.join(sorted(missing))}")
        sat = {k: v for k, v in sat.items() if k in keep}
        fixes = {k: v for k, v in fixes.items() if k in keep}
    tpl = (HERE / "zoning_template.html").read_text(encoding="utf-8")
    page = (tpl.replace("/*__DATA__*/[]", json.dumps(stops, ensure_ascii=False))
               .replace("/*__SAT__*/{}", json.dumps(sat))
               .replace("/*__FIXES__*/{}", json.dumps(fixes, ensure_ascii=False)))
    OUT.write_text(page, encoding="utf-8")
    print(f"{OUT}  ({len(stops)} stop(s): {', '.join(s['stop_idx'] for s in stops)}, {OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
