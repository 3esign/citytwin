"""A2/A3 heat_green.v0 — where is it hottest, and where would trees help most?

Evidence: LST and NDVI composites are Observed; the priority index is Estimated.
Valid scale: 30 m cells aggregated to blocks; LST is SURFACE temperature, never air temperature.

priority = z(LST within the built-up area) clipped >= 0
         x (1 - NDVI_scaled)                  # little vegetation now
         x built_share_150m (WorldCover 50)   # where people live and walk
Outputs: L4_heat_v0_priority.tif, L4_heat_v0_cells.geojson (top 10 % cells as 30 m squares),
         L4_heat_v0_buildings.geojson (LST/NDVI per building), L4_heat_v0_summary.json
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "fetch"))
from common import city, city_dir, manifest, now  # noqa: E402

def main(cid):
    import rasterio, geopandas as gpd
    from rasterio.vrt import WarpedVRT
    from rasterio.enums import Resampling
    from scipy.ndimage import uniform_filter
    from shapely.geometry import box
    c = city(cid); crs = c["crs"]["compute"]; L = city_dir(cid, "data", "layers")
    with rasterio.open(os.path.join(L, "L2_lst_summer_median.tif")) as r:
        lst = r.read(1); tr = r.transform; prof = r.profile; shape = lst.shape
    def onto(name, resampling):
        with rasterio.open(os.path.join(L, name)) as s, WarpedVRT(s, crs=crs, transform=tr, width=shape[1], height=shape[0], resampling=resampling) as v:
            return v.read(1).astype("float32")
    ndvi = onto("L2_ndvi_summer_median.tif", Resampling.average)
    wc = onto("L0_landcover_worldcover2021_core.tif", Resampling.mode)
    built = (wc == 50).astype("float32")
    built150 = uniform_filter(built, size=11)  # 11 x 30 m ~ 330 m window
    urban = built150 > 0.15
    mu, sd = np.nanmean(lst[urban]), np.nanstd(lst[urban])
    z = np.clip((lst - mu) / sd, 0, None)
    veg = np.clip((np.nan_to_num(ndvi, nan=0) - 0.1) / 0.6, 0, 1)
    pr = z * (1 - veg) * built150
    pr[~urban] = np.nan
    prof.update(dtype="float32", nodata=np.nan)
    with rasterio.open(os.path.join(L, "L4_heat_v0_priority.tif"), "w", **prof) as d: d.write(pr.astype("float32"), 1)
    thr = np.nanpercentile(pr, 90)
    rows, cols = np.where(pr >= thr)
    cells = []
    for i, j in zip(rows, cols):
        x0, y0 = tr * (j, i); x1, y1 = tr * (j + 1, i + 1)
        cells.append({"lst_c": round(float(lst[i, j]), 1), "ndvi": round(float(ndvi[i, j]), 2), "priority": round(float(pr[i, j]), 3), "geometry": box(x0, y1, x1, y0)})
    g = gpd.GeoDataFrame(cells, crs=crs); g["state"] = "Estimated"
    fp = os.path.join(L, "L4_heat_v0_cells.geojson")
    if os.path.exists(fp): os.remove(fp)
    g.to_crs("EPSG:4326").to_file(fp, driver="GeoJSON")
    b = gpd.read_file(os.path.join(L, "L0_buildings.gpkg")).to_crs(crs)
    rp = b.geometry.representative_point()
    inv = ~tr
    cc, rr = inv * (rp.x.values, rp.y.values)
    rr = np.clip(rr.astype(int), 0, shape[0] - 1); cc = np.clip(cc.astype(int), 0, shape[1] - 1)
    b["lst_c"] = np.round(lst[rr, cc], 1); b["ndvi"] = np.round(ndvi[rr, cc], 2); b["heat_priority"] = np.round(pr[rr, cc], 3)
    b["state"] = "Observed LST/NDVI; Estimated priority"
    fp = os.path.join(L, "L4_heat_v0_buildings.geojson")
    if os.path.exists(fp): os.remove(fp)
    b[[x for x in ["id", "class", "height", "num_floors", "lst_c", "ndvi", "heat_priority", "state", "geometry"] if x in b]].to_crs("EPSG:4326").to_file(fp, driver="GeoJSON")
    summ = {"time": now(), "algorithm": "heat_green.v0", "urban_lst_mean_c": round(float(mu), 1), "urban_lst_sd_c": round(float(sd), 1),
            "urban_lst_p95_c": round(float(np.nanpercentile(lst[urban], 95)), 1), "rural_lst_mean_c": round(float(np.nanmean(lst[~urban])), 1),
            "urban_ndvi_mean": round(float(np.nanmean(ndvi[urban])), 2), "priority_cells_top10pct": len(cells),
            "state": "Estimated", "caveats": ["surface temperature at ~10:00 local overpass, not air temperature at night",
                                              "Landsat thermal band is 100 m native, delivered at 30 m", "priority weights are a first proposal for the City to change"]}
    json.dump(summ, open(os.path.join(L, "L4_heat_v0_summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    manifest(cid, {"layer": "L4.heat_v0", "algorithm": "A2/A3", "path": "data/layers/L4_heat_v0_priority.tif", "state": "Estimated"})
    print(json.dumps(summ, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "trebinje")
