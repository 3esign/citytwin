# Urban Digital Twin Landscape for a Small City — Pilot: Trebinje (BiH / Republika Srpska)

*Research date: 2026-09-17. Scope: open-source stacks, analytical engines, commercial products, literature, standards, funding.*

**Legend.** `[verified]` = checked on the cited page during this research. `[unverified]` = from background knowledge or search snippets only; check before relying on it.
**Note on release dates.** The page-reading tool sometimes gave the wrong **year** for GitHub release dates. For example, it dated pvlib v0.15.2 and deck.gl v9.4 to 2024, but those version numbers are newer than that. Version numbers are reliable. Where a year looked doubtful, it is marked `[date unverified]`.

---

## 0. Bottom line for Trebinje

A city of about 30k people does not need an "urban operating system". It needs:
1. **A 3D base model.** Build it from LiDAR or photogrammetry if RGURS/the city have it; otherwise use OSM/Overture footprints plus heights. Serve it as **3D Tiles** in **CesiumJS** or **VC Map**.
2. **A spatial database and API.** Use **PostGIS**, with **pygeoapi** or **GeoServer** on top for OGC APIs. Keep **DuckDB spatial** for fast offline analysis.
3. **Four to six "what-if" analysis layers**, computed offline and published as tiles or GeoJSON:
   - solar rooftop potential (PVGIS + pvlib / GRASS r.sun)
   - heat and green space (Sentinel-2 NDVI, Landsat LST, UMEP/SOLWEIG, 3-30-300)
   - flooding on the Trebišnjica (HEC-RAS / LISFLOOD-FP)
   - tourist and pedestrian access and parking (OSMnx / r5py, SUMO for the old-town core)
   - building energy (City Energy Analyst)
4. **A citizen participation layer**: Decidim, or a simple map-based feedback form.
5. **Alignment with EU standards and practice**: CityGML 3.0 / CityJSON, OGC APIs, NGSI-LD if IoT data is added later, and the EU LDT Toolbox / LDT CitiVERSE EDIC. This improves eligibility for Interreg HR-BA-ME, IPA ADRION, Digital Europe and Horizon Europe funding.

---

## 1. Open-source platforms and stacks

| Tool | URL | Licence | Maturity / latest | Fit for Trebinje |
|---|---|---|---|---|
| **CesiumJS** (+ 3D Tiles, OGC Community Std) | https://github.com/CesiumGS/cesium | Apache-2.0 | v1.143, 2026-07-01 [verified]; monthly releases | **Core 3D viewer**. Browser-based, handles terrain, buildings and point clouds. Cesium ion is optional; tiles can be self-hosted. |
| **VC Map** (virtualcitysystems, open-source core + UI) | https://github.com/virtualcitySYSTEMS/map-ui , map-core | MIT [verified] | release-v6.3 branch, 139 tags [verified]; commercial "VC Suite 2026" exists (https://vc.systems/en/vc-suite-release-2026/) | **Best ready-made 2D/3D/oblique twin UI.** Built on OpenLayers + Cesium, with a plugin system; used in DUET and in German cities. |
| **iTwin.js** (Bentley) | https://github.com/iTwin/itwinjs-core | MIT (library) [unverified licence text]; iModelHub/iTwin services are commercial | v5.11.1 [date unverified] | Strong for infrastructure/BIM. Too heavy and tied to Bentley cloud services for a lean pilot. |
| **Open Urban Platform / DIN SPEC 91357** | https://www.smart-city-berlin.de/en/projects-list/project-detail/din-spec-91357-reference-architecture-model-open-urban-platform-oup/ | Specification (DIN, paid document) | 2017 reference architecture; still cited | A reference architecture for layering the system and describing it in proposals. It is not software. |
| **Urban Data Space Platform** (German openCode) | https://opencode.de/en/software/urban-data-space-platform-4909 | Open source (EUPL/other per component) [unverified] | Listed in the EU OSS catalogue | Full German municipal platform (FIWARE-based). Useful as a reference; too heavy to deploy for 30k people. |
| **FIWARE Orion-LD** (NGSI-LD broker) + **Smart Data Models** | https://github.com/FIWARE/context.Orion-LD ; https://smartdatamodels.org | AGPL-3.0 (broker) [unverified]; data models CC-BY-4.0 [unverified] | Orion-LD 1.12.0, 2025-01-28 [verified] | Use **only when real-time IoT data arrives** (parking sensors, air quality). Smart Data Models are useful now as a schema vocabulary. NGSI-LD is ETSI standard GS CIM 009. |
| **Masterportal** (Hamburg Urban Data Platform) | https://bitbucket.org/geowerkstatt-hamburg/masterportal/ ; https://www.masterportal.org | MIT [unverified] | Active; "Masterportal Admin" config tool; Urban Data Platform conference 2026 (Connected Urban Twins) | Mature municipal 2D/3D geoportal, configured through JSON. A good alternative to VC Map. Documentation is mostly in German. |
| **OpenRemote** | https://github.com/openremote/openremote | AGPL-3.0 [unverified]; 1.9k stars [verified] | 1.30.0 [date unverified; requires Keycloak 26.x → likely 2025/26] | IoT and asset management with rules and maps. Good if the city manages lighting, parking or energy assets. |
| **3DCityDB v5** | https://github.com/3dcitydb/3dcitydb | Apache-2.0 [unverified] | v5.x, **full CityGML 3.0 support** [verified]; v5.1.3 [date unverified] | Standard PostGIS-based storage for CityGML/CityJSON. Its importer/exporter can produce 3D Tiles/glTF through helper tools. |
| **CityJSON** tools (cjio, cjval, ninja, 3dfier, geoflow/roofer) | https://www.cityjson.org ; https://github.com/cityjson | MIT / GPL mix [unverified] | CityJSON is an OGC Community Standard (https://docs.ogc.org/cs/20-072r5/20-072r5.html) [verified] | **The lightweight path to LoD1.2/LoD2 buildings.** Use `roofer`/`geoflow` (3D BAG) when LiDAR exists, or `3dfier` to extrude from footprints. |
| **OSM Buildings** | https://osmbuildings.org ; https://github.com/OSMBuildings | BSD-2 (lib) [unverified] | Low activity [unverified] | Quick 2.5D demo only. |
| **MapLibre GL JS** | https://github.com/maplibre/maplibre-gl-js | BSD-3 [unverified] | v6.0.0 pre-release series [date unverified] | **2D/2.5D base map** with vector tiles, terrain and fill-extrusion. Lighter than Cesium, good for mobile. |
| **deck.gl** | https://github.com/visgl/deck.gl | MIT [unverified] | v9.4.0, WebGPU across all layers [verified version; date unverified] | Analytical overlays (heatmaps, flows, trips animation) on MapLibre. Also renders 3D Tiles. |
| **kepler.gl** | https://github.com/keplergl/kepler.gl | MIT [unverified] | Active [unverified] | Zero-code exploratory analysis for staff and for demos. |
| **pygeoapi** (OGC API reference implementation) | https://github.com/geopython/pygeoapi | MIT [verified] | 0.23.x [verified; date unverified] | **Light OGC API – Features/Processes server.** Processes can wrap our analysis scripts. |
| **GeoServer** | https://geoserver.org | GPL-2.0 | 2.2x/3.0, active [unverified] | Heavier and Java-based, but the standard for WMS/WFS/WMTS. Choose GeoServer or pygeoapi, not both. |
| **PostGIS** | https://postgis.net | GPL-2.0 | 3.5/3.6 [unverified] | **System of record.** |
| **DuckDB spatial** | https://duckdb.org/docs/extensions/spatial | MIT | Active [unverified] | Queries Overture GeoParquet directly. Very fast offline ETL; no server needed. |
| **QGIS** | https://qgis.org | GPL-2.0+ | 3.40 LTR / 3.4x [unverified] | Desktop tool for staff. Hosts the UMEP, GRASS and SAGA plugins. |
| **Overture Maps** | https://docs.overturemaps.org | Buildings/Transportation/Base: **ODbL**; Places: **CDLA-Permissive-2.0**; Addresses: per source [verified] | Monthly releases; attribution docs updated 2026-05-15 [verified] | Global building footprints (OSM + Microsoft/Google ML), sometimes with heights. **Check Trebinje coverage.** |
| **Digital Twin Hub / UK "Gemini Principles"** | https://digitaltwinhub.co.uk | Guidance (free) | Community hub; CDBB legacy [unverified] | Governance principles, e.g. the "Gemini Principles" used to evaluate the Herrenberg twin. |
| **EU LDT Toolbox** | https://ldtcitiverse-edic.eu/eu-ldt-toolbox-launch-box/ | Open source, "standards-based" [verified]; per-component licences not listed | **Launched 16–17 June 2026, Valencia** [verified]; now run by the LDT CitiVERSE EDIC | **Align with this.** Reusing its components improves EU fundability. It is unclear whether non-EU cities can deploy it [unverified]. |
| **TwinCity3d** | https://www.twincity3d.com | "Open source" per site title [unverified — page not reachable] | Unknown | Watch-list only. |

---

## 2. Analytical engines by theme

### 2.1 Solar rooftop potential
| Tool | URL | Licence / maturity | Fit |
|---|---|---|---|
| **EU PVGIS 5.3 API** (JRC) | https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/getting-started-pvgis/api-non-interactive-service_en | Free public API; PVGIS 5.3 current [verified exists] | **Covers the Balkans** (SARAH-3/ERA5 [unverified dataset]). Gives yield per kWp by tilt and azimuth; combine with roof geometry. |
| **pvlib-python** | https://github.com/pvlib/pvlib-python | BSD-3 [unverified]; v0.15.2 [verified version] | Energy model per roof plane; has a built-in PVGIS client (`pvlib.iotools.pvgis`). |
| **GRASS r.sun / r.horizon** | https://grass.osgeo.org | GPL-2.0+; GRASS 8.4 [unverified] | Raster irradiance on a DSM, including terrain shading. Important in Trebinje's valley. |
| **SAGA GIS** (Potential Incoming Solar Radiation) | https://saga-gis.sourceforge.io | GPL-2.0 | Alternative to r.sun. |
| **UMEP SEBE** (solar energy on building envelopes) | https://umep-docs.readthedocs.io | GPL [unverified] | Roof and wall irradiance from a DSM in QGIS. |
| **Google Solar API** | https://developers.google.com/maps/documentation/solar/coverage | Commercial, per-request pricing | Coverage is only available as a map/GeoJSON; the page text gives no per-country list. **BiH coverage: [unverified — likely none or only "BASE"/experimental expanded coverage](https://developers.google.com/maps/documentation/solar/expanded-coverage).** Do not plan on it. |

Method: LiDAR DSM (or LoD2) → roof planes (slope, aspect, area) → r.sun/SEBE shading factor × PVGIS yield → kWh/year, CO₂ and payback per building. This is the fastest high-value demo.

### 2.2 Traffic, parking, accessibility
| Tool | URL | Licence / maturity | Fit |
|---|---|---|---|
| **Eclipse SUMO** | https://projects.eclipse.org/projects/automotive.sumo | EPL-2.0 / GPL-2.0+; **v1.27.1, 2026-06-25** [verified] | Microsimulation of the old-town core, bridges and parking search; scenarios such as closures and one-way streets. |
| **MATSim** | https://matsim.org | GPL-2.0 [unverified] | Agent-based, whole-day demand. Overkill for 30k people unless research partners use it. |
| **UrbanSim** | https://github.com/UDST/urbansim | BSD-3 [unverified]; commercial cloud by UrbanSim Inc. | Land-use/real-estate model; data-hungry. Not for the pilot. |
| **A/B Street** | https://github.com/a-b-street/abstreet | Apache-2.0 [verified]; **since 2025 split into specialised tools** (Network Planning Workspace, LTN tool) [verified] | The LTN tool is good for citizen-facing "low-traffic neighbourhood" demos. |
| **r5py / R5** | https://github.com/r5py/r5py | MIT (r5py) / R5 licence [unverified]; v1.1.x [verified version] | Multimodal travel-time matrices (walk, bike, GTFS). Useful for 15-minute-city and school/health access analysis. |
| **OSMnx** | https://github.com/gboeing/osmnx | MIT [unverified]; v2.x on PyPI [unverified] | Street network from OSM, centrality, isochrones. **Essential and cheap.** |
| **AequilibraE** | https://www.aequilibrae.com | Custom permissive (MIT-like) [unverified] | Macro assignment as a QGIS plugin. Good for a municipal traffic model if count data exists. |

### 2.3 Pedestrian and tourist flows
- **Data sources**: anonymised mobile-operator data (m:tel / BH Telecom [unverified availability]), Wi-Fi counters, Google Popular Times (ToS limits), manual counts, Strava Metro (free for cities [unverified]).
- **Tools**: SUMO pedestrian model, **JuPedSim** (https://www.jupedsim.org, LGPL [unverified]) for crowd dynamics around the Old Town (Stari grad), Platani square and Arslanagić bridge, OSMnx/r5py for walk access, and deck.gl TripsLayer for visualisation.

### 2.4 Urban heat island and outdoor thermal comfort
| Tool | URL | Notes |
|---|---|---|
| **UMEP / SOLWEIG** (QGIS "UMEP for processing") | https://plugins.qgis.org/plugins/processing_umep/ ; https://zenodo.org/records/15309384 | **SOLWEIG v2025** is part of UMEP-processing [verified]. A Rust port exists (https://github.com/UMEP-dev/solweig) [verified]. Computes mean radiant temperature (Tmrt) and UTCI heat-stress maps from a DSM plus trees. **Top pick.** |
| **Landsat 8/9 TIRS LST** (single-channel / split-window), **Sentinel-3 SLSTR**, **ECOSTRESS** | USGS / Copernicus | Free. 100 m (Landsat) is adequate for a 30k city. Use Google Earth Engine or openEO (Copernicus Data Space). |
| **ENVI-met** | https://www.envi-met.com | Commercial. Micro-scale CFD for street design. Use only for specific projects. |
| **WRF-urban (BEP/BEM, SLUCM)** | https://www.mmm.ucar.edu/models/wrf | Public domain. A research tool; needs HPC. Partner with the University of East Sarajevo or Banja Luka [unverified capacity]. |

### 2.5 Green space access and greening
- **3-30-300 rule** (Konijnendijk 2023, *J. Forestry Research* 34:821–830, doi:10.1007/s11676-022-01523-z [DOI from link, verified URL]). Measurement method: Browning et al. 2024, *Sci. Total Environ.*, "Measuring the 3-30-300 rule…" (https://pubmed.ncbi.nlm.nih.gov/37832672/) [verified title]. European city assessment: https://pmc.ncbi.nlm.nih.gov/articles/PMC13223244/ [verified exists].
- **Inputs**: Sentinel-2 NDVI (10 m), tree canopy (ESA WorldCover 10 m, Meta/WRI 1 m canopy height [unverified licence]), OSM parks → OSMnx 300 m network distance to parks larger than 1 ha.

### 2.6 Flood and river modelling (Trebišnjica, karst, HPP Gorica/Trebinje dams)
| Tool | URL | Licence | Fit |
|---|---|---|---|
| **HEC-RAS 6.x (2D)** | https://www.hec.usace.army.mil/software/hec-ras/ | Free (US gov), closed source | Industry standard; local hydrologists know it. |
| **LISFLOOD-FP** | https://www.seamlesswave.com/LISFLOOD8.0 | BSD-3 [unverified] | Fast 2D, GPU-capable. |
| **ANUGA** | https://github.com/anuga-community/anuga_core | Apache-2.0 [unverified] | Python 2D shallow water. Good for scripted what-if runs. |
| **Copernicus EMS / GloFAS / JRC flood hazard maps** | https://data.jrc.ec.europa.eu/collection/id-0054 | Free | Pan-European 100 m hazard layer; screening only. |
| **ThinkHazard (GFDRR)** | https://thinkhazard.org | Free | Screening. |

Trebinje-specific notes: the river flow is regulated by the HET (Hidroelektrane na Trebišnjici) dams, so dam-release scenarios are the key what-if. No public flood hazard map for Trebinje was found [unverified; ask HET or the RS water agency "Vode Srpske"].

### 2.7 Building energy (UBEM)
| Tool | URL | Licence / maturity | Fit |
|---|---|---|---|
| **City Energy Analyst (CEA)** | https://github.com/architecture-building-systems/CityEnergyAnalyst | MIT [unverified]; v4.0.0 beta series [verified version; date unverified] | **Best all-in-one**: demand, solar, district networks, GUI. Takes OSM footprints directly. |
| **EnergyPlus** (+ URBANopt) | https://energyplus.net ; https://docs.urbanopt.net | BSD-3 | Engine behind many UBEM tools; URBANopt (NREL) handles district scale. |
| **TEASER** (RWTH) | https://github.com/RWTH-EBC/TEASER | MIT [unverified] | Archetype generator for Modelica; German typologies. |
| **SimStock** (UCL) | https://github.com/UCL/simstock [unverified URL] | [unverified] | EnergyPlus UBEM for UK stock. |
| **CityBES** (LBNL) | https://citybes.lbl.gov | Free web tool [unverified status] | US-oriented, largely dormant [unverified]. |
| **TABULA/EPISCOPE typologies** | https://episcope.eu | Free | BiH/Serbia typologies exist through national studies [unverified]. Needed for archetypes. |

### 2.8 Wildfire risk (relevant: Mediterranean karst and eastern Herzegovina fires)
- **EFFIS** (European Forest Fire Information System, covers the Western Balkans): https://effis.jrc.ec.europa.eu — FWI forecasts and burnt areas.
- **FlamMap / FARSITE** (free, US Forest Service), **Cell2Fire**, **ForeFire** (open, [unverified licence]).
- Wildland–urban interface mapping: combine a WorldCover fuel proxy, slope and buildings.

### 2.9 What-if and scenario planning tools
| Tool | Type | URL | Notes |
|---|---|---|---|
| **MIT CityScope** | OSS (MIT/GPL mix [unverified]) | https://github.com/CityScope | Tangible and web scenario tables; well suited to workshops. |
| **UrbanFootprint** | Commercial SaaS (US) | https://urbanfootprint.com | US data only. Not suitable. |
| **Esri ArcGIS Urban** | Commercial | https://www.esri.com/en-us/arcgis/products/arcgis-urban/buy | Included only in **ArcGIS Online "Professional Plus" user type** [verified]; price via sales. |
| **Esri CityEngine** | Commercial | https://www.esri.com/cityengine | Procedural 3D modelling (CGA). |
| **Autodesk InfraWorks / Forma** | Commercial | https://www.autodesk.com/products/forma | Forma: early-stage site analysis (sun, wind, noise). |
| **Aino** | Commercial SaaS with AI | https://www.aino.world/pricing | **Pro $50/mo, Teams $300/mo (annual), Enterprise custom** [verified]. Cheap for quick demos. |
| **Giraffe** | Commercial SaaS | https://www.giraffe.build | Browser-based feasibility/massing tool [unverified pricing]. |
| **TestFit** | Commercial | https://www.testfit.io | Site-yield tool for developers; limited municipal fit. |
| **Cityzenith SmartWorldPro2** | Commercial | https://tracxn.com/d/companies/cityzenith/ | Company status uncertain [unverified]. Avoid. |

### 2.10 Citizen participation
| Tool | URL | Licence / maturity | Fit |
|---|---|---|---|
| **Decidim** | https://github.com/decidim/decidim | **AGPL-3.0**, **v0.32.1, 2026-07-30** [verified] | Participatory budgeting, proposals, meetings; used by Barcelona, Helsinki, etc. Needs Ruby hosting. |
| **CONSUL Democracy** | https://github.com/consuldemocracy/consuldemocracy | AGPL-3.0 [unverified version] | Similar; used in Madrid and in Latin America. |
| **FixMyStreet (mySociety)** | https://github.com/mysociety/fixmystreet | AGPL-3.0 [unverified] | Issue reporting on a map. |
| **Maptionnaire** | https://maptionnaire.com | Commercial (Finland) | Map-based surveys; the best fit for planning consultation. |
| **Go Vocal (ex-CitizenLab)** | https://www.govocal.com | Commercial SaaS; core code AGPL [unverified] | Proposals and surveys. |
| **UNDP BiH eCitizen app** | https://www.undp.org/bosnia-herzegovina/news/digital-transformation-18-local-governments-bih | Swiss-funded MEG project, 18 LGs (2020) [verified]; **Trebinje not listed** [verified] | A local precedent; possible to reuse. |

### 2.11 Heritage (HBIM)
- Stari grad (Kastel), Arslanagić bridge, Tvrdoš and Hercegovačka Gračanica monasteries.
- **Workflow**: TLS/UAV photogrammetry (Agisoft Metashape, or open-source **OpenDroneMap** https://opendronemap.org, AGPL) → point cloud → **Potree** web viewer or Cesium 3D Tiles → HBIM in Revit/ArchiCAD (commercial) or **BlenderBIM/Bonsai + IfcOpenShell** (LGPL, open) → CityGML 3.0 / IFC link.
- **Closest analogue**: Blagonić, Markovinović, Matijević, Redovniković (2025), "Integration of Digital Twin Technologies in Urban Regeneration of a Small Historic Town in Europe", *Sustainability* 17(23):10740, doi:10.3390/su172310740 [verified]. It covers Draguć, Istria (HR) using UAV, TLS, GNSS, Metashape and QGIS/PostGIS.

---

## 3. Commercial products municipalities buy

| Vendor / product | URL | Pricing (public?) | Notes |
|---|---|---|---|
| **Esri ArcGIS Urban** (+ Online/Enterprise, CityEngine) | https://www.esri.com/en-us/arcgis/products/arcgis-urban/buy | Requires the **Professional Plus** user type [verified]; price not public. Professional Plus reportedly ~US$4k–5k per user/year [unverified]. Esri BiH distributor via GDi [unverified]. | Most common municipal choice; some RS agencies already use Esri [unverified]. |
| **Bentley iTwin / OpenCities Planner / OpenCities Map** | https://www.bentley.com/industry/cities-government/cities-municipalities | Enterprise quote | Strong for infrastructure and reality modelling (ContextCapture/iTwin Capture). |
| **Virtual City Systems VC Suite** | https://vc.systems/en/solutions/digital-twin/ | Quote; open-source VC Map core | German municipalities; DUET partner. |
| **Dassault 3DEXPERIENCE City / Virtual Singapore** | https://www.3ds.com | Enterprise, high (multi-M€ class for large cities) [unverified] | Out of scope. |
| **Siemens (Xcelerator / City Performance Tool)** | https://www.siemens.com | Enterprise | Out of scope. |
| **Aino** | https://www.aino.world/pricing | $50–300/mo; Enterprise custom [verified] | Low-cost AI planning analytics. |
| **51World (51WORLD, China)** | https://www.51aes.com [unverified URL] | Enterprise | Game-engine twins. Geopolitical and procurement considerations apply. |
| **Twinby** | — | Not found as a city-twin vendor [unverified] | Possibly confused with TwinUp (https://www.twinup.io/digital-smart-city/) or TwinCity (https://www.twincity.dev/en/). |
| **Cesium ion (SaaS)** | https://cesium.com/platform/cesium-ion/pricing/ | Community free tier (non-commercial); Commercial ~$149/mo+ [unverified] | Optional tiling pipeline. |
| **Geofoto (HR)** | — | Quote | Built the ZG3D Zagreb model [snippet]. A regional provider of LiDAR and 3D capture. |

---

## 4. Key literature and case studies (2019–2026)

### 4.1 Review and position papers
1. **Ketzler, B., Naserentin, V., Latino, F., Zangelidis, C., Thuvander, L., Logg, A. (2020).** Digital Twins for Cities: A State of the Art Review. *Built Environment* 46(4):547–573. doi:10.2148/benv.46.4.547 [DOI unverified; paper verified via Chalmers/Ingenta].
2. **Shahat, E., Hyun, C.T., Yeom, C. (2021).** City Digital Twin Potentials: A Review and Research Agenda. *Sustainability* 13(6):3386. doi:10.3390/su13063386 [verified via MDPI URL].
3. **Lehtola, V.V., Koeva, M., Oude Elberink, S., Raposo, P., Virtanen, J.-P., Vahdatikhaki, F., Borsci, S. (2022).** Digital twin of a city: Review of technology serving city needs. *Int. J. Applied Earth Observation and Geoinformation* 114:102915. doi:10.1016/j.jag.2022.102915 [paper verified; DOI from PII S1569843222001169].
4. **Weil, C., Bibri, S.E., Longchamp, R., Golay, F., Alahi, A. (2023).** Urban Digital Twin Challenges: A Systematic Review and Perspectives for Sustainable Smart Cities. *Sustainable Cities and Society* 99:104862. doi:10.1016/j.scs.2023.104862 [verified via ADS bibcode 2023SusCS..9904862W].
5. **Batty, M. (2018).** Digital twins. *Environment and Planning B* 45(5):817–820. doi:10.1177/2399808318796416 [unverified DOI].
6. **Batty, M. (2024).** Digital twins in city planning. *Nature Computational Science* 4(3):192–199. doi:10.1038/s43588-024-00606-7 [verified]. Key point: the twin is decision support with a human in the loop.
7. **Wu, T.G., Guan, C. (2025).** Advancing Intra and Inter-City Urban Digital Twins: An Updated Review. *J. Planning Education and Research*. doi:10.1177/0739456X241260887 [verified URL].
8. **Mazzetto, S. (2024).** A Review of Urban Digital Twins Integration, Challenges, and Future Directions in Smart City Development. *Sustainability* 16(19):8337. doi:10.3390/su16198337 [author unverified; URL verified].
9. **Dembski, F., Wössner, U., Letzgus, M., Ruddat, M., Yamu, C. (2020).** Urban Digital Twins for Smart Cities and Citizens: The Case Study of Herrenberg, Germany. *Sustainability* 12(6):2307. doi:10.3390/su12062307 [verified URL]. **The key small-city (~31k) precedent**, closest in size to Trebinje.
10. **Ruohomäki, T., Airaksinen, E., Huuska, P., Kesäniemi, O., Martikka, M., Suomisto, J. (2018/2021).** Smart City Platform Enabling Digital Twin (Helsinki) / *IET Smart Cities* "Urban development with dynamic digital twins in Helsinki city" doi:10.1049/smc2.12015 [verified URL; authors unverified].
11. **Blagonić et al. (2025)** — small historic town UDT (Draguć, HR), doi:10.3390/su172310740 [verified].
12. **Konijnendijk (2023)** 3-30-300 — see §2.5.
13. **Gemini/FAIR evaluation of Herrenberg (2023)** — https://www.researchgate.net/publication/369949953 [verified title].

### 4.2 City case studies
| City | Size | Takeaway | Source |
|---|---|---|---|
| **Herrenberg (DE)** | ~31k | HLRS-built VR twin: traffic, air flow, noise, citizen VR sessions; long-term planning with public feedback | https://www.mdpi.com/2071-1050/12/6/2307 ; https://www.hlrs.de/solutions/types-of-computing/visualization/city-planning-urban-digital-twins |
| **Helsinki / Kalasatama (FI)** | 680k | Open CityGML + mesh models as open data; energy and solar analysis | https://hri.fi/data/en/dataset/helsingin-3d-kaupunkimalli ; https://www.hel.fi/en/decision-making/information-on-helsinki/maps-and-geospatial-data/helsinki-3d |
| **Espoo (FI)** | 300k | [unverified details] | — |
| **Zurich (CH)** | 430k | Open 3D city model, noise/solar/wind, participatory 3D [unverified details] | https://www.stadt-zuerich.ch/digitaler-zwilling [unverified URL] |
| **Rotterdam (NL)** | 650k | Open Urban Platform; 3D model on Cesium [unverified details] | — |
| **Vienna (AT)** | 2M | "Digitaler Zwilling Wien", LiDAR-based city model [unverified] | — |
| **Tallinn (EE)** | 450k | Buildings-registry-based twin [unverified] | — |
| **Zagreb (HR)** | 770k | **ZG3D** city 3D model/"digital twin" used in spatial planning | https://www.gim-international.com/content/article/spatial-planning-in-the-city-of-zagreb ; https://www.researchgate.net/publication/386152599 ; https://senengroup.com/sustainability/digital-twin-zagreb-case-study/ |
| **Draguć (HR)** | small village | Historic-town UDT method | doi:10.3390/su172310740 |
| **Novi Sad (RS)** | 370k | University campus 3D city model (CityGML) — *ISPRS IJGI* 9(8):476 (2020), doi:10.3390/ijgi9080476 [verified URL] | https://www.mdpi.com/2220-9964/9/8/476 |
| **Ljubljana, Rijeka, Belgrade** | — | No substantive UDT publication found in this pass [unverified] | Paper on UDT for planning in an international context: https://hrcak.srce.hr/en/322675 |
| **Sarajevo (BiH)** | — | **First Western Balkans EU Climate-Neutral Cities Mission Label (16 Feb 2026)** [verified]; UNDP "Sarajevo Smart City Initiative" | https://netzerocities.eu/2026/02/16/... ; https://www.undp.org/bosnia-herzegovina/projects/smart-city-initiative |

### 4.3 EU initiatives
- **EU LDT Toolbox**:
  - Procurement: DIGITAL Europe WP 2021–22, tender closed 2023-10-02, Lot 1 dev + Lot 2 monitoring [verified]. https://digital-strategy.ec.europa.eu/en/funding/procurement-development-local-digital-twins-toolbox
  - **Launched June 2026 as European public infrastructure under the LDT CitiVERSE EDIC** [verified]. https://ldtcitiverse-edic.eu/
- **LDT4SSC** (Local Digital Twins for Smart and Sustainable Communities): €17M cascade funding, **up to €1M per consortium, 18 months**; Calls 1–3 closed (Call 3 deadline 2026-07-13) [verified]. Eligibility of BiH not stated [unverified]. https://ldt4ssc.eu/
- **DIGITAL-2024-CLOUD-DATA-AI-07-DIGITALTWIN**: €20M, deadline 2024-11-21, ≥85% cascade funding, SIMPL-aligned [verified]. https://www.ffg.at/sites/default/files/downloads/FFG_Infosheet_Call7_LDT_bf.pdf
- **Living-in.EU** (the cities' "EU way" declaration; LDT partnership): https://living-in.eu/partnerships/eu-local-digital-twin-ldt-toolbox
- **CitiVerse**: https://digital-strategy.ec.europa.eu/en/factpages/citiverse
- **DestinE (Destination Earth)**: climate and extremes twins; for downscaled climate inputs [general].
- **DUET (H2020 870697, 2019–2022)**: Flanders, Pilsen, Athens; VCS was a partner. https://cordis.europa.eu/project/id/870697 ; https://www.digitalurbantwins.com/
- **URBANAGE (H2020)**: age-friendly planning with twins; Leuven, Santander, Helsinki [unverified details].

### 4.4 Standards
| Standard | Status | Link |
|---|---|---|
| **ISO/IEC 30173:2023** Digital twin — Concepts and terminology | Published 2023 [verified] | https://www.iso.org/standard/81442.html |
| **OGC CityGML 3.0** Part 1 Conceptual Model (adopted 2021) and Part 2 GML Encoding (adopted later; 2023 [unverified year]) | [verified] | https://docs.ogc.org/is/20-010/20-010.html ; https://docs.ogc.org/is/21-006r2/21-006r2.html |
| **CityJSON** (OGC Community Standard, v2.0) | [verified CS doc] | https://docs.ogc.org/cs/20-072r5/20-072r5.html |
| **OGC 3D Tiles** (Community Standard), **OGC API – Features / Processes / Tiles / 3D GeoVolumes** | [general] | https://ogcapi.ogc.org |
| **ISO 37120** (city indicators; with **ISO 37122** smart and **ISO 37123** resilient) | Published (37120:2018) [unverified edition] | https://www.iso.org/standard/68498.html [unverified URL] |
| **DIN SPEC 91357** Open Urban Platform | 2017 | see §1 |
| **ETSI NGSI-LD (GS CIM 009)** | Current v1.8+ [unverified] | https://www.etsi.org |
| **INSPIRE** (BiH is aligning under EU acquis) | — | https://inspire.ec.europa.eu |
| **IFC 4.3 (ISO 16739-1:2024)** for BIM/HBIM | [unverified] | — |

---

## 5. Funding angles for Trebinje (2026–2027)

| Instrument | Status / facts | Fit and how |
|---|---|---|
| **Interreg VI-A IPA Croatia–Bosnia and Herzegovina–Montenegro** | €107M, 3 countries. Priorities: R&I, SMEs, energy efficiency, **climate adaptation**, circular economy, health, **tourism and culture**. **2nd call: 188 applications, 25 projects approved**; implementation workshops Aug 2026 [verified]. Trebinje is in the programme area [unverified — very likely, as a border city with Dubrovnik/Herceg Novi; confirm in the programme document]. | **Best fit.** Cross-border project with Dubrovnik and Herceg Novi: tourist flows, heat and wildfire, heritage twin. Watch for a 3rd call or strategic projects. Contact: js-hr-ba-me@mrrfeu.hr. https://interreg-hr-ba-me.eu/ |
| **Interreg IPA ADRION (Adriatic-Ionian)** | BiH is a partner state; 2nd call in 2025 [verified FAQ/EEAS] | Transnational: climate adaptation, smart and green tourism. https://www.eeas.europa.eu/delegations/bosnia-and-herzegovina/second-call-projects-under-interreg-ipa-adrion-2021-2027-program-has-been-opened_en |
| **Interreg IPA South Adriatic** | **Italy–Albania–Montenegro only; BiH is NOT eligible** [verified programme name] | Only through Montenegrin partners, if at all. |
| **Interreg Danube Region** / **Euro-MED** | BiH participates in Danube (partner state) [unverified for 2026 calls]. BiH is in the Euro-MED area as an IPA country [unverified]. | Danube: smart and resilient cities topics. Euro-MED: green-living areas, sustainable tourism (fits Trebinje). |
| **IPA III (bilateral BiH)** | **€140.5M in grants for 2025–2027 unlocked after ratification (EEAS, 2026-08-17)**: governance, green agenda, economic development; no explicit municipal digital line [verified]. The €373M Reform and Growth Facility is at risk [verified quote]. | Indirect: green agenda and public-service lines through state/entity institutions. IPA 2026–27 programming info: https://fmks.gov.ba/en/information-about-the-ipa-2026-and-2027-programme-for-bosnia-and-herzegovina/ ; DEI: https://www.dei.gov.ba/en/ipa-iii |
| **Horizon Europe** | BiH has been an **associated country** since 2022 [verified via JRIC meetings 2024, 2025]. Sarajevo received the Cities Mission Label [verified]. | Join consortia as a pilot city: Cluster 5/6, **Cities Mission** calls, and NetZeroCities "Twinning". Pair with the University of East Sarajevo / Banja Luka / Mostar [unverified contacts]. |
| **Digital Europe Programme** | **BiH associated; agreement in force retroactively from 2024-01-01**. Open strands named: AI, advanced digital skills, EDIHs [verified]. Whether LDT/data-space topics (SO2) are open to BiH is not confirmed [unverified]. | Check each call's eligibility. Partner with an EDIH in BiH. |
| **LDT4SSC / LDT CitiVERSE EDIC** | Cascade calls are closed [verified]; the EDIC is membership-based [verified] | Monitor for new calls; request observer status through Living-in.EU (open to non-EU signatories? [unverified]). |
| **UNDP BiH** | Smart City Initiative (Sarajevo); Digital Transformation in the Public Sector; eCitizen for 18 LGs (Swiss-funded, 2020) [verified]; IPC Trebinje innovation hub story [verified URL]; UNDP "Digital Twins for Cities" urban brief, July 2025 [verified URL] | **A direct local partner**; UNDP runs a coworking/innovation hub (IPC) in Trebinje. https://www.undp.org/bosnia-herzegovina/stories/ipc-trebinje-more-just-workspace-hub-ideas-and-vibrant-community ; https://www.undp.org/sites/g/files/zskgke326/files/2025-08/digital_twins_for_cities_urban_brief_july_2025.pdf |
| **GIZ** | Programmes on local governance/energy efficiency/digitalisation in BiH [unverified 2026 specifics] | Technical assistance; contact GIZ BiH. |
| **EBRD Green Cities** | BiH members: **Banja Luka, Sarajevo** [verified pages] | Trebinje would need an EBRD investment project (e.g. district heating, public lighting, water) to enter; a Green City Action Plan can include a data/twin baseline. https://ebrdgreencities.com/our-cities/cities/banja-luka |
| **World Bank** | **GIVE project (Geospatial Infrastructure and Valuation Enhancement), €23.1M, approved 2024-05-15, FBiH-focused** (SDI, building registers, valuation) [verified]; no RS component mentioned [verified]. Older Real Estate Registration Project covered both entities [verified doc] | Mostly benefits FBiH; RS equivalent via RGURS [unverified]. Relevant as a data source and precedent. https://www.worldbank.org/en/news/press-release/2024/05/15/bosnia-and-herzegovina-to-modernize-land-administration-with-world-bank-support |
| **Other** | Swiss (SDC) MEG successor, Sweden/Sida, EIB (via Mission Label), Green for Growth Fund [unverified] | — |

### Trebinje data sources to check first
- **RGURS geoportal** (RS Geodetic Authority): https://geoportal.rgurs.org/ — orthophoto, cadastre, e-Katastar. LiDAR/DTM availability and licence: **[unverified — ask RGURS]**.
- **City of Trebinje**: urban plans (PPGT/ urbanistički plan), address register, public lighting, and parking data.
- **HET (Hidroelektrane na Trebišnjici)**: dam releases and river gauges.
- **Copernicus**: Sentinel-1/2/3, Urban Atlas (Trebinje FUA not covered [unverified]), CLMS HR layers (imperviousness, tree cover), EU-DEM / Copernicus DEM GLO-30.
- **OSM / Overture**: footprints, POIs, roads.

---

## 6. Recommended lean stack ("demo in 6–8 weeks")

```
Data:   Overture/OSM + RGURS ortho/cadastre + (LiDAR|UAV via OpenDroneMap) + Sentinel/Landsat + PVGIS
ETL:    DuckDB-spatial + GDAL + Python (OSMnx, pvlib, rasterio) ; roofer/3dfier -> CityJSON LoD1.2/LoD2
Store:  PostGIS (+ 3DCityDB v5 if CityGML 3.0 compliance needed)
Serve:  pygeoapi (OGC API Features/Processes) + static 3D Tiles/PMTiles on any CDN
View:   CesiumJS (3D) or VC Map (turnkey UI)  |  MapLibre + deck.gl (2D/mobile)
Models: pvlib/r.sun (solar) · UMEP-SOLWEIG + Landsat LST (heat) · OSMnx/r5py (access, 3-30-300)
        SUMO (old-town traffic/parking) · HEC-RAS/ANUGA (Trebišnjica) · CEA (building energy)
People: Decidim (or lightweight map feedback) ; workshop with CityScope-style table
Govern: ISO/IEC 30173 vocabulary, CityGML 3.0/CityJSON, OGC APIs, NGSI-LD later; align with EU LDT Toolbox
```

Everything above is free and open source except HEC-RAS (free but closed source). None of it needs a cloud vendor.

---

## 7. Honest verdict
- **Checked in this research**: CesiumJS release; VC Map licence; Orion-LD release; 3DCityDB CityGML 3.0 support; pygeoapi licence; SUMO version and date; Decidim version, date and licence; Aino prices; ArcGIS Urban licensing tier; the EU LDT Toolbox launch (June 2026); LDT4SSC amounts and closure; DIGITAL call 7; BiH association to DEP and its date; the IPA III €140.5M announcement (Aug 2026); the World Bank GIVE project; Sarajevo's Mission Label; the Interreg HR-BA-ME budget and 2nd-call results; Overture licences; ISO/IEC 30173; CityGML 3.0 docs; the Batty 2024 DOI; the Blagonić 2025 paper; the A/B Street status.
- **Inferred**: several DOIs taken from publisher PIIs or URLs; Trebinje's eligibility in Interreg HR-BA-ME; GitHub release years where the tool's date parsing looked wrong.
- **Not checked**: Google Solar coverage for BiH (the coverage map is interactive only); RGURS LiDAR availability; the Espoo, Zurich, Rotterdam, Vienna and Tallinn details; commercial prices other than Aino; GIZ 2026 programmes; per-component licences of the LDT Toolbox; many licence strings marked [unverified].
