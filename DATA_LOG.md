# Data upload record

Record of the database files uploaded with the platform. Hashes let you check that a file is the same version the platform was built and reviewed with.

## Upload 1 — 2026-10-31

- **Source folder:** `AR5801/0-Week review/week11/01-Platform` and `week11/02-Data` (the week-11 review copy; `02-Data` holds copies of the week-9 / week-10 sources so the platform builds on its own).
- **Uploaded:** platform source and build, correction records, sample exports, the stop database.
- **Not uploaded:** regulation / standard documents and literature (`week11/literatures/`), the DataMall API key, old backups (`_backup_2026-10-27_pre-nav/`), Rhino / Grasshopper models, posters and presentations.
- **Build in the repo:** `LTA-Against Air Pollution Platform.html` as built on 2026-10-29 from these files; 85 stops after discarding 3 out-of-service stops.

| File | Size | Last modified | SHA-256 (first 12) | Content |
|---|---:|---|---|---|
| `02-Data/baseline_fixes.json` | 0.4 KB | 2026-10-26 | `4ca88c153eca` | baseline corrections reviewed per stop in the week10 workbench |
| `02-Data/fetch_stop_bus_types.py` | 1.9 KB | 2026-10-24 | `a19d4f7a9d7c` | script that produced stop_bus_types.json (needs a DataMall key, not included) |
| `02-Data/shelter_far_from_pole_v2.csv` | 1.8 KB | 2026-10-26 | `71ecea1cdc31` | 14 stops whose labelled shelter is far from the pole (QA list) |
| `02-Data/shelter_off_lta_position_v3.csv` | 4.5 KB | 2026-10-26 | `9b30eaa12021` | 46 stops whose shelter is offset from the LTA point (QA list) |
| `02-Data/stop_bus_types.json` | 1.9 KB | 2026-10-24 | `2b8209676882` | bus types (SD/DD/BD) and services at the 3 demo stops, DataMall BusArrival snapshot 2026-10-24 23:05 |
| `02-Data/stop_dataset_v2.csv` | 51.3 KB | 2026-10-26 | `136d2d32d349` | 88 sampled stops: prototype, shelter extent, zone, rear depth, load index, etc. (week10/02_prototypes) |
| `02-Data/stop_location_fix.py` | 9.1 KB | 2026-10-26 | `401ed03ab818` | script that produced stop_location_fixes_v1.csv (needs a DataMall key + week9 files, not included) |
| `02-Data/stop_location_fixes_v1.csv` | 20.4 KB | 2026-10-26 | `fe882f3d717c` | LTA DataMall BusStops check: 85 keep / 3 discard (out of service), current names, pole moves (2026-10-26) |
| `02-Data/stop_metrics_v1.geojson` | 68.9 KB | 2026-10-26 | `8afee09f56e3` | 88 stop points (SVY21, EPSG:3414), traffic bearing, stop side (week10/01_metrics) |
| `02-Data/stop_wind_conditions.xlsx` | 24.9 KB | 2026-10-26 | `23b6d5472b40` | wind per stop from the nearest NEA weather station: Typical / Adverse / Seasonal directions (sheets: stop_wind_3conditions, stations, notes) |
| `02-Data/svi_match.csv` | 69.8 KB | 2026-10-26 | `eb578de9d02d` | 285 Street View panorama IDs matched to stops (C/U/D views); IDs and coordinates only, no images |
| `02-Data/crops/ (89 jpg)` | 13,677.0 KB | 2026-10-26 | `8a86fef9f240` | 89 OneMap satellite crops, zoom 20 (about 0.15 m/px); used as the base image in the platform |
| `01-Platform/data_fixes.json` | 0.8 KB | 2026-10-28 | `24249fc82068` | corrections made inside the platform on top of the baseline (_rev versioned) |
| `01-Platform/exports/P041_transversal_options_archive.json` | 262.4 KB | 2026-10-29 | `70964496814a` | exported Archive: 4 saved design options for P041 |
| `01-Platform/exports/P065_lateral_geometry_local.dxf` | 34.2 KB | 2026-10-28 | `ae5cbcb21f8d` | sample DXF export (local s,y metres, BS_* layers) for P065 |
| `01-Platform/exports/P065_lateral_gh_params.json` | 2.7 KB | 2026-10-28 | `5f35492139ce` | sample Grasshopper parameter package (gh_sliders, dimensions) for P065 |
| `01-Platform/exports/P065_lateral_scenario.json` | 11.6 KB | 2026-10-28 | `e748e8fbd392` | sample scenario export (elements, zones, wind, vehicles) for P065 |
The crops row hashes all 89 images together (SHA-256 of the concatenated per-file SHA-256 digests, sorted by name).

## Correction records

Field-level fixes are kept separate from the source data and applied in this order when the page is built:

1. `02-Data/baseline_fixes.json` – reviewed in the week-10 workbench (P006 bus bay).
2. `01-Platform/data_fixes.json` – made in the platform (P006 bay; P065 `_rev 1`: pole 55.5 m downstream of the data point, shelter s −10 → −1.5, front 4.05 m offset; to be checked on Street View).

When adding a fix, give it a `_note` saying what was changed and from which evidence, bump `_rev` for that stop, and add an entry under a new "Upload" heading here.
