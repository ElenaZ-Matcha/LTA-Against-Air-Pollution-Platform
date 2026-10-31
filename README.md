# LTA-Against Air Pollution Platform (LTA-AAP)

A browser tool for redesigning bus stops in Singapore so that waiting passengers are less exposed to bus exhaust. The designer picks a stop, reads its site conditions, tries a design prototype, edits it on the satellite plan, checks it, saves options and exports them to Grasshopper / Rhino for detailed design.

> **This is a student project.** It was made for the architecture design studio **AR5801, National University of Singapore (NUS), Semester 1 2026**. It is **not** an LTA product. LTA has not commissioned, reviewed or endorsed it.

## Who it is for

| | |
|---|---|
| **Client (assumed)** | An **LTA bus stop designer**. This client and their brief were **set by the authors** for the studio; there is no real client. |
| **What that designer does with it** | Fast comparison of options at one stop, then hand-off to Grasshopper for detailed modelling. |
| **Not for** | Passengers, the public, approval submissions, or engineering / health decisions. |

The designer's workflow follows the left navigation of the page:

1. **Find stop** – map of the sampled stops, coloured by an indicative exposure grade under the worst wind direction.
2. **Baseline** – existing shelter, bus bay, pole, bollards, columns and five zones (Boarding, Crossing, Waiting, Filtering, Bicycle) drawn on the satellite crop.
3. **Edit** – apply a prototype (*In-place*, *Longitudinal*, *Transversal*) and change components and zones.
4. **Export & check** – geometry checks, wind and bus-exhaust scenario, DXF / JSON / PNG / GH package.
5. **Design** – 2D plan beside a 3D preview built from the DXF layers.
6. **Archive / Analysis** – saved options, compared under the same scenario, across stops.

## Repository contents

```
01-Platform/
  LTA-Against Air Pollution Platform.html   built page (open this)
  platform_template.html                    source of the page
  make_platform.py                          builds the page from 02-Data + data_fixes.json
  zoning design.html, zoning_template.html, make_zoning.py
                                            standalone zoning editor (early prototype, now merged into the platform)
  serve_platform.py                         local server; exports are written into 01-Platform/exports/
  data_fixes.json                           corrections made inside the platform
  exports/                                  sample exports (P041 archive, P065 DXF / GH params / scenario)
02-Data/                                    the project database used by the platform
DATA_LOG.md                                 upload record of every data file (source, date, size, hash)
```

## How to run

Open the page directly:

```
01-Platform/LTA-Against Air Pollution Platform.html
```

Or run the local server from the repository root (needed so that the non-demo satellite crops in `02-Data/crops/` load and exports are saved to disk):

```bash
python 01-Platform/serve_platform.py 8765
```

then open `http://localhost:8765/01-Platform/LTA-Against%20Air%20Pollution%20Platform.html`. The server listens on 127.0.0.1 / ::1 only.

Rebuild after changing the data or the template (needs Python 3 with `Pillow` and `pyproj`):

```bash
python 01-Platform/make_platform.py
```

## Database

`02-Data/` holds the stop database the platform is built from; `DATA_LOG.md` records each uploaded file, where it came from and its date. In short:

- **88 sampled bus stops**; **85** are kept after an LTA DataMall check (3 out of service are skipped).
- **3 demo stops** carry full detail and embedded satellite images: P021 Blk 662A (22501, Boon Lay), P040 NTUC FairPrice (17239, Clementi), P039 BLK 329 (17169, Clementi).
- Coordinates are SVY21 (EPSG:3414), metres. The editor works in local `(s, y)`: `s` positive downstream with the traffic, `y` from the boarding kerb towards the footpath; `s = 0` is the LTA data point.
- `data_fixes.json` and `02-Data/baseline_fixes.json` are the correction records on top of the source data. They are versioned with `_rev`; a newer system revision wins over a copy saved in the browser.

## Limits — read before using any result

**Scope**
- 88 sampled stops in the study areas, not the whole island. A rule that fits these samples is not proven for every stop in Singapore.
- Prototype rules say which operations are *possible* at a stop. They do not say a stop *should* be changed, and they are not a cost estimate.

**Air quality**
- Exposure is an **indicative index** from a simplified plume model, used only to compare options under the same wind and bus scenario. It is **not CFD, not a measurement, not µg/m³**, and must not be read as a health benefit.
- The barrier factor (×0.5, after Baldauf et al. 2016) and the vegetation factor are demonstration assumptions. Calm / low wind is outside what the model can show.
- Map grades use provisional thresholds (8 / 12 / 16). The worst single wind direction is a screening case, not the most common direction or a yearly exposure.
- Wind directions are meteorological FROM (0° = north). The wind buttons in the page (NE / SW monsoon, along road, worst) still use 30° / 210° defaults that do not fully match the per-stop data in `stop_wind_conditions.xlsx`.

**Geometry and data**
- Shelters, bays and poles were labelled on satellite crops. Some are marked "check on Street View / site", e.g. P006 (under a viaduct) and P065 (pole moved 55.5 m downstream). Verify on site before design use.
- Bus types are a DataMall snapshot of 2026-10-24 for the 3 demo stops only; other stops default to single- and double-deck.
- The 3D view is a three.js preview made in the page, not Grasshopper or Rhino. The GH package covers flat roofs; gable roofs are preview only.
- Zones are for planning and checking; DXF / 3D solids are generated from components, not from zones.

**Regulations**
- The platform does **not** check compliance with LTA, BCA, URA or any other code. Passing its checks is not approval.
- **Regulation and standard documents (e.g. LTA standard details, design criteria) are intentionally not included in this repository.** Get the current versions from the issuing authority.

**Storage**
- The Archive is kept in the browser (`localStorage`), separately for every address (`file://` and `http://localhost:8765` are different). Use *Export archive* / *Import archive* to move or back up options; nothing is stored on a server.

## Data sources and terms

- **LTA DataMall** – bus stops and bus arrival (bus types). The two fetch scripts in `02-Data/` need your own DataMall AccountKey (file or env `LTA_ACCOUNT_KEY`); **no key is included**. They also read week-9 project files that are not in this repository, so they are kept as a record and will not run as-is.
- **OneMap / Singapore Land Authority** – map tiles and the satellite crops in `02-Data/crops/`. © OneMap, Singapore Land Authority; used here for non-commercial academic work.
- **Google Street View** – `svi_match.csv` stores panorama IDs and coordinates only; the page links out to Google Maps. No Street View images are stored.
- **NEA weather stations** – basis of the per-stop wind directions.

Users of this repository are responsible for following each provider's terms.

## Notes

- Internal keys differ from the names in the UI: *Longitudinal* = `split`, *Transversal* = `lateral` (formerly called P-LAT, now P-TSV).
- Exports in `01-Platform/exports/` are samples from the review on 2026-10-28/29, not final designs.
- Status: course work in progress (week 11 review). No warranty; do not use for real projects.

---

### 中文简介

本仓库是 NUS AR5801 建筑设计课程的学生项目。"LTA 公交站设计师"是作者为课程设定的假想客户，项目与 LTA 无关、未经其审核。平台用于在同一风况与车辆情景下快速比较公交站方案，并交给 Grasshopper 深化。暴露值是示意指数，不是实测或健康结论；平台不做法规检查，本仓库也不包含任何法规/规范文件。
