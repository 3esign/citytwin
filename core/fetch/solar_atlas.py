"""L2 irradiance: Global Solar Atlas v2 country GIS data (World Bank Group / Solargis, CC-BY-4.0).
Download endpoint as linked from the World Bank Data Catalog (dataset 0039603). One zip per country.
Extracts yearly GHI and DIF GeoTIFFs and clips them to the city's horizon bbox."""
import glob, json, os, sys, urllib.parse, zipfile
from common import city, city_dir, download, get, manifest

API = "https://api.globalsolaratlas.info/download/"

def pick(country):
    files = json.loads(get(API + urllib.parse.quote(country)))
    gis = [f["name"] for f in files if "GISdata" in f["name"] and "GEOTIFF" in f["name"].upper() and "LTAy" in f["name"]]
    if not gis: raise SystemExit(f"no GIS GeoTIFF package listed for {country}: {[f['name'] for f in files][:20]}")
    gis.sort(key=lambda n: (0 if "YearlyMonthly" in n else 1, n))
    return gis[0]

def main(cid, country="Bosnia and Herzegovina"):
    c = city(cid); hb = c["bbox_horizon"]
    raw = city_dir(cid, "data", "raw", "global_solar_atlas")
    name = pick(country); print("GSA package:", name)
    z = os.path.join(raw, name)
    h = download(API + urllib.parse.quote(country) + "/" + urllib.parse.quote(name), z)
    daily = "AvgDaily" in name
    manifest(cid, {"layer": "L2.irradiance.raw", "source": "S-010", "path": os.path.relpath(z, city_dir(cid)), "sha256": h, "package": name})
    with zipfile.ZipFile(z) as zf:
        names = zf.namelist(); print("\n".join(names[:40]))
        zf.extractall(os.path.join(raw, "unz"))
    import rasterio
    from rasterio.windows import from_bounds
    for var in ("GHI", "DIF", "PVOUT"):
        cands = [p for p in glob.glob(os.path.join(raw, "unz", "**", f"{var}*.tif"), recursive=True)]
        if not cands:
            print("  missing", var); continue
        with rasterio.open(cands[0]) as src:
            win = from_bounds(hb["west"], hb["south"], hb["east"], hb["north"], src.transform)
            arr = src.read(1, window=win).astype("float32"); tr = src.window_transform(win)
            if src.nodata is not None: arr[arr == src.nodata] = float("nan")
            if daily: arr = arr * 365.25   # daily averages -> yearly totals
            meta = src.meta.copy(); meta.update(height=arr.shape[0], width=arr.shape[1], transform=tr, compress="deflate", dtype="float32", nodata=float("nan"))
        out = city_dir(cid, "data", "layers", f"L2_gsa_{var.lower()}_yearly.tif")
        with rasterio.open(out, "w", **meta) as dst: dst.write(arr, 1)
        import numpy as np
        a = np.ma.masked_invalid(arr.astype("float64"))
        print(f"  {var}: min {a.min():.0f} max {a.max():.0f} mean {a.mean():.0f} (yearly total, kWh/m2 or kWh/kWp)")
        manifest(cid, {"layer": f"L2.gsa.{var}", "source": "S-010", "path": os.path.relpath(out, city_dir(cid)), "state": "Estimated",
                       "note": "long-term yearly total (1994/1999/2007-2018 model), ~250 m", "licence": "CC-BY-4.0, © 2019 The World Bank, Solar resource data: Solargis"})

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "trebinje", *(sys.argv[2:3]))
