"""L0.c2 terrain (Copernicus DEM GLO-30) and L0.c6 land cover (ESA WorldCover 2021) from AWS open data.
Downloads whole 1-degree / 3-degree tiles covering the city's horizon bbox, then clips with rasterio."""
import math, os, sys
from common import city, city_dir, download, manifest, s3_list

DEM_BUCKET = "https://copernicus-dem-30m.s3.amazonaws.com"
WC_BUCKET = "https://esa-worldcover.s3.eu-central-1.amazonaws.com"

def lat_tag(v): return ("N" if v >= 0 else "S") + f"{abs(v):02d}"
def lon_tag(v): return ("E" if v >= 0 else "W") + f"{abs(v):03d}"

def dem_tiles(b):
    for lat in range(math.floor(b["south"]), math.floor(b["north"]) + 1):
        for lon in range(math.floor(b["west"]), math.floor(b["east"]) + 1):
            name = f"Copernicus_DSM_COG_10_{lat_tag(lat)}_00_{lon_tag(lon)}_00_DEM"
            yield name, f"{DEM_BUCKET}/{name}/{name}.tif"

def wc_tiles(b):
    seen = set()
    for lat in range(math.floor(b["south"]), math.floor(b["north"]) + 1):
        for lon in range(math.floor(b["west"]), math.floor(b["east"]) + 1):
            la, lo = 3 * math.floor(lat / 3), 3 * math.floor(lon / 3)
            if (la, lo) in seen: continue
            seen.add((la, lo))
            name = f"ESA_WorldCover_10m_2021_v200_{lat_tag(la)}{lon_tag(lo)}_Map.tif"
            yield name, f"{WC_BUCKET}/v200/2021/map/{name}"

def clip(srcs, bbox, dest):
    import rasterio
    from rasterio.merge import merge
    ds = [rasterio.open(s) for s in srcs]
    arr, tr = merge(ds, bounds=(bbox["west"], bbox["south"], bbox["east"], bbox["north"]))
    meta = ds[0].meta.copy()
    meta.update(driver="GTiff", height=arr.shape[1], width=arr.shape[2], transform=tr,
                compress="deflate", tiled=True)
    with rasterio.open(dest, "w", **meta) as out:
        out.write(arr)
    for d in ds: d.close()

def main(cid):
    c = city(cid); hb = c["bbox_horizon"]; cb = c["bbox_core"]
    raw = city_dir(cid, "data", "raw")
    dem_raw = []
    for name, url in dem_tiles(hb):
        dest = os.path.join(raw, "copernicus_dem", name + ".tif")
        h = download(url, dest); dem_raw.append(dest)
        manifest(cid, {"layer": "L0.c2.raw", "source": "S-002", "url": url, "path": os.path.relpath(dest, city_dir(cid)), "sha256": h})
    out = city_dir(cid, "data", "layers", "L0_terrain_dem30_horizon.tif")
    clip(dem_raw, hb, out)
    manifest(cid, {"layer": "L0.c2", "source": "S-002", "path": os.path.relpath(out, city_dir(cid)), "state": "Observed", "note": "DSM (includes buildings/trees), 30 m, EPSG:4326"})
    wc_raw = []
    for name, url in wc_tiles(cb):
        dest = os.path.join(raw, "esa_worldcover", name)
        h = download(url, dest); wc_raw.append(dest)
        manifest(cid, {"layer": "L0.c6.raw", "source": "S-003", "url": url, "path": os.path.relpath(dest, city_dir(cid)), "sha256": h})
    out = city_dir(cid, "data", "layers", "L0_landcover_worldcover2021_core.tif")
    clip(wc_raw, cb, out)
    manifest(cid, {"layer": "L0.c6", "source": "S-003", "path": os.path.relpath(out, city_dir(cid)), "state": "Observed", "note": "10 m classes, 2021"})

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "trebinje")
