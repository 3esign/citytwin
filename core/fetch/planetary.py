"""L2 periodic: summer land surface temperature (Landsat 8/9 C2 L2) and NDVI (Sentinel-2 L2A)
from Microsoft Planetary Computer (STAC + SAS tokens; robots.txt allows all).
Composites = per-pixel median over clear pixels of all summer scenes (Jun-Aug) in the given years."""
import json, os, sys, urllib.request
import numpy as np
from common import UA, city, city_dir, get, manifest

STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
SAS = "https://planetarycomputer.microsoft.com/api/sas/v1/token/{}"

def search(collection, bbox, years, cloud=20, extra=None):
    items = []
    for y in years:
        body = {"collections": [collection], "bbox": bbox, "datetime": f"{y}-06-01/{y}-08-31", "limit": 100,
                "query": {"eo:cloud_cover": {"lt": cloud}, **(extra or {})}}
        req = urllib.request.Request(STAC, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            items += json.load(r)["features"]
    return items

def token(collection):
    return json.loads(get(SAS.format(collection)))["token"]

def read_window(href, bounds_wgs, dst_crs, res, shape, transform, resampling="bilinear"):
    """Warp only the blocks that cover our grid (WarpedVRT reads lazily over HTTP)."""
    import rasterio
    from rasterio.vrt import WarpedVRT
    from rasterio.enums import Resampling
    with rasterio.open(href) as src, WarpedVRT(src, crs=dst_crs, transform=transform, width=shape[1], height=shape[0],
                                               resampling=getattr(Resampling, resampling), src_nodata=src.nodata, nodata=0) as vrt:
        out = vrt.read(1).astype("float32")
    out[out == 0] = np.nan
    return out

def grid(c, res):
    from pyproj import Transformer
    from rasterio.transform import from_origin
    b = c["bbox_core"]; crs = c["crs"]["compute"]
    t = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    xs, ys = zip(*[t.transform(x, y) for x in (b["west"], b["east"]) for y in (b["south"], b["north"])])
    x0, y1 = min(xs), max(ys); w = int((max(xs) - x0) / res); h = int((y1 - min(ys)) / res)
    return crs, from_origin(x0, y1, res, res), (h, w)

def write(path, arr, crs, transform):
    import rasterio
    with rasterio.open(path, "w", driver="GTiff", height=arr.shape[0], width=arr.shape[1], count=1, dtype="float32",
                       crs=crs, transform=transform, nodata=np.nan, compress="deflate") as d:
        d.write(arr.astype("float32"), 1)

def lst(cid, years):
    c = city(cid); b = c["bbox_core"]; bbox = [b["west"], b["south"], b["east"], b["north"]]
    items = search("landsat-c2-l2", bbox, years, 20, {"platform": {"in": ["landsat-8", "landsat-9"]}})
    print("landsat scenes", len(items)); tok = token("landsat-c2-l2")
    crs, tr, shape = grid(c, 30)
    stack, used = [], []
    for it in items:
        a = it["assets"]
        try:
            st = read_window(a["lwir11"]["href"] + "?" + tok, None, crs, 30, shape, tr)
            qa = read_window(a["qa_pixel"]["href"] + "?" + tok, None, crs, 30, shape, tr, "nearest")
        except Exception as e:
            print("  skip", it["id"], e); continue
        qa = np.nan_to_num(qa).astype("uint16")
        clear = ((qa & (1 << 6)) > 0) & ((qa & 0b11111) == 0)   # clear bit, no fill/dilated/cirrus/cloud
        k = st * 0.00341802 + 149.0 - 273.15
        k[~clear | (st <= 0)] = np.nan
        if np.isfinite(k).mean() < 0.3: continue
        stack.append(k); used.append(it["id"]); print("  ok", it["id"], round(float(np.nanmedian(k)), 1))
    comp = np.nanmedian(np.stack(stack), axis=0)
    out = city_dir(cid, "data", "layers", "L2_lst_summer_median.tif"); write(out, comp, crs, tr)
    manifest(cid, {"layer": "L2.lst_summer", "source": "S-011", "path": os.path.relpath(out, city_dir(cid)), "scenes": used,
                   "state": "Observed (composite)", "unit": "degC land SURFACE temperature, not air", "years": years})

def ndvi(cid, years):
    c = city(cid); b = c["bbox_core"]; bbox = [b["west"], b["south"], b["east"], b["north"]]
    items = search("sentinel-2-l2a", bbox, years, 15)
    print("sentinel-2 scenes", len(items)); tok = token("sentinel-2-l2a")
    crs, tr, shape = grid(c, 10)
    stack, used = [], []
    for it in items[:40]:
        a = it["assets"]
        try:
            r = read_window(a["B04"]["href"] + "?" + tok, None, crs, 10, shape, tr)
            n = read_window(a["B08"]["href"] + "?" + tok, None, crs, 10, shape, tr)
            scl = read_window(a["SCL"]["href"] + "?" + tok, None, crs, 10, shape, tr, "nearest")
        except Exception as e:
            print("  skip", it["id"], e); continue
        v = (n - r) / (n + r + 1e-6)
        v[~np.isin(np.nan_to_num(scl), [4, 5, 6])] = np.nan   # vegetation, bare, water
        if np.isfinite(v).mean() < 0.3: continue
        stack.append(v); used.append(it["id"])
    comp = np.nanmedian(np.stack(stack), axis=0)
    out = city_dir(cid, "data", "layers", "L2_ndvi_summer_median.tif"); write(out, comp, crs, tr)
    manifest(cid, {"layer": "L2.ndvi_summer", "source": "S-012", "path": os.path.relpath(out, city_dir(cid)), "scenes": used, "state": "Observed (composite)"})

if __name__ == "__main__":
    cid = sys.argv[1] if len(sys.argv) > 1 else "trebinje"
    what = sys.argv[2] if len(sys.argv) > 2 else "both"
    if what in ("lst", "both"): lst(cid, [2023, 2024, 2025])
    if what in ("ndvi", "both"): ndvi(cid, [2025])
