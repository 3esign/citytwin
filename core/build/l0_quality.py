"""L0 quality and enrichment:
  1. building completeness per 100 m cell: GHSL built surface (2020) vs Overture footprint area
     -> L0Q_completeness_cells.geojson (cells where GHSL sees >= 1500 m2 built but footprints cover < 35 %)
  2. building height estimate: GHSL average gross building height (2018) of the building's cell
     where Overture has no height -> L0Q_buildings_height.gpkg/.geojson (height_est, floors_est, height_origin)
  3. population: GHS-POP 2025 in the core bbox and assigned to residential-looking buildings by floor area
Evidence: every derived value is Estimated and says where it came from."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "fetch"))
from common import city, city_dir, manifest, now

def main(cid):
    import rasterio, geopandas as gpd
    from shapely.geometry import box
    c = city(cid); crs = c["crs"]["compute"]; L = city_dir(cid, "data", "layers")
    with rasterio.open(os.path.join(L, "L0_built_surface_ghs2020.tif")) as r:
        bs = r.read(1); tr = r.transform; shape = bs.shape
    with rasterio.open(os.path.join(L, "L0_built_height_ghs2018.tif")) as r: bh = r.read(1)
    with rasterio.open(os.path.join(L, "L0_pop_ghs2025.tif")) as r: pop = r.read(1)
    b = gpd.read_file(os.path.join(L, "L0_buildings.gpkg")).to_crs(crs)
    b["fp"] = b.geometry.area
    rp = b.geometry.representative_point()
    inv = ~tr
    cc, rr = inv * (rp.x.values, rp.y.values)
    rr = rr.astype(int); cc = cc.astype(int)
    ok = (rr >= 0) & (rr < shape[0]) & (cc >= 0) & (cc < shape[1])
    fp_cell = np.zeros(shape, dtype="float64")
    np.add.at(fp_cell, (rr[ok], cc[ok]), b.fp.values[ok])
    # 1. completeness
    cov = np.where(bs > 0, fp_cell / bs, np.nan)
    miss = (bs >= 1500) & (np.nan_to_num(cov) < 0.35)
    cells = []
    for i, j in zip(*np.where(miss)):
        x0, y0 = tr * (j, i); x1, y1 = tr * (j + 1, i + 1)
        cells.append({"ghs_built_m2": round(float(bs[i, j])), "footprint_m2": round(float(fp_cell[i, j])),
                      "coverage": round(float(np.nan_to_num(cov[i, j])), 2), "geometry": box(x0, y1, x1, y0)})
    g = gpd.GeoDataFrame(cells, geometry="geometry", crs=crs) if cells else gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs=crs)
    fp = os.path.join(L, "L0Q_completeness_cells.geojson")
    if os.path.exists(fp): os.remove(fp)
    g.to_crs("EPSG:4326").to_file(fp, driver="GeoJSON")
    built_cells = bs >= 1500
    agg_cov = float(fp_cell[built_cells].sum() / bs[built_cells].sum()) if built_cells.any() else None
    # 2. heights
    hcell = np.full(len(b), np.nan)
    hcell[ok] = bh[rr[ok], cc[ok]]
    has = b["height"].notna() if "height" in b else np.zeros(len(b), bool)
    b["height_est"] = np.where(has, b.get("height"), np.where(np.nan_to_num(hcell) > 0, np.round(hcell, 1), 6.0))
    b["height_origin"] = np.where(has, "overture", np.where(np.nan_to_num(hcell) > 0, "ghsl_agbh_2018_cell_mean", "default_6m"))
    fl = b["num_floors"] if "num_floors" in b else np.nan
    b["floors_est"] = np.where(pd_notna(fl), fl, np.clip(np.round(b["height_est"] / 3.0), 1, None))
    b["floor_area_est"] = (b.fp * b.floors_est).round(0)
    # 3. population to buildings (only cells with population; share by floor area; non-residential classes excluded)
    nonres = {"church", "chapel", "mosque", "school", "industrial", "retail", "office", "hospital", "train_station", "bunker", "roof", "post_office", "university", "garage", "garages", "shed"}
    resid = ~b.get("class", np.nan).isin(nonres) if "class" in b else np.ones(len(b), bool)
    fa_cell = np.zeros(shape); np.add.at(fa_cell, (rr[ok & resid], cc[ok & resid]), b.floor_area_est.values[ok & resid])
    share = np.zeros(len(b))
    idx = np.where(ok & resid)[0]
    denom = fa_cell[rr[idx], cc[idx]]
    share[idx] = np.where(denom > 0, b.floor_area_est.values[idx] / denom, 0)
    pc = np.zeros(len(b)); pc[ok] = np.nan_to_num(pop[rr[ok], cc[ok]])
    b["residents_est"] = np.round(pc * share, 1)
    b["state"] = "Estimated"
    cols = [x for x in ["id", "class", "height", "num_floors", "fp", "height_est", "height_origin", "floors_est", "floor_area_est", "residents_est", "state", "geometry"] if x in b]
    out = os.path.join(L, "L0Q_buildings_height")
    for ext, drv in ((".gpkg", "GPKG"), (".geojson", "GeoJSON")):
        if os.path.exists(out + ext): os.remove(out + ext)
        b[cols].to_crs("EPSG:4326").to_file(out + ext, driver=drv)
    pop_bbox = float(np.nansum(pop))
    pop_in_buildings = float(b.residents_est.sum())
    summ = {"time": now(), "cells_ghs_built_ge_1500m2": int(built_cells.sum()),
            "footprint_coverage_of_ghs_built_surface": None if agg_cov is None else round(agg_cov, 3),
            "cells_possibly_missing_buildings": len(cells),
            "height_origin_counts": b.height_origin.value_counts().to_dict(),
            "floor_area_est_m2_total": round(float(b.floor_area_est.sum())),
            "ghs_pop_2025_core_bbox": round(pop_bbox), "residents_assigned_to_buildings": round(pop_in_buildings),
            "official_city_estimate_2024": c.get("population_official", {}).get("2024_estimate_rzs_rs"),
            "note": "bbox is not the city boundary; GHS-POP is modelled; official figure covers the whole city territory",
            "state": "Estimated"}
    json.dump(summ, open(os.path.join(L, "L0Q_summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    manifest(cid, {"layer": "L0Q", "path": "data/layers/L0Q_buildings_height.gpkg", "state": "Estimated"})
    print(json.dumps(summ, ensure_ascii=False, indent=1))

def pd_notna(v):
    import pandas as pd
    return pd.notna(v)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "trebinje")
