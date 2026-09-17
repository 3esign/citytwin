"""A1 solar.rooftop.v0 — screening of rooftop PV potential for every building.

Question: "Where do we put solar panels first?"   Evidence state of all outputs: Estimated.
Valid scale: building screening (not installation design).

Method
  1. Terrain horizon per building from the DSM (samples from 300 m to 20 km, 36 azimuths).
     Near samples are skipped on purpose: a 30 m DSM contains trees and roofs, which would
     make noise, not shading. Neighbour shading is v2 (LoD2 + r.sun).
  2. Sun path for one year (hourly, NOAA equations). Share of beam energy lost behind the
     horizon = sum(sin(elev) where elev < horizon(az)) / sum(sin(elev) where elev > 0).
  3. Sky view factor for diffuse light = mean over azimuths of cos^2(horizon).
  4. E_roof = GHI * [(1-kd)*(1-beam_loss) + kd*SVF]   (kWh/m2/yr on a horizontal plane;
     tilted optimal panels would gain ~10-15 %, ignored = conservative)
  5. kWh/yr = E_roof * footprint * usable_share * efficiency * performance_ratio
Inputs: L0_buildings.gpkg, L0_terrain_dem30_horizon.tif, params.json (GHI and kd with source)
Outputs: L4_solar_v0.gpkg / .geojson, L4_solar_v0_top_public.csv, L4_solar_v0_summary.json
"""
import json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "fetch"))
from common import city, city_dir, jfield, manifest, now  # noqa: E402

DEFAULTS = {
    "ghi_kwh_m2_yr": None,          # must come from a recorded source (params.json)
    "ghi_source": None,
    "diffuse_fraction": 0.35,       # typical for S Adriatic hinterland; replace with source value
    "usable_roof_share": 0.60,
    "module_efficiency": 0.20,
    "performance_ratio": 0.80,
    "kwp_per_m2": 0.20,
    "horizon_min_m": 300, "horizon_max_m": 20000, "horizon_step_m": 60, "azimuths": 36,
    "min_footprint_m2": 30,
}
PUBLIC_CLASSES = {"civic", "government", "public", "school", "kindergarten", "university", "college",
                  "hospital", "fire_station", "police", "library", "sports_hall", "stadium",
                  "community_centre", "townhall", "museum", "theatre"}
PUBLIC_PLACE_WORDS = ("school", "kindergarten", "university", "college", "hospital", "clinic", "health",
                      "government", "city_hall", "town_hall", "police", "fire_station", "library",
                      "museum", "theatre", "sports", "stadium", "community", "public_service", "post_office")

def sun_positions(lat, lon, year=2025):
    """Hourly solar elevation/azimuth (deg) for a year, NOAA simplified equations, UTC times."""
    t = np.arange(0, 365 * 24) + 0.5
    doy = t / 24.0
    g = 2 * np.pi / 365 * (doy - 1)
    eqt = 229.18 * (0.000075 + 0.001868 * np.cos(g) - 0.032077 * np.sin(g) - 0.014615 * np.cos(2 * g) - 0.040849 * np.sin(2 * g))
    decl = (0.006918 - 0.399912 * np.cos(g) + 0.070257 * np.sin(g) - 0.006758 * np.cos(2 * g)
            + 0.000907 * np.sin(2 * g) - 0.002697 * np.cos(3 * g) + 0.00148 * np.sin(3 * g))
    minutes_utc = (t % 24) * 60
    tst = minutes_utc + eqt + 4 * lon
    ha = np.radians(tst / 4 - 180)
    la = np.radians(lat)
    cz = np.sin(la) * np.sin(decl) + np.cos(la) * np.cos(decl) * np.cos(ha)
    zen = np.arccos(np.clip(cz, -1, 1))
    elev = 90 - np.degrees(zen)
    az = np.degrees(np.arctan2(np.sin(ha), np.cos(ha) * np.sin(la) - np.tan(decl) * np.cos(la))) + 180  # 0=N, clockwise
    up = elev > 0
    return elev[up], az[up] % 360

def horizons(xy_utm, dem, dem_to_utm, p):
    """Horizon angle (deg) per point per azimuth. dem: rasterio dataset in EPSG:4326."""
    from pyproj import Transformer
    utm_to_geo = Transformer.from_crs(dem_to_utm, "EPSG:4326", always_xy=True)
    arr = dem.read(1).astype("float32")
    nod = dem.nodata
    if nod is not None: arr[arr == nod] = np.nan
    inv = ~dem.transform
    dists = np.arange(p["horizon_min_m"], p["horizon_max_m"] + 1, p["horizon_step_m"], dtype="float64")
    azs = np.radians(np.arange(p["azimuths"]) * 360.0 / p["azimuths"])
    # observer ground elevation
    lon0, lat0 = utm_to_geo.transform(xy_utm[:, 0], xy_utm[:, 1])
    c0, r0 = inv * (lon0, lat0)
    z0 = sample(arr, r0, c0) + 3.0  # roof ~ 3 m above DSM-ground is irrelevant at >300 m; small offset
    out = np.zeros((len(xy_utm), len(azs)), dtype="float32")
    for j, a in enumerate(azs):
        dx, dy = np.sin(a) * dists, np.cos(a) * dists
        X = xy_utm[:, [0]] + dx[None, :]; Y = xy_utm[:, [1]] + dy[None, :]
        lon, lat = utm_to_geo.transform(X.ravel(), Y.ravel())
        c, r = inv * (np.asarray(lon), np.asarray(lat))
        z = sample(arr, r, c).reshape(X.shape)
        ang = np.degrees(np.arctan2(z - z0[:, None], dists[None, :]))
        out[:, j] = np.nan_to_num(np.nanmax(ang, axis=1), nan=0.0).clip(min=0)
    return out, z0

def sample(arr, r, c):
    r = np.asarray(r).astype(int); c = np.asarray(c).astype(int)
    ok = (r >= 0) & (r < arr.shape[0]) & (c >= 0) & (c < arr.shape[1])
    v = np.full(r.shape, np.nan, dtype="float32")
    v[ok] = arr[r[ok], c[ok]]
    return v

def main(cid):
    import geopandas as gpd, rasterio, pandas as pd
    c = city(cid); crs = c["crs"]["compute"]
    L = city_dir(cid, "data", "layers")
    ppath = os.path.join(HERE, "params", f"{cid}.json")
    p = dict(DEFAULTS); p.update(json.load(open(ppath, encoding="utf-8")) if os.path.exists(ppath) else {})
    ghi_r = os.path.join(L, "L2_gsa_ghi_yearly.tif"); dif_r = os.path.join(L, "L2_gsa_dif_yearly.tif")
    use_raster = os.path.exists(ghi_r)
    if not use_raster and not p["ghi_kwh_m2_yr"]:
        sys.exit(f"GHI missing: run core/fetch/solar_atlas.py or put ghi_kwh_m2_yr + ghi_source in {ppath}")
    b = gpd.read_file(os.path.join(L, "L0_buildings.gpkg")).to_crs(crs)
    b["footprint_m2"] = b.geometry.area
    b = b[b.footprint_m2 >= p["min_footprint_m2"]].copy()
    xy = np.column_stack([b.geometry.representative_point().x, b.geometry.representative_point().y])
    elev, az = sun_positions(c["centre"]["lat"], c["centre"]["lon"])
    w = np.sin(np.radians(elev)); wsum = w.sum()
    azi_idx = np.round(az / (360.0 / p["azimuths"])).astype(int) % p["azimuths"]
    with rasterio.open(os.path.join(L, "L0_terrain_dem30_horizon.tif")) as dem:
        H = np.zeros((len(b), p["azimuths"]), dtype="float32"); Z = np.zeros(len(b), dtype="float32")
        for s in range(0, len(b), 400):
            H[s:s + 400], Z[s:s + 400] = horizons(xy[s:s + 400], dem, crs, p)
            print(f"  horizon {min(s + 400, len(b))}/{len(b)}", flush=True)
    beam_loss = np.array([(w * (elev < h[azi_idx])).sum() / wsum for h in H])
    svf = np.mean(np.cos(np.radians(H)) ** 2, axis=1)
    if use_raster:
        pts = gpd.GeoSeries(b.geometry.representative_point(), crs=crs).to_crs("EPSG:4326")
        coords = list(zip(pts.x, pts.y))
        with rasterio.open(ghi_r) as r: ghi = np.array([v[0] for v in r.sample(coords)], dtype="float64")
        if os.path.exists(dif_r):
            with rasterio.open(dif_r) as r: dif = np.array([v[0] for v in r.sample(coords)], dtype="float64")
            kd = np.clip(dif / np.where(ghi > 0, ghi, np.nan), 0.1, 0.9)
            kd = np.where(np.isnan(kd), p["diffuse_fraction"], kd)
        else:
            kd = p["diffuse_fraction"]
        p["ghi_source"] = "Global Solar Atlas v2 (S-010), sampled per building"
    else:
        ghi = p["ghi_kwh_m2_yr"]; kd = p["diffuse_fraction"]
    b["ghi_kwh_m2_yr"] = np.round(ghi, 0)
    b["horizon_max_deg"] = H.max(axis=1).round(1)
    b["beam_loss_pct"] = (100 * beam_loss).round(1)
    b["sky_view"] = svf.round(3)
    b["irr_kwh_m2_yr"] = (ghi * ((1 - kd) * (1 - beam_loss) + kd * svf)).round(0)
    b["usable_m2"] = (b.footprint_m2 * p["usable_roof_share"]).round(0)
    b["kwp"] = (b.usable_m2 * p["kwp_per_m2"]).round(1)
    b["kwh_yr"] = (b.irr_kwh_m2_yr * b.usable_m2 * p["module_efficiency"] * p["performance_ratio"]).round(0)
    b["state"] = "Estimated"
    q = os.path.join(L, "L0Q_buildings_height.gpkg")
    if os.path.exists(q):
        hq = gpd.read_file(q, columns=["id", "height_est", "floors_est"], ignore_geometry=True)
        b = b.merge(hq, on="id", how="left")
    # public buildings: own class or a public place inside the footprint
    pub = b["class"].fillna("").isin(PUBLIC_CLASSES) if "class" in b else pd.Series(False, index=b.index)
    pl_path = os.path.join(L, "L0_places.gpkg")
    b["public_hint"] = np.where(pub, b["class"] if "class" in b else None, None)
    b["public_category"] = np.where(pub, "building class", None)
    if os.path.exists(pl_path):
        pl = gpd.read_file(pl_path).to_crs(crs)
        allowed = set(c.get("public_building_categories", []))
        pl["cat"] = pl["categories"].map(jfield).fillna("") if "categories" in pl else ""
        pl = pl[pl["cat"].isin(allowed)]
        if len(pl):
            j = gpd.sjoin(pl[["names", "cat", "geometry"]], b[["geometry"]], predicate="within", how="inner")
            for idx, grp in j.groupby("index_right"):
                nm = grp["names"].map(jfield).dropna()
                b.loc[idx, "public_hint"] = (nm.iloc[0] if len(nm) else grp["cat"].iloc[0])
                b.loc[idx, "public_category"] = grp["cat"].iloc[0]
    b["is_public"] = b["public_hint"].notna()
    out = os.path.join(L, "L4_solar_v0")
    cols = [x for x in ["id", "class", "names", "footprint_m2", "ghi_kwh_m2_yr", "horizon_max_deg", "beam_loss_pct", "sky_view", "irr_kwh_m2_yr", "usable_m2", "kwp", "kwh_yr", "is_public", "public_hint", "public_category", "height_est", "floors_est", "state", "geometry"] if x in b]
    g = b[cols].to_crs("EPSG:4326")
    for ext, drv in ((".gpkg", "GPKG"), (".geojson", "GeoJSON")):
        if os.path.exists(out + ext): os.remove(out + ext)
        g.to_file(out + ext, driver=drv)
    top = b[b.is_public].sort_values("kwh_yr", ascending=False).head(30)
    top[[x for x in ["id", "public_hint", "public_category", "class", "footprint_m2", "kwp", "kwh_yr", "irr_kwh_m2_yr", "beam_loss_pct"] if x in top]].to_csv(out + "_top_public.csv", index=False, encoding="utf-8")
    top_cols = [x for x in ["id", "public_hint", "public_category", "class", "footprint_m2", "kwp", "kwh_yr", "irr_kwh_m2_yr", "beam_loss_pct"] if x in top]
    json.dump(json.loads(top[top_cols].to_json(orient="records", force_ascii=False)), open(out + "_top_public.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    summ = {"time": now(), "algorithm": "solar.rooftop.v0", "params": p, "buildings": int(len(b)),
            "public_buildings_detected": int(b.is_public.sum()),
            "total_kwp": round(float(b.kwp.sum())), "total_mwh_yr": round(float(b.kwh_yr.sum()) / 1000),
            "public_kwp": round(float(b[b.is_public].kwp.sum())), "public_mwh_yr": round(float(b[b.is_public].kwh_yr.sum()) / 1000),
            "irr_min_max": [float(b.irr_kwh_m2_yr.min()), float(b.irr_kwh_m2_yr.max())],
            "beam_loss_pct_median": float(b.beam_loss_pct.median()), "state": "Estimated",
            "caveats": ["terrain horizon only (>300 m); no neighbour or tree shading", "horizontal-plane irradiance; no tilt/orientation",
                        "footprint as roof area proxy; usable share is a parameter", "public buildings detected from open data — incomplete until the City register (R3)"]}
    json.dump(summ, open(out + "_summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    manifest(cid, {"layer": "L4.solar_v0", "algorithm": "A1", "path": os.path.relpath(out + ".gpkg", city_dir(cid)), "state": "Estimated", "count": int(len(b))})
    print(json.dumps(summ, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "trebinje")
