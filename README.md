# CityTwin — Digital Trebinje

**A decision model for a city: "what happens if we do this?"**
Pilot city: Trebinje (Republika Srpska, Bosnia and Herzegovina). The core is city-agnostic — any city is a folder of configuration.

**Live preview:** https://3esign.github.io/citytwin/ (Serbian Cyrillic by default, Latin toggle; every model value is marked as an estimate)

## Authors

- **doc. dr Semir Poturak** — Faculty of Construction Management, University "Union – Nikola Tesla"
- **prof. dr Darinka Golubović Matić** — Faculty of Construction Management, University "Union – Nikola Tesla"

Contact: **poturaksemir@gmail.com**

Built with Svemir, the authors' local AI workbench (named contributor, not an author); code and texts were drafted with Claude (Anthropic) and reviewed by the authors.

## What it is

Cities already hold data on buildings, streets, traffic, greenery, energy, water, tourism and population, but look at them separately. CityTwin connects them step by step into one model, starting from two or three questions the city cares about most, and shows the likely consequences of a decision before it is made.

It is not a 3D picture. The product is the answer to a question, with its evidence.

| Question (pilot) | Algorithm | Status |
|---|---|---|
| Where do we put solar panels first? | A1 rooftop solar screening (terrain horizon + Global Solar Atlas) | v0 |
| Where do we plant new trees? | A2/A3 summer surface heat × lack of greenery × built density | v0 |
| Where do visitors walk? | A5 shortest-path corridors between checked attractions and parking | v0 |
| Where do we need parking? | A4 walking minutes from every building to mapped parking | v0 |
| Traffic regime changes, public-building retrofit, development impact, river, heritage, emergencies, citizen reports | A4–A11 | planned (see `PHASES.md`) |

## How it works

`ARCHITECTURE.md` describes the full design. In short:

```
L6 faces      map 2D/3D · question box · citizen map · reports
L5 decisions  scenario patches · transparent multi-criteria ranking · decision log
L4 algorithms solar · heat · green · mobility/parking · tourism · water · energy · impact · heritage · emergency
L3 live       weather · river · parking occupancy · citizen reports
L2 periodic   satellite composites · statistics · tourism nights · energy bills
L1 city data  plans · cadastre · public-building register · heritage zones · parking zones
L0 ground     permission ledger · reference frame · terrain, water, streets, buildings, land cover, population
```

Rules: question first; **legal ground zero** (every source is checked for licence and robots.txt before collection; refusals are recorded, never circumvented — `cities/trebinje/registry/sources.jsonl`); five evidence states (Observed, Untimed, Estimated, Forecast, Unavailable); city-agnostic core; honest resolution.

## Coordinate reference systems

Computation and delivery in **ETRS89 / UTM 34N (EPSG:25834)**, the reference system of Republika Srpska. Exports are also produced in the legacy state system **MGI 1901 / Balkans zone 6 (EPSG:8678, formerly 3908)** using the EPSG operation for Bosnia and Herzegovina (~1 m); PROJ otherwise may pick the Croatian parameter set. Cadastral-grade work needs the official RUGIPP transformation.

## Data and licences

| Source | Use | Licence |
|---|---|---|
| Overture Maps (includes OpenStreetMap) | buildings, streets, water, land use, places | ODbL-1.0 / CDLA-Permissive-2.0 — © OpenStreetMap contributors, Overture Maps Foundation |
| Copernicus DEM GLO-30 | terrain, horizon | © DLR e.V. 2010–2014 and © Airbus Defence and Space GmbH 2014–2018, provided under COPERNICUS by the EU and ESA |
| ESA WorldCover 2021 | land cover | CC-BY-4.0 |
| Global Solar Atlas v2 | irradiance | CC-BY-4.0, © World Bank Group, data Solargis |
| Landsat 8/9 C2 L2, Sentinel-2 L2A (via Microsoft Planetary Computer) | surface temperature, NDVI | USGS public domain; Copernicus Sentinel data |
| JRC GHSL R2023A | population, building height, built surface | CC-BY-4.0 |

Refused by robots.txt and therefore not used: Overpass API, Geofabrik, planet.openstreetmap.org, BBBike, PVGIS.

The layers published under `docs/layers/` are derived from OpenStreetMap data and are released under the **ODbL-1.0**. Code is released under the **MIT License** (`LICENSE`).

## What the model does not know yet

- Building heights are known for <1 % of buildings; the rest are 100 m grid estimates.
- In 213 cells satellites see more built surface than mapped buildings — to be checked.
- Neighbour and tree shading on roofs, real parking occupancy, pedestrian counts, energy use of public buildings, river release regimes.

## Run it

Windows:

```
powershell -ExecutionPolicy Bypass -File tools\bootstrap.ps1
powershell -File tools\run.ps1 core\fetch\overture.py trebinje
powershell -File tools\run.ps1 core\fetch\raster_tiles.py trebinje
powershell -File tools\run.ps1 core\fetch\solar_atlas.py trebinje
powershell -File tools\run.ps1 core\fetch\ghsl.py trebinje
powershell -File tools\run.ps1 core\fetch\planetary.py trebinje both
powershell -File tools\run.ps1 core\build\l0_report.py trebinje
powershell -File tools\run.ps1 core\build\l0_quality.py trebinje
powershell -File tools\run.ps1 core\algorithms\a1_solar\solar_v0.py trebinje
powershell -File tools\run.ps1 core\algorithms\a2_heat\heat_v0.py trebinje
powershell -File tools\run.ps1 core\algorithms\a5_walk\walk_v0.py trebinje
node faces\serve.js trebinje 4870
```

Data are written to `cities/<id>/data/` (not in git) with a manifest of source, sha256 and evidence state.

## Status

Phase 0 ("the city in a day", open data only) is complete. Phase 1 is a pilot with the City on two or three chosen questions. See `PHASES.md` for the plan and the list of data requested from the City.
