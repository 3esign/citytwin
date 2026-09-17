# Trebinje Digital Twin: Public Data Catalogue

**Area:** Grad Trebinje (Republika Srpska, BiH), centre about 42.711 N, 18.344 E. Area of interest: city core, Trebišnjica corridor (HE Trebinje / Gorica), Popovo polje.
**Compiled:** 2026-09-17, from web search and fetch.
**Marking:** `[unverified]` means the item was not confirmed on the source page during this pass. It may rely on general knowledge, or the page did not load (robots rules, timeout or TLS error).
**Access codes:** OPEN = open download · API = free API or registration · KEY = API key or account · REQ = request from an authority · PAID = paid.

---

## 1. Base geometry: buildings, terrain, imagery

| Source | Publisher | URL / endpoint | Format | Resolution / coverage | Licence | Vintage | Access | Themes |
|---|---|---|---|---|---|---|---|---|
| OpenStreetMap | OSM Foundation | https://www.openstreetmap.org ; Geofabrik BiH extract https://download.geofabrik.de/europe/bosnia-herzegovina.html ; Overpass https://overpass-api.de/api/interpreter | PBF, GeoJSON | Vector, whole city | ODbL | Continuous | OPEN / API | all; buildings, roads, POIs, heritage, Ćiro relation 7191321 |
| Overture Maps (buildings, places, transportation) | Overture Maps Foundation | https://docs.overturemaps.org ; s3://overturemaps-us-west-2/release/ | GeoParquet | Global; merges OSM, MS and Google footprints | ODbL / CDLA-P (per theme) | Monthly releases | OPEN | buildings, POIs, roads |
| Microsoft Global ML Building Footprints | Microsoft | https://github.com/microsoft/GlobalMLBuildingFootprints | GeoJSONL, quadkey partitions | Global incl. Europe; the 2026 update adds heights for parts of Europe | ODbL | 2026 update (Feb 2026) | OPEN | buildings, solar, heat |
| Google Open Buildings (v3) | Google Research | https://sites.research.google/open-buildings/ | CSV, GEE | Africa, S/SE Asia, Latin America. **Does not cover Europe/BiH** [unverified] | CC-BY 4.0 / ODbL | 2023 | OPEN | not usable for Trebinje |
| GHSL: built-up surface, built-up height (GHS-BUILT-S/H), settlement model, population (GHS-POP) | EC JRC | https://human-settlement.emergency.copernicus.eu/download.php | GeoTIFF | Global; 10 m (built-S 2018), 100 m (height, pop) | CC-BY 4.0 | R2023A (epochs 1975–2030) | OPEN | green/heat, population, planning |
| Copernicus DEM GLO-30 / GLO-90 | ESA / Copernicus | https://dataspace.copernicus.eu ; AWS s3://copernicus-dem-30m | COG GeoTIFF | 30 m DSM, global | Copernicus licence (free) | 2011–2015 TanDEM-X base | OPEN | flood, solar shading (coarse), terrain |
| EU-DEM v1.1 | EEA / Copernicus | https://land.copernicus.eu (EU-DEM) | GeoTIFF | 25 m, EEA39 incl. BiH [unverified] | Copernicus | 2016 | OPEN (legacy product) | terrain |
| ALOS World 3D (AW3D30) | JAXA | https://www.eorc.jaxa.jp/ALOS/en/aw3d30/ ; OpenTopography | GeoTIFF | 30 m DSM | Free with attribution | v4 (2023) | OPEN (registration) | terrain |
| TanDEM-X 90 m DEM | DLR | https://geoservice.dlr.de/web/dataguide/tdm90/ | GeoTIFF | 90 m (12 m version is commercial/science only) | Free (90 m) | 2016 | OPEN (registration) | terrain |
| OpenTopography | NSF | https://opentopography.org ; API https://portal.opentopography.org/apidocs/ | GeoTIFF | Serves global DEMs (COP30, SRTM, AW3D). **No LiDAR point cloud for Trebinje found** | per dataset | – | KEY (free) | terrain |
| Sentinel-2 L2A | ESA / Copernicus | https://dataspace.copernicus.eu ; STAC https://catalogue.dataspace.copernicus.eu/stac ; Sentinel Hub | JP2 / COG | 10–60 m, about 5-day revisit | Free/open | 2015 onward | OPEN / API | green, heat, land cover, fire scars, reservoir extent |
| Sentinel-1 GRD/SLC | ESA / Copernicus | same as above | SAFE / COG | 10 m SAR | Free/open | 2014 onward | OPEN | Popovo polje flood mapping, InSAR subsidence (EGMS) |
| European Ground Motion Service (EGMS) | Copernicus | https://egms.land.copernicus.eu | CSV / points | Point InSAR, Copernicus participating states; BiH coverage [unverified] | Copernicus | 2018–2022 onward | OPEN | buildings, dam, geohazard |
| Landsat 8/9 C2 L2 (incl. ST_B10 LST) | USGS | https://earthexplorer.usgs.gov ; https://landsatlook.usgs.gov/stac-server | COG | 30 m (thermal resampled from 100 m) | Public domain | 1984 onward | OPEN (EROS account) | heat (LST), green |
| ECOSTRESS LST | NASA JPL / LP DAAC | https://lpdaac.usgs.gov (ECO_L2T_LSTE) ; AppEEARS | COG | 70 m, irregular times incl. afternoon | Public domain | 2018 onward | OPEN (Earthdata login) | heat (diurnal) |
| MODIS LST / NDVI (MOD11, MOD13) | NASA | https://lpdaac.usgs.gov ; AppEEARS | HDF/COG | 250 m–1 km, daily | Public domain | 2000 onward | OPEN | heat trends, vegetation |
| Street-level: Google Street View | Google | Maps Platform Street View Static API | Images | **Trebinje covered (captured July 2024)**, BiH launch Nov 2025 | Proprietary ToS (no bulk derivation) | 2024 | KEY / PAID | visual verification, facades |
| Street-level: Mapillary | Meta | https://www.mapillary.com/app ; API https://graph.mapillary.com | Images, detections | Crowd-sourced; Trebinje density **not checked** [unverified] | CC-BY-SA 4.0 | varies | KEY (free) | parking signs, street greenery |
| Street-level: KartaView | Grab | https://kartaview.org | Images | Crowd-sourced; coverage [unverified] | CC-BY-SA | varies | OPEN | same |
| Orthophoto RS (DOF) | RGURS (Republička uprava za geodetske i imovinsko-pravne poslove RS) | https://geoportal.rgurs.org ; metadata catalogue https://geoportal.rgurs.org/metakatalog (GeoNetwork) | WMS view; GeoTIFF on request | Entity-wide; resolution and year [unverified] (typically 25–50 cm) | View free; data under RGURS fee schedule | [unverified] | OPEN view / PAID or REQ data | base imagery |
| LiDAR / DTM of RS | RGURS | via geoportal / request | LAS / GeoTIFF | **No public LiDAR for Trebinje found** | – | – | REQ | 3D city model, flood |

**OSM building completeness:** not measured. Overpass and ohsome queries were blocked by robots rules in this environment. Next step: run `way["building"](area:"Grad Trebinje")` in Overpass or use ohsome dashboard and compare with MS footprints. From general knowledge, the urban core is likely mapped well and villages or Popovo polje less so [unverified].

---

## 2. Land cover, green infrastructure, heat

| Source | Publisher | URL | Format | Resolution / coverage | Licence | Vintage | Access |
|---|---|---|---|---|---|---|---|
| CORINE Land Cover | EEA / CLMS | https://land.copernicus.eu/en/products/corine-land-cover | GPKG / GeoTIFF | 100 m raster / 25 ha MMU. BiH is included (EEA cooperating country) | Copernicus free | 1990–2018 (CLC+ Backbone 2021) | OPEN |
| HRL Imperviousness, Tree Cover Density, Grassland | EEA / CLMS | https://land.copernicus.eu/en/products/high-resolution-layer-imperviousness | GeoTIFF | 10/20 m, EEA38 incl. BiH [unverified] | Copernicus free | 2018, 2021 onward | OPEN |
| Urban Atlas 2018 / Street Tree Layer | EEA / CLMS | https://land.copernicus.eu/api/en/products/urban-atlas/urban-atlas-2018 | GPKG | FUAs with 50k+ population. **Trebinje (about 29k) is very likely NOT covered** [unverified: the product page was blocked by robots rules] | Copernicus free | 2018 (2021 update) | OPEN |
| ESA WorldCover | ESA | https://esa-worldcover.org ; AWS s3://esa-worldcover | COG | 10 m, global | CC-BY 4.0 | 2020, 2021 | OPEN |
| Meta/WRI High-Resolution Canopy Height | Meta & WRI | s3://dataforgood-fb-data/forests/v1/ ; GEE | COG | about 1 m, global | CC-BY 4.0 | 2018–2020 imagery (v2 2024 [unverified]) | OPEN |
| ETH Global Canopy Height 2020 | ETH Zürich (Lang et al.) | https://langnico.github.io/globalcanopyheight/ | GeoTIFF | 10 m | CC-BY 4.0 | 2020 | OPEN |
| Dynamic World | Google/WRI | GEE `GOOGLE/DYNAMICWORLD/V1` | raster | 10 m near-real-time | CC-BY 4.0 | 2015 onward | API (GEE) |
| ERA5 / ERA5-Land | ECMWF / C3S | https://cds.climate.copernicus.eu ; cdsapi | NetCDF / GRIB | 31 km / 9 km, hourly | Copernicus free | 1940/1950 to now | KEY (free) |
| Copernicus urban climate (UrbClim) | C3S | https://cds.climate.copernicus.eu (sis-urban-climate-cities) | NetCDF | 100 m for 100 EU cities; **Trebinje not included** [unverified] | free | 2008–2017 | KEY |
| RHMZ RS: meteorological station Trebinje | Republički hidrometeorološki zavod RS | https://rhmzrs.com [unverified: site not fetched] | Bulletins / yearbooks (PDF) | Station point (Trebinje main climatological station [unverified]) | Institutional; long series usually on request, possibly for a fee | long series | OPEN bulletins / REQ series |
| Open-Meteo (reanalysis + forecast) | Open-Meteo | https://open-meteo.com/en/docs/historical-weather-api | JSON | ERA5 / ECMWF-based, point query | CC-BY 4.0 | 1940 onward | API (no key) |

---

## 3. Energy and solar

| Source | Publisher | URL | Format | Coverage | Licence | Vintage | Access |
|---|---|---|---|---|---|---|---|
| PVGIS 5.3 | EC JRC | https://re.jrc.ec.europa.eu/pvg_tools/ ; API https://re.jrc.ec.europa.eu/api/v5_3/PVcalc | JSON / CSV | Europe incl. BiH (SARAH-3), point | Free | 2005–2023 | API (no key) |
| Global Solar Atlas | World Bank / Solargis | https://globalsolaratlas.info ; GIS download | GeoTIFF | about 250 m | CC-BY 4.0 | long-term avg | OPEN |
| Global Wind Atlas | DTU / World Bank | https://globalwindatlas.info | GeoTIFF | 250 m | CC-BY 4.0 | v3 | OPEN |
| City SEAP (Sustainable Energy Action Plan) | Grad Trebinje | referenced on https://investintrebinje.com/energy-efficiency-and-environmental-protection/?lang=en | PDF | City-wide baseline inventory | – | **SEAP adopted Dec 2011.** The city is a Covenant of Mayors signatory (per Invest in Trebinje). No SECAP found | OPEN (check mycovenant.eumayors.eu) / REQ |
| City energy management system (EMS/ISEE, UNDP) | Grad Trebinje / UNDP | not public | database | Public buildings' consumption | – | ongoing | **REQ** |
| Public lighting LED retrofits | Grad Trebinje | same page | text | 2013, 2015, 2018 (969 fixtures, about 60% saving). 2019 detailed lighting audits (Swedish-funded GED project) | – | 2013–2019 | OPEN summary / REQ inventory |
| HET: Hidroelektrane na Trebišnjici | ERS group | https://henatrebisnjici.com | web / annual reports | HE Trebinje I/II, Gorica, Bileća reservoir | – | annual | OPEN reports / REQ operational data |
| Elektro-Hercegovina a.d. Trebinje (DSO) | ERS group | https://www.elektrohercegovina.com | notices | distribution network, outages | – | – | **REQ** consumption by feeder or area |
| Solar plant Trebinje (utility scale) | ERS/HET [unverified] | https://sr.wikipedia.org/sr-el/Соларна_електрана_Требиње | – | – | – | [unverified] | OPEN (info) |
| Household solar subsidy programme | Grad Trebinje | news: padrino.ba "Trebinje: Počinje ugradnja solarnih panela domaćinstvima" | – | list of installations | – | [unverified] | REQ |
| Fond za zaštitu životne sredine i EE RS | Fond RS | https://www.ekofondrs.org [unverified] | calls, reports | project lists | – | – | OPEN / REQ |

---

## 4. Traffic, mobility, parking

| Source | Publisher | URL | Format | Coverage | Licence | Vintage | Access |
|---|---|---|---|---|---|---|---|
| Traffic counts on the RS road network (PGDS) | JP Putevi Republike Srpske | https://www.putevirs.com/korisnik/dokumenti/Brojanje_vozila_u_RS_2016.pdf (2009 and 2015 editions also exist) | PDF tables | Main/regional roads incl. M-20 / M-6 / R-436 around Trebinje [unverified station IDs] | – | 2009, 2015, 2016 published; newer [unverified] | OPEN (PDF) / REQ newer |
| JKP Parking servis Trebinje | City public utility | https://trebinjeparking.com | web | **1,130+ spaces**, Zone I and II, 3 garages. Pay by machines, SMS or GoParking app (Lanaco). Seasonal tariffs (Zone I 3/2 KM/h). Zones extended 1 Sep 2025 (night charging introduced) | – | 2025 | OPEN (text) / **REQ** occupancy, transactions, zone geometry |
| Road-safety statistics | Agencija za bezbjednost saobraćaja RS / MUP RS | https://www.absrs.org [unverified] ; MUP RS annual reports | PDF | entity / police-district level; municipal detail [unverified] | – | annual | OPEN summary / REQ geocoded accidents |
| Ćiro Trail (Mostar–Dubrovnik rail trail) | community / tourism boards | OSM relation https://www.openstreetmap.org/relation/7191321 ; https://ciro-trail.com ; GPX at https://www.herzegovinabike.ba | OSM / GPX | Trebinje sections (Zavala–Trebinje) | ODbL / proprietary GPX | current | OPEN |
| Bus lines / GTFS | local operators | **no GTFS found** | – | – | – | – | REQ |
| Street View / Mapillary | see §1 | | | | | | |

---

## 5. Tourism

| Source | Publisher | URL | Format | Coverage | Vintage | Access |
|---|---|---|---|---|---|---|
| TO Trebinje press releases | Turistička organizacija Grada Trebinja | https://gotrebinje.com/en/01-25/ , https://gotrebinje.com/en/01-2024/ , https://gotrebinje.com/en/1-23/ | web | Registered nights: 2022 over 180k, 2023 over 200k, **2024: 230,710**, 2025 about 215–216k (trebinjelive.info, 15 Jan 2026). About 50% from Serbia. Officials estimate real nights at 500–600k (only about 1/3 registered; about 700 listings vs 40–50 reporting) | 2022–2025 | OPEN (aggregates) |
| e-Turizam guest registration system | RS / TO | – | database | per-facility arrivals and nights | 2026 onward | **REQ** |
| RZS RS tourism statistics | Republički zavod za statistiku RS | https://www.rzs.rs.ba | PDF / XLS | arrivals and nights by municipality, monthly/annual | annual | OPEN |
| GoTrebinje POI listings (accommodation, parking, attractions) | TO Trebinje | https://gotrebinje.com/en/listings/ | web | POIs | current | OPEN (scrape with care) |
| OSM / Overture places | see §1 | | | | | OPEN |

---

## 6. Water, river, flood, karst

| Source | Publisher | URL | Format | Coverage | Licence | Vintage | Access |
|---|---|---|---|---|---|---|---|
| JRC European river flood hazard maps | EC JRC | https://data.jrc.ec.europa.eu/collection/id-0054 | GeoTIFF | 100 m, return periods 10–500 y. Coverage of the karst Trebišnjica [unverified] | CC-BY 4.0 | 2019–2024 | OPEN |
| JRC global flood hazard (GloFAS-based) | EC JRC | https://data.jrc.ec.europa.eu/dataset/jrc-floods-floodmapgl_rp50y-tif | GeoTIFF | 90 m global | CC-BY | 2016/2024 | OPEN |
| GloFAS / EFAS | Copernicus EMS | https://global-flood.emergency.copernicus.eu ; CDS `cems-glofas-historical` | NetCDF | 0.05° discharge reanalysis and forecasts | Copernicus (EFAS real-time restricted to partners) | 1979 onward | KEY (CDS) |
| Global Surface Water (JRC) | JRC / Google | https://global-surface-water.appspot.com | GeoTIFF | 30 m water occurrence (Gorica / Bileća reservoirs, Popovo polje inundation history) | CC-BY | 1984–2021 | OPEN |
| RHMZ RS hydrological stations | RHMZ RS | https://rhmzrs.com [unverified] | web / yearbook | Trebišnjica gauges (Trebinje; Gorica) [unverified] | institutional | – | OPEN current / REQ series |
| JU Vode Srpske | RS water agency | https://www.voders.org [unverified] | plans | Trebišnjica catchment (Adriatic basin) water management plan, flood-risk maps (EU Floods Directive-style PFRA) [unverified] | – | – | OPEN plans / REQ GIS |
| HET reservoir / discharge data | HET | https://henatrebisnjici.com | – | Bileća, Gorica levels, turbine outflow, Popovo polje concrete channel | – | – | **REQ** (operational) |
| Vodovod Trebinje | JKP Vodovod | Facebook page; no data portal found | – | network, consumption, outages | – | – | **REQ** |
| Academic: karst hydrology | Milanović P. et al. | https://www.researchgate.net/publication/312129932_Popovo_polje_a_different_view ; https://link.springer.com/article/10.1007/s10040-024-02811-0 (flood storage in Mediterranean karst, 2024) | papers | Popovo polje, Trebišnjica system | varies | 2016–2024 | OPEN / PAID |

---

## 7. Emergencies, fire, risk

| Source | Publisher | URL | Format | Coverage | Vintage | Access |
|---|---|---|---|---|---|---|
| EFFIS (fire danger, burnt areas, active fires) | Copernicus EMS / JRC | https://effis.emergency.copernicus.eu ; burnt-area WMS/WFS | WMS / shapefile | Europe incl. BiH; burnt areas of 30 ha and up | 2000 onward | OPEN |
| NASA FIRMS (MODIS/VIIRS hotspots) | NASA | https://firms.modaps.eosdis.nasa.gov/api/ | CSV / API | 375 m hotspots, NRT | 2000 onward | KEY (free) |
| Wildfire near Trebinje, 30 Aug 2026 | third-party aggregator | https://currentwildfires.com/en/fire/wildfire-near-trebinje-ba-2026-2/ | web | details not fetched [unverified] | 2026 | OPEN |
| Copernicus EMS rapid mapping | EC | https://mapping.emergency.copernicus.eu/activations/ | vector / PDF | **No activation specific to Trebinje found.** BiH 2014 floods (Sava basin) did not cover Trebinje [unverified] | – | OPEN |
| City risk assessment ("Procjena ugroženosti od elementarnih nepogoda i drugih nesreća za grad Trebinje") | Grad Trebinje / Civil protection | news: https://topportal.info/usvojena-procjena-ugrozenosti-od-elementarnih-nepogoda-i-drugih-nesreca-za-grad-trebinje/ (page not loaded) | PDF | floods, fire, earthquake, etc. | adoption date [unverified] | **REQ** full document and GIS layers |
| Republička uprava civilne zaštite RS | RS | https://www.ruczrs.org [unverified] | plans | entity risk assessment | – | OPEN / REQ |
| Seismic hazard (ESHM20 / EFEHR) | EFEHR | http://hazard.efehr.org | GeoTIFF / API | Europe incl. Balkans | 2020 | OPEN |

---

## 8. Population, statistics

| Source | Publisher | URL | Format | Coverage | Vintage | Access |
|---|---|---|---|---|---|---|
| Census 2013 (final) | Agencija za statistiku BiH | https://www.popis.gov.ba/popis2013/doc/RezultatiPopisa_BS.pdf | PDF / XLS | Municipality and settlement level | 2013 | OPEN |
| Census 2013 (RS publication, with maps) | RZS RS | https://www.rzs.rs.ba/static/uploads/bilteni/popis/PreliminarniRezultati_Popis2013-drugo_izdanje_sa_kartama_Final.pdf ; final results at https://www.rzs.rs.ba | PDF | RS municipalities | 2013 | OPEN |
| Population estimates | RZS RS | https://www.rzs.rs.ba | PDF / XLS | **Trebinje: 28,407 (census 2013 per RZS RS) → 28,626 (2024 estimate).** Estimates exclude external migration. Note: the BHAS/Wikipedia census figure is about 29.2k | annual | OPEN |
| Interactive population map | RGURS metakatalog | geoportal.rgurs.org/metakatalog (record f5c138ef…, returned 404 via API) | WMS | municipalities | – | OPEN [unverified] |
| statistika.ba (1991 census mapped to 2013 settlements) | private | http://www.statistika.ba/?show=15 | web | settlements | – | OPEN |
| WorldPop | Univ. Southampton | https://hub.worldpop.org (BIH) ; constrained 100 m | GeoTIFF | 100 m, age/sex | 2000–2020 (+2025 R2025A [unverified]) | OPEN, CC-BY 4.0 |
| Meta High Resolution Population Density | Meta / CIESIN | https://data.humdata.org (search "Bosnia high resolution population") | GeoTIFF / CSV | about 30 m; BiH availability [unverified] | 2020 | OPEN, CC-BY |
| GHS-POP | JRC | see §1 | GeoTIFF | 100 m | 2020/2025/2030 | OPEN |

---

## 9. Planning, cadastre, public buildings

| Source | Publisher | URL | Format | Coverage | Vintage | Access |
|---|---|---|---|---|---|---|
| **Prostorni plan Grada Trebinja** | Grad Trebinje | https://trebinje.rs.ba/prostorni-plan-grada-trebinja/ ; text https://trebinje.rs.ba/wp-content/uploads/2022/09/PPG-Trebinje_PLAN-JUL-2022_text_final-1.pdf ; land-use map JPG https://trebinje.rs.ba/wp-content/uploads/2022/09/1_Osnovna_namjena_povrsina-1-scaled.jpg | PDF + raster JPG (no GIS) | whole city | July 2022 | OPEN |
| **Urbanistički plan Grada Trebinja** | Grad Trebinje | https://trebinje.rs.ba/urbanisticki-plan/ ; https://trebinje.rs.ba/wp-content/uploads/2025/12/UP-Trebinje-elaborat_A3_PLAN.pdf ; synthesis map https://trebinje.rs.ba/wp-content/uploads/2025/12/B1-Planirana-namjena-sintezna-karta-1-scaled.jpg | PDF + JPG | urban area | Dec 2025 | OPEN |
| **Regulacioni planovi** (35 PDFs) | Grad Trebinje | https://trebinje.rs.ba/regulacioni-planovi/ (files under /wp-content/uploads/YYYY/MM/) | PDF | Zasad polje (7 amendments, 2012–2025); Bregovi 1, 2, Jug (2011–2022); Južni gradski izlaz (2010–2024); Sjeverni Logor (2012–2022); Istočni Logor (2015); Novo Trebinje (zoning plan 2017–2019); Blace–Abazovinka (2011–2024); Centar (2009); Stari grad (2009; new plan in preparation per trebinjedanas.com); Grad sunca (2016–2024); Humac and Ubla (zoning plans 2021) | 2009–2025 | OPEN (PDF only) |
| Guide to location and building permits | Grad Trebinje | https://trebinje.rs.ba/vodic-za-dobijanje-lokacijskih-i-gradjevinskih-dozvola/ | web | procedure | – | OPEN |
| Development Strategy 2018–2027 | Grad Trebinje | https://investintrebinje.com/wp-content/uploads/2019/07/Development-Strategy-2018-2027-pdf.pdf | PDF | socio-economic baseline | 2019 | OPEN |
| City budget | Grad Trebinje | https://trebinje.rs.ba (Službeni glasnik / budget pages) [unverified exact URL] | PDF | annual | annual | OPEN (PDF); no open-data portal found |
| Cadastre (e-Katastar) | RGURS | https://www.rgurs.org/sr-lat/stranica/e-katastar ; https://www.rgurs.org/sr-lat/stranica/e-servisi | web viewer (parcel lookup) | parcels, buildings, ownership (view) | current | OPEN view / **PAID or REQ** vector extract |
| Geoportal RS (NSDI, GeoNetwork) | RGURS | https://geoportal.rgurs.org ; legacy http://www.geoportal.rgurs.org/index_lat.html | WMS/WFS [unverified endpoints] | RS-wide: orthophoto, topo maps, address register, cadastre overview | – | OPEN view |
| Spatial Plan of RS | Ministarstvo za prostorno uređenje, građevinarstvo i ekologiju RS | https://www.vladars.rs (ministry pages) [unverified] | PDF | entity | 2015–2025 plan (new one in preparation) [unverified] | OPEN |
| Public buildings register (schools, kindergartens, health) | Grad Trebinje / ministries | – | – | – | – | **REQ** (EMS/ISEE gives floor areas and energy use) |
| Address register | RGURS | via geoportal [unverified] | – | – | – | OPEN view / REQ |

---

## 10. Heritage

| Source | Publisher | URL | Format | Notes | Access |
|---|---|---|---|---|---|
| KONS national monuments database | Komisija za očuvanje nacionalnih spomenika BiH | http://aplikacija.kons.gov.ba/kons/public/nacionalnispomenici ; map https://www.kons.gov.ba/Content/Map ; petitions by municipality https://www.kons.gov.ba/data/Novi%20dokumenti/Peticije/peticije-opcine-07.02.2023.pdf | web / PDF | Decisions are published in Službeni glasnik BiH | OPEN |
| Zavod za zaštitu kulturno-istorijskog i prirodnog nasljeđa RS | RS | https://nasljedje.org [unverified] | – | entity heritage register | OPEN / REQ |

**Designated national monuments in Trebinje (confirmed in sources):** local media report 36 (2019), later 42 designated plus 58 on the provisional list.
- Arslanagić (Perović) bridge, historic monument, 2006 ([KONS app](http://aplikacija.kons.gov.ba/kons/public/nacionalnispomenici))
- Historic urban area of Trebinje (Old town Kastel, Krš, city centre, 3 zones), 16 May 2019
- Church of St John the Baptist, Donje Vrbno, 16 May 2019
- Church of St Basil of Ostrog, Gornje Vrbno, 29 Aug 2019
- Church of the Ascension, Konjsko–Zupci, 26 Jun 2019
- Church of the Dormition, Mosko, 26 Jun 2019
- Church of the Ascension, Dubočani, 2 Jul 2020
- Church of St Panteleimon with old school (1762), Aleksina Međa, Jan 2019
- Churches of St Nicholas and Nativity of St John the Baptist, Popovo (Poljice), late 2017
- Church of the Prophet Elijah, Sedlari, Mar 2018
- Mosque in Mostaći, 2019
- Džamija (Dživar) with cemetery, Donje Čičevo, Mar 2019

Sources for this list: [Radio Trebinje 1](https://radiotrebinje.com/vijest/putokazi-iz-proslosti-trebinje-sve-bogatije-nacionalnim-spomenicima/?lang=lat) and [Radio Trebinje 2](https://radiotrebinje.com/vijest/nacionalni-spomenici-u-trebinju-blago-koje-treba-sacuvati?lang=lat).

The other monuments (about 30) were not enumerated here: Tvrdoš monastery, Osman-pasha mosque, Duži monastery, Zavala monastery, Mrkonjići, stećci sites and others are likely on the list [unverified]. Extract them from the KONS app (filter by "Trebinje"). Individual KONS decision pages carry coordinates or descriptions.

**Hercegovačka Gračanica** (built 2000) is not a national monument [unverified]. It is a tourism POI.

---

## 11. Citizen participation, e-government

| Source | URL | Notes | Access |
|---|---|---|---|
| Grad Trebinje portal (news, Službeni glasnik, public calls, public consultations on plans) | https://trebinje.rs.ba | Public hearings on regulation plans are announced there | OPEN |
| "Smart city Trebinje" announcement | https://rejting.info/trebinje/smart-city-uskoro-u-trebinju/ | Content not loaded [unverified] | – |
| Invest in Trebinje | https://investintrebinje.com | investment zones, EE projects | OPEN |
| Local media (trebinjelive.info, radiotrebinje.com, etrebinje.com) | – | event/incident signals | OPEN |
| **No open-data portal, city GIS portal or "Geoportal Trebinje" was found** | – | – | – |

---

## Request list for the City of Trebinje (and its companies)

1. **Plans in GIS form**: Spatial plan (2022), Urban plan (2025) and all 35 regulation plans as SHP/DWG/GPKG. Only PDF/JPG are public.
2. **Cadastre and building extract** from RGURS (via the City's Urbanizam/Geodetic dept): parcels, building footprints with floors, use and year. Also the orthophoto GeoTIFF and any LiDAR or DTM.
3. **Energy**: the UNDP EMS/ISEE database for public buildings (consumption, floor area, energy source), SEAP 2011 and its monitoring reports, and the public-lighting inventory (points, lamp types, kWh). Also the household solar subsidy list.
4. **Elektro-Hercegovina**: aggregated consumption per transformer station or neighbourhood, plus the list of prosumers and PV connections.
5. **Parking servis**: zone polygons, space counts, hourly occupancy and payment transactions (SMS/app/machines), and garage counters.
6. **Traffic**: any city traffic counts, the traffic study behind the regulation plans, and geocoded accident data (police / MUP RS). Also newer Putevi RS PGDS counts for stations near Trebinje.
7. **Tourism**: monthly e-Turizam arrivals and nights by facility and location (anonymised), plus the list of accommodation units.
8. **Water**: Vodovod network (pipes, reservoirs, sources), consumption by zone, and outages. HET reservoir levels and releases (Gorica, Bileća). RHMZ RS hydrological and meteorological series for the Trebinje stations.
9. **Risk**: the full "Procjena ugroženosti" document with flood, fire and seismic maps; civil-protection assets; fire-brigade intervention logs.
10. **Public buildings register**: schools, kindergartens, health centres, administration, with addresses, areas, occupancy and year built.
11. **Green**: city tree cadastre, parks and green-area inventory (Komunalno / Zelenilo), plus irrigation.
12. **Heritage**: the RS heritage institute register and protection zones for the historic urban area (2019 decision) as GIS.
13. **Budget / capital investments**: machine-readable (XLS) budget and capital-project list with locations.
14. **Public transport**: routes, stops and timetables (for GTFS).

## Gaps

- **No high-resolution 3D / LiDAR** available publicly. The 3D model must come from the RGURS request, or from MS 2026 heights + Copernicus DEM + GHSL height (coarse).
- **Urban Atlas and UrbClim likely do not cover Trebinje** (the city is below the FUA threshold). Heat analysis must rely on Landsat, ECOSTRESS and Sentinel-2 plus HRL layers.
- **Planning documents are PDF/JPG only.** There is no GIS, open-data portal or city geoportal.
- **No real-time or open sensor data** for traffic, parking occupancy, air quality, noise or water level.
- **Tourism statistics undercount** real visits by about 2–3x (officials' own estimate). e-Turizam data is not public.
- **Energy consumption** of buildings or districts is not public. The SEAP is from 2011 and no SECAP was found.
- **Karst hydrology** (Popovo polje, sinkholes, HET-controlled flows) is not represented in generic JRC/GloFAS flood models. This needs HET/Vode Srpske data and academic models.
- **Population** has no census since 2013. Estimates exclude migration, and tourist or seasonal population is invisible.
- **Not verified in this pass** (sites blocked or timed out): rhmzrs.com, rgurs.org geoportal endpoints, Urban Atlas coverage page, OSM building counts, Mapillary density, the full KONS list, the risk-assessment date and the Smart City project content.
