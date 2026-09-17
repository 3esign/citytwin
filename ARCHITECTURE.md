# CityTwin — architecture of a decision model for any city ("City X")

Version 0.1 · 2026-09-17 · pilot city: Trebinje (Republika Srpska, BiH)
Status: first architecture from the initial brainstorm. Everything here is a proposal to be tested by building.

---

## 1. What this is, in one sentence

A city model that answers **"what happens if we do this?"** — not a 3D picture of a city, but a
chain of *layers → algorithms → scenarios → decisions*, where every number carries its source,
time, place, unit and permission.

The 3D view is one of its faces. The product is the answer to a question.

## 2. Design rules (inherited from BEOPS and Pazarac, generalised)

1. **Question first.** Nothing is collected or modelled unless it serves a named question
   ("Where do we put solar panels first?"). Each question has an owner at the City.
2. **Legal ground zero.** Every source passes a permission check before collection
   (licence, terms, robots.txt, personal-data law). Unknown is never permission. Refusals are
   recorded, never circumvented.
3. **Five evidence states** for every value: *Observed · Untimed · Estimated · Forecast ·
   Unavailable*. Missing is not zero. A model output is always *Estimated* and says so.
4. **City-agnostic core, city pack per city.** Code never names a city. A city is a
   configuration folder (`cities/<id>/city.json`): boundary, CRS, sources, local adapters,
   questions, weights.
5. **Layers are versioned, algorithms are pure.** An algorithm reads named layer versions and
   writes a new layer version. A scenario is a *patch* on layers; only downstream algorithms
   rerun (a build graph, like `make`).
6. **Honest resolution.** Every output declares the scale at which it may be read
   (building / block / neighbourhood / city). No false precision.
7. **Open stack, no lock-in.** Open formats (GeoPackage, GeoParquet, COG, CityJSON, 3D Tiles),
   open standards (OGC API, ISO/IEC 30173 vocabulary), open-source engines. The City owns its data.
8. **Beautiful and serious.** Urban-design grade cartography; a decision maker should read
   a map in five seconds.

## 3. The layer stack

```
 L6  FACES        planner map 2D/3D · question box · citizen map · report export
 L5  DECISIONS    scenario workbench · multi-criteria ranking · cost/benefit · decision log
 L4  ALGORITHMS   solar · heat · green · mobility/parking · tourism flow · water · energy
                  retrofit · development impact · heritage · emergency · participation
 L3  LIVE SENSES  weather · river level · parking occupancy · citizen reports · air
 L2  PERIODIC     satellite composites · census/estimates · tourism nights · energy bills
                  · traffic counts · fire/flood events
 L1  THEMATIC     plans (georeferenced) · cadastre · public-building register · heritage
     BASES        register & zones · parking zones · green inventory · POIs · utilities
 L0  GROUND       (a) legal & permission ledger
                  (b) reference frame: CRS, grid, time, identity, evidence states
                  (c) the physical ground: boundary · terrain · water · network ·
                      buildings · land cover · population grid
```

### 3.1 Layer 0 — the ground everything stands on

L0 is what any city in Europe can have **in one day, from open data, without asking anyone**.
It is the part that makes the system city-agnostic.

| # | Component | What it is | Open source for City X | Trebinje status |
|---|---|---|---|---|
| L0.a | **Permission ledger** | one record per source: licence, terms, robots, personal data, decision, date | own (from BEOPS `legal_capture`) | started (`registry/sources.jsonl`) |
| L0.b1 | **CRS** | computation CRS + official CRS | UTM/ETRS89 zone of the city; national CRS | compute in ETRS89 / UTM 34N (EPSG:25834); official RS/BiH CRS to confirm (MGI 1901 / Balkans zone 6, EPSG:3908?) |
| L0.b2 | **Grid** | common analysis cells for fusion and privacy | INSPIRE 100 m grid + H3 res 10 (~15 000 m²) | to build |
| L0.b3 | **Time model** | observed time, received time, valid period | own | from BEOPS |
| L0.b4 | **Identity** | stable IDs for buildings, segments, places | Overture GERS IDs; own IDs for local objects | to build |
| L0.c1 | **Boundary** | city, settlements, urban area, local communities (MZ) | OSM admin relations / geoBoundaries; official from RUGIPP | open (OSM/Overture) |
| L0.c2 | **Terrain** | DEM, slope, aspect, horizon, flow | Copernicus DEM GLO-30 (AWS open data) | tile N42 E018 located |
| L0.c3 | **Water** | river, streams, reservoirs, flow lines, HAND | OSM/Overture water + DEM-derived | open |
| L0.c4 | **Network** | streets, paths, bridges, parking areas as graph | Overture transportation (OSM-derived, ODbL) | open |
| L0.c5 | **Buildings** | footprints, height/floors, use | Overture buildings (OSM + Microsoft ML + others) | open; completeness to be measured |
| L0.c6 | **Land cover** | 10 m classes, tree cover, imperviousness | ESA WorldCover 2021 (AWS), Copernicus HRL | WorldCover tile N42E018 located |
| L0.c7 | **Population grid** | residents per cell | GHS-POP / WorldPop / Kontur | open |
| L0.c8 | **Places** | POIs, public buildings, heritage points | Overture places + OSM + Wikidata | open |

**L0 acceptance test** (the same for every city): boundary closes; DEM covers boundary + 5 km
buffer (horizon shading needs the hills); ≥ 90 % of buildings visible on the latest imagery exist
as footprints (sampled, manually, 200 random points); network graph is one connected component
for driving; population grid total within ±10 % of the official estimate.

### 3.2 Layer 1 — thematic bases (mostly from the City)

Georeferenced plans (PDF → GeoTIFF + digitised zones), cadastre parcels, register of public
buildings (area, year, heating, consumption), heritage register and protection zones, parking
zones and capacities, green inventory (trees, parks), utilities (water network — sensitive, kept
local), bus lines and stops, public lighting.

### 3.3 Layer 2 — periodic observations

Sentinel-2 (NDVI, 10 m, every ~5 days), Landsat 8/9 surface temperature (100 m native TIR, 30 m
delivered, 16 days), ECOSTRESS (70 m, irregular times of day), population estimates, monthly
tourist nights, energy consumption of public buildings, traffic counts, fire and flood events.

### 3.4 Layer 3 — live senses

Weather (national hydromet + citizen sensors), river level and dam releases (HET — to be
requested), parking occupancy (Parking servis payment data), citizen reports, air quality.
Rule: a live value is shown only when a device was really read, with its own time.

## 4. The algorithm system

### 4.1 Common contract

Every algorithm is a small, pure, documented unit:

```
algorithm:
  id: solar.rooftop.v1
  question: "Where do we put solar panels first?"
  inputs:  [L0.buildings@v, L0.terrain@v, L2.irradiance@v, L1.public_buildings@v?]
  params:  {panel_efficiency: 0.20, performance_ratio: 0.80, usable_roof_share: 0.6, ...}
  outputs: [L4.solar_potential@v+1]          # per building + per grid cell
  evidence_state: Estimated
  valid_scale: building (screening), not engineering design
  assumptions: [...]
  validation: [compare with PVGIS point values; compare with 3 real installations]
  runtime: minutes on a laptop
```

The **build graph** links them. A **scenario** is a set of patches
(e.g. *add 400 trees at these points*, *close this street to cars*, *insert this building*); the
graph reruns only what depends on patched layers and writes a **delta** (scenario − baseline).
The **decision layer** ranks options with transparent weights set by the City (multi-criteria
analysis), and every ranking is saved with its inputs to a decision log.

```
 question ─▶ indicators ─▶ algorithms (DAG) ─▶ baseline
                              ▲                    │
 intervention ─▶ layer patch ─┘                    ▼
                                    scenario ─▶ delta ─▶ ranking ─▶ decision log
```

### 4.2 The algorithms, per theme

Each is listed as **v0 (open data, days)** → **v1 (City data, weeks)** → **v2 (full model, months)**.

**A1 · Solar potential** — *"Where first? How much energy?"*
- v0: footprint × usable roof share × annual irradiance (PVGIS/Global Solar Atlas) × horizon
  loss from DEM (hills around Trebinje matter) → kWh/yr, kWp, simple payback, CO₂ avoided;
  ranked list of public buildings.
- v1: roof type and orientation from orthophoto; consumption of each public building → self-
  consumption share; subsidy rules.
- v2: LoD2 roofs (LiDAR or photogrammetry) + GRASS `r.sun` with neighbour shading, per roof face.

**A2 · Heat** — *"Where is it hottest, and where would trees help most?"*
- v0: summer Landsat LST composite (2019–2026, clear days) → relative hot spots; heat
  vulnerability = exposure (LST) × sensitivity (population, elderly share when available) ×
  lack of adaptive capacity (canopy, water, shade).
- v1: local calibration with in-situ measurements (a mobile measurement walk on a hot day is
  cheap and convincing); statistical ΔLST per +10 % canopy fitted locally — always labelled
  *Estimated*.
- v2: UMEP/SOLWEIG mean radiant temperature at street level for the centre; scenario "trees here".

**A3 · Green space and quality of life** — *"Where is greenery missing?"*
- v0: NDVI / tree cover per block; **3-30-300** per building (3 trees in view ≈ canopy within
  15 m, 30 % canopy in the neighbourhood, a park ≥ 0.5 ha within 300 m walking on the network).
- v1: green inventory from the City; candidate planting sites = hot ∧ low canopy ∧ walked ∧
  physically possible (sidewalk width, utilities).
- v2: green corridor optimisation (connectivity graph between parks and the river).

**A4 · Traffic and parking** — *"Where do we need parking? What if we change this street?"*
- v0: street graph → network centrality (proxy for through-traffic), walking catchments of
  parking areas; demand proxy = floor area by use × trip rates, with a summer tourism multiplier;
  supply = mapped parking; deficit per 5-minute walking catchment.
- v1: Parking servis occupancy/payment data by zone and hour; road counts; accident points →
  calibrated demand; pedestrian-zone scenario as closing edges and re-routing.
- v2: SUMO microsimulation of the centre (both bridges, the ring around the old town) for
  concrete regime changes; seasonal peaks.

**A5 · Tourism flows** — *"Where should tourist facilities, paths and parking go?"*
- v0: attractions (Old town / Kastel, Arslanagić bridge, Hercegovačka Gračanica, Tvrdoš
  monastery, Trebišnjica banks, Ćiro trail, wineries) and arrival points (bus station, parking,
  hotels) → gravity model + shortest walking paths → expected corridors; gaps in shade, benches,
  signage along them.
- v1: monthly tourist nights (and the e-Turizam registration data) → seasonal weights;
  counters at 2–3 points to calibrate.
- v2: agent-based day-trip model (Dubrovnik and Montenegro coast day visitors are a distinct
  population).

**A6 · Water and the Trebišnjica** — *"How do we plan the riverbank safely?"*
- v0: HAND (height above nearest drainage) from DEM → flood susceptibility (screening only);
  riverbank access and continuity of the riverside path; JRC flood hazard where it exists.
- v1: HET release regimes and river levels; historical flood events; karst behaviour of Popovo
  polje (literature + Vode Srpske).
- v2: HEC-RAS 2D or ANUGA with surveyed cross-sections for the urban reach; release scenarios.

**A7 · Public buildings and energy retrofit** — *"Which building first?"*
- v0: public buildings from OSM/Overture + footprint area + estimated age → rough energy use
  intensity by typology (TABULA/EPISCOPE-style archetypes) → screening.
- v1: the City's register and bills (UNDP energy management system data) → EUI benchmark,
  savings potential, cost, CO₂, solar synergy (A1) → priority list.
- v2: urban building energy model (City Energy Analyst) for the portfolio.

**A8 · New development impact** — *"What does this building do to its surroundings?"*
- v0: massing box inserted into the model → shadow hours on neighbours (sun path for the
  latitude), view from protected viewpoints (Kastel, Gračanica hill, the bridge), added floor area
  → parking and trip demand (A4), lost green (A3).
- v1: plan rules (height, coverage) checked automatically against the regulation plan.
- v2: 3D Tiles scene with LoD2 surroundings; comparison of design alternatives side by side.

**A9 · Cultural heritage** — *"How does development respect the identity of the city?"*
- v0: register of national monuments as points/polygons; protected views and visual corridors;
  risk overlay (heat, flood, traffic vibration proxy).
- v1: protection zones from the heritage authority; condition records.
- v2: photogrammetric models / HBIM of key objects (Old town walls, the bridge).

**A10 · Emergencies** — *"Who is exposed, and how do we get there?"*
- v0: isochrones from fire station and health centre; wildfire exposure (fuel from land cover ×
  slope × distance to settlement edge); settlements reached by a single road or single bridge
  (graph redundancy); population exposed (grid).
- v1: fire brigade interventions (history) and the City's risk assessment → calibrated maps.
- v2: evacuation routing scenarios.

**A11 · Citizen participation** — *"What do residents actually need?"*
- v0: simple map form (missing tree, light, bench, parking, unsafe crossing).
- v1: reports clustered and joined with model layers (a reported "missing shade" in a modelled
  hot spot rises in priority); feedback to the reporter.
- v2: participatory scenario voting (Decidim-style) on concrete interventions.

**X · Cross-cutting engines**
- *Scenario engine* (patches, rerun, delta), *ranking engine* (MCDA with explicit weights),
  *evidence engine* (states, provenance, licence), *explain engine* (every map cell can say how
  its value was made), and later a *language face*: a local model that turns a question into a
  query over the graph and answers with the map (the Pazarac pattern).

## 5. Physical layout of the repository

```
citytwin/
  README.md  ARCHITECTURE.md  PHASES.md  LOG.md  KNOWLEDGE.md  RECNIK.jsonl  svemir_kit.json
  core/                 city-agnostic code (no city names)
    fetch/              source adapters (one file per source, each with its permission record)
    build/              L0/L1 builders
    algorithms/         A1…A11, one folder each, with contract + tests
    scenario/           patches, graph, deltas
  cities/
    trebinje/
      city.json         bbox, CRS, boundary source, questions, weights
      registry/         sources.jsonl (permission ledger), requests.md (what we asked the City)
      data/             raw/ (immutable) · work/ · layers/ (versioned outputs)   ← not in git
      notes/            local knowledge
  research/             literature and product landscape, data catalogues
  faces/                web map (MapLibre / deck.gl; CesiumJS for 3D)
  docs/                 presentation material, figures
```

## 6. Technology choice (lean, open, laptop-first)

| Need | Choice | Why |
|---|---|---|
| Storage | GeoPackage + GeoParquet files; PostGIS when multi-user | files first = zero ops, portable to the City |
| Processing | Python (GDAL, DuckDB spatial, rasterio) | proven, reproducible |
| Network analysis | OSMnx / r5py | walking/driving catchments |
| Solar | PVGIS data + DEM horizon; GRASS `r.sun` in v2 | EU reference, free |
| Heat | Landsat C2 L2 ST; UMEP/SOLWEIG in v2 | standard method |
| Traffic | SUMO in v2 | open, mature |
| Flood | HEC-RAS / ANUGA in v2 | free, accepted |
| Participation | own light form in v0; Decidim if the City wants a platform | |
| Web face | MapLibre GL + deck.gl (2D/2.5D), CesiumJS / 3D Tiles (3D) | open, mobile-friendly |
| Standards | CityJSON/CityGML 3.0, OGC API, ISO/IEC 30173 terms | EU LDT Toolbox alignment |

## 7. What the model will never pretend

- It does not predict traffic from centrality alone; v0 traffic maps are labelled *proxy*.
- It does not compute heat in °C of air from satellites; LST is surface temperature.
- Solar v0 is screening, not a design for installation.
- Flood v0 is susceptibility, not a hazard map with return periods.
- No person-level data; residents appear only as grid counts.
