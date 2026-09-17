# CityTwin Trebinje — phases

Version 0.1 · 2026-09-17. Three kinds of work are kept apart: **what we can do now** (open data,
no permission), **what needs time** (modelling, calibration), and **what needs special data**
(only the City or its companies have it).

## Phase 0 — "Trebinje in a day" (now → meeting next week)

Goal: walk into the meeting with a working map, not slides about a map.

| Step | Output | Data | Effort |
|---|---|---|---|
| 0.1 | Permission ledger for all open sources | licences, robots | 0.5 d |
| 0.2 | L0 ground: boundary, DEM, water, streets, buildings, land cover, population grid | Overture, Copernicus DEM, WorldCover, GHS-POP | 1 d |
| 0.3 | L0 acceptance test + building completeness sample | L0 + imagery | 0.5 d |
| 0.4 | **Demo 1 — Solar screening** of all roofs, top-20 public buildings | L0 + PVGIS-class irradiance + DEM horizon | 1 d |
| 0.5 | **Demo 2 — Heat & green**: summer LST composite, NDVI, 3-30-300 | Landsat, Sentinel-2 | 1–2 d |
| 0.6 | **Demo 3 — Tourism walking & parking catchments** (centre, Old town, bridge, Gračanica, Tvrdoš) | L0 network + POIs | 1 d |
| 0.7 | Web face: one map, three questions, 2.5D buildings, honest labels, mobile | MapLibre | 1–2 d |
| 0.8 | Presentation (SR) built around the three questions + the request list | — | 1 d |

Exit criterion: each demo answers its question on the map, and each value says where it came from.

## Phase 1 — Pilot with the City (months 1–3)

Choose **2–3 questions together** with the City (candidates: solar on public buildings, heat and
trees, parking in the centre). For the chosen ones:
- sign a data-sharing note; receive the request list items (below);
- georeference the regulation plans for the pilot area;
- calibrate v1 algorithms; field checks (heat walk, parking count on a summer Saturday);
- deliver: web tool for City staff + a short methods report per question.

## Phase 2 — Models that answer "what if" (months 3–9)

Scenario engine live; SUMO for the centre; SOLWEIG street heat; energy retrofit priority for the
public portfolio; development impact (shadow, views, demand); citizen reporting map.

## Phase 3 — The living model (months 9–18)

LoD2 3D city (LiDAR/photogrammetry), live senses (parking, river, weather), decision log inside
City procedures, training of City staff, EU funding (Interreg Croatia–BiH–Montenegro with
Dubrovnik/Herceg Novi; Horizon Europe pilot-city role; UNDP BiH partnership).

---

## Special data — the request list (only the City or its companies have it)

| # | Data | Holder | Serves | Phase |
|---|---|---|---|---|
| R1 | Regulation / zoning plans in GIS (SHP/DWG/GPKG) | Grad Trebinje | A8, A9, all | 1 |
| R2 | Cadastre & building extract, orthophoto GeoTIFF, LiDAR/DEM if any | RUGIPP (RS geodetic authority) | L0, A1, A8 | 1 |
| R3 | Register of public buildings + energy bills (UNDP EMIS data) | Grad | A7, A1 | 1 |
| R4 | Parking zones, capacities, occupancy/payment by hour | Parking servis | A4 | 1 |
| R5 | Traffic studies, counts, geocoded accidents | Grad, Putevi RS, police | A4 | 1–2 |
| R6 | Monthly guest arrivals/nights, e-Turizam data (aggregated) | Turistička organizacija | A5 | 1 |
| R7 | River levels, dam releases, historic floods | HET, Vode Srpske, RHMZ | A6 | 2 |
| R8 | Risk assessment + hazard maps, fire-brigade interventions | Grad / civil protection | A10 | 2 |
| R9 | Heritage protection zones in GIS | Heritage institute RS | A9 | 1–2 |
| R10 | Tree / green-space inventory | Komunalno | A3 | 1 |
| R11 | Public lighting inventory | Grad | A11, energy | 2 |
| R12 | Bus lines & timetables | Grad / operator | A4, A5 | 2 |
| R13 | Budget and investment plan (spreadsheet) | Grad | A5 decisions | 1 |
| R14 | Water network (kept local, never published) | Vodovod | A10 | 3 |

## Questions that came out of the first build simulation

These are real questions, raised by trying to build Phase 0 against real sources:

1. **Which 2–3 questions does the City care about most?** Phase 0 prepares three demos
   (solar, heat/green, tourism/parking); the City picks.
2. **Who is the counterpart at the City** (urbanism department? mayor's office? development
   agency) and who presents with you?
3. **Is the goal a funded project?** If yes, Interreg Croatia–BiH–Montenegro fits the themes
   (climate, tourism, heritage); UNDP BiH already runs an innovation hub in Trebinje.
4. **OSM access policy:** Overpass, Geofabrik and planet.openstreetmap.org all disallow automated
   clients in robots.txt (BEOPS recorded the same and did not circumvent). Phase 0 therefore uses
   Overture Maps (which carries OSM data under ODbL, on AWS open data). Keep this rule?
5. **PVGIS API:** the JRC host disallows all robots in robots.txt although the API is documented
   for programmatic use. Use it (documented API ≠ crawling), or use Global Solar Atlas rasters
   instead?
6. **Official CRS** for deliverables to the City (RS still uses MGI 1901 / Balkans zone 6 in many
   offices?) — computation stays in ETRS89 / UTM 34N.
7. **Language of the tool:** Serbian (Cyrillic? Trebinje official documents use Cyrillic) plus English.

---

## Phase 0 status (2026-09-17, 02:00)

| Step | Status | Result |
|---|---|---|
| 0.1 ledger | done | 12 sources, 4 refused by robots (Overpass, Geofabrik, planet OSM, BBBike), PVGIS pending |
| 0.2 L0 | done | Overture 2026-08-19.0: 11 654 buildings, 3 132 street segments, 505 places, 3 405 land-use, 90 water; DEM 30 m; WorldCover 10 m |
| 0.3 acceptance | partial | numbers in `data/L0_REPORT.json`; the 200-point imagery sample is still to do; building height known for <1 % (floors must come from the City or LiDAR) |
| 0.4 solar | done v0 | 9 414 roofs ≥ 30 m² → ~163 MWp / ~195 GWh/yr theoretical; 16 public buildings detected → ~3.5 MWp / ~4.2 GWh/yr; horizon loss median 1.8 % |
| 0.5 heat & green | done v0 | summer surface temp. (Landsat, ~10:00): urban 38.7 °C vs surroundings 33.4 °C; 1 306 priority cells |
| 0.6 walk & parking | done v0 | 6 checked anchor points, 159 mapped parking areas; 13.1 % of building footprint area within 800 m of the centre is > 5 min walk from mapped parking |
| 0.7 face | done v0 | `node faces/serve.js trebinje 4870` — 4 questions, 3D, Serbian labels, evidence badges |
| 0.8 presentation | next | |

---

## Decisions 2026-09-17 (decided by the authors)

| # | Question | Decision | Why |
|---|---|---|---|
| D-004 | OSM access | **Overture Maps only.** Overpass, Geofabrik, planet.osm and BBBike stay refused (robots.txt). | Same ground-zero rule as BEOPS; Overture carries OSM under ODbL with no refusal. |
| D-005 | PVGIS | **Not used.** Irradiance = Global Solar Atlas (World Bank, CC-BY-4.0), per building. | JRC host disallows all robots; GSA is a documented download and already gives GHI/DIF/PVOUT at ~250 m. |
| D-006 | CRS | **Compute and deliver in ETRS89 / UTM 34N (EPSG:25834)** = the RS reference system (Zakon o premjeru i katastru RS, čl. 31–33; REFRS/SRPOS). **Accept and export the old DKS** (MGI 1901 / Balkans zone 6, EPSG:8678, ex-3908) with the EPSG Bosnia-and-Herzegovina 7-parameter operation (~1 m), chosen explicitly because PROJ otherwise may pick the Croatian set. Official RUGIPP transformation requested under R2 for cadastral-grade work. | Tested 2026-09-17 on the Trebinje centre. |
| D-007 | Script | **Cyrillic by default** (official script of the City), Latin and English as toggles in the face; public repo/docs stay English. | City documents are Cyrillic; the page transliterates its own text. |
| D-008 | Question 4 (City counterpart, choice of questions, funding) | **Deferred** to the project/funding track. The deck ends with the three next steps only. | Authors, 2026-09-17. |

## Phase 0 status update (2026-09-17, 08:40)

- 0.3 acceptance: GHSL comparison done instead of a manual 200-point sample — footprints cover **51 %** of GHSL built surface in 638 built cells; **213 cells** flagged as possibly missing buildings (`L0Q_completeness_cells.geojson`). GHSL tends to overestimate small towns, so this is a list to check, not a count of missing buildings.
- Heights: 11 204 buildings from GHSL average gross building height (2018, 100 m cell mean, max 7.5 m), 444 default 6 m, 6 from Overture — **estimated**, flattens real variation.
- Population: GHS-POP 2025 gives 20 752 people inside the core bbox (official city total 28 626 covers the whole territory); 19 112 assigned to buildings by floor area.
- 0.8 presentation: done as a Cyrillic deck (13 slides) with four map views.
- Exports for the City: `data/export/*_25834.gpkg` and `*_8678.gpkg`.
