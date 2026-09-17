"""L0.c7 population grid and building height / built surface from the JRC Global Human Settlement
Layer (GHSL R2023A, 100 m, Mollweide tiles). Host serves no robots.txt; data CC-BY-4.0.
Outputs (EPSG of the city, 100 m): L0_pop_ghs2025.tif, L0_built_height_ghs2018.tif, L0_built_surface_ghs2020.tif"""
import glob, math, os, sys, zipfile
from common import city, city_dir, download, manifest

BASE = "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/"
PRODUCTS = {
    "L0_pop_ghs2025": "GHS_POP_GLOBE_R2023A/GHS_POP_E2025_GLOBE_R2023A_54009_100/V1-0/tiles/GHS_POP_E2025_GLOBE_R2023A_54009_100_V1_0_{t}.zip",
    "L0_built_height_ghs2018": "GHS_BUILT_H_GLOBE_R2023A/GHS_BUILT_H_AGBH_E2018_GLOBE_R2023A_54009_100/V1-0/tiles/GHS_BUILT_H_AGBH_E2018_GLOBE_R2023A_54009_100_V1_0_{t}.zip",
    "L0_built_surface_ghs2020": "GHS_BUILT_S_GLOBE_R2023A/GHS_BUILT_S_E2020_GLOBE_R2023A_54009_100/V1-0/tiles/GHS_BUILT_S_E2020_GLOBE_R2023A_54009_100_V1_0_{t}.zip",
}

def tiles(b):
    from pyproj import Transformer
    t = Transformer.from_crs("EPSG:4326", "ESRI:54009", always_xy=True)
    out = set()
    for lon in (b["west"], b["east"]):
        for lat in (b["south"], b["north"]):
            x, y = t.transform(lon, lat)
            out.add(f"R{int((9000000 - y) // 1e6) + 1}_C{int((x + 18041000) // 1e6) + 1}")
    return sorted(out)

def main(cid):
    import rasterio
    from rasterio.merge import merge
    from rasterio.warp import reproject, Resampling
    from rasterio.transform import from_origin
    from pyproj import Transformer
    import numpy as np
    c = city(cid); b = c["bbox_core"]; crs = c["crs"]["compute"]
    raw = city_dir(cid, "data", "raw", "ghsl")
    tf = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    xs, ys = zip(*[tf.transform(x, y) for x in (b["west"], b["east"]) for y in (b["south"], b["north"])])
    x0, y1 = math.floor(min(xs) / 100) * 100, math.ceil(max(ys) / 100) * 100
    w, h = int((max(xs) - x0) // 100) + 1, int((y1 - min(ys)) // 100) + 1
    dst_tr = from_origin(x0, y1, 100, 100)
    for lid, pat in PRODUCTS.items():
        srcs = []
        for t in tiles(b):
            url = BASE + pat.format(t=t)
            z = os.path.join(raw, os.path.basename(url))
            hsh = download(url, z)
            manifest(cid, {"layer": lid + ".raw", "source": "S-013", "url": url, "path": os.path.relpath(z, city_dir(cid)), "sha256": hsh})
            ud = z[:-4]
            if not glob.glob(os.path.join(ud, "*.tif")):
                with zipfile.ZipFile(z) as zf: zf.extractall(ud)
            srcs += glob.glob(os.path.join(ud, "*.tif"))
        ds = [rasterio.open(s) for s in srcs]
        arr, tr = merge(ds) if len(ds) > 1 else (ds[0].read(), ds[0].transform)
        nod = ds[0].nodata
        out = np.full((h, w), np.nan, dtype="float32")
        src = arr[0].astype("float32")
        if nod is not None: src[src == nod] = np.nan
        reproject(src, out, src_transform=tr, src_crs=ds[0].crs, dst_transform=dst_tr, dst_crs=crs,
                  resampling=Resampling.nearest, src_nodata=np.nan, dst_nodata=np.nan)
        for d in ds: d.close()
        p = city_dir(cid, "data", "layers", lid + ".tif")
        with rasterio.open(p, "w", driver="GTiff", height=h, width=w, count=1, dtype="float32", crs=crs,
                           transform=dst_tr, nodata=np.nan, compress="deflate") as d:
            d.write(out, 1)
        print(f"  {lid}: sum {np.nansum(out):.0f} max {np.nanmax(out):.1f}")
        manifest(cid, {"layer": lid, "source": "S-013", "path": os.path.relpath(p, city_dir(cid)), "state": "Estimated (modelled grid)",
                       "note": "100 m, nearest resampling from Mollweide; values per cell", "licence": "CC-BY-4.0, European Commission JRC GHSL R2023A"})

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "trebinje")
