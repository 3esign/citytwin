"""Export layers for the City in its coordinate systems.

Republika Srpska (Zakon o premjeru i katastru, čl. 31–33; REFRS + SRPOS) moved to ETRS89 with the
UTM projection; for Trebinje that is ETRS89 / UTM zone 34N = EPSG:25834 (also our compute CRS).
Most municipal and cadastral archives are still in the old state system (DKS: Bessel ellipsoid,
Hermannskogel datum, Gauss-Krüger zone 6 = EPSG:3908 "MGI 1901 / Balkans zone 6").

Transformation ETRS89 -> DKS uses the EPSG operation whose area of use is Bosnia and Herzegovina
("MGI 1901 to ETRS89 (7)", 7-parameter, ~1 m). Without that choice PROJ may take the Croatian set
(checked 2026-09-17: first candidate was "(2) Croatia - onshore"), so it is selected explicitly. For cadastral-grade work the official RUGIPP transformation (grid/parameters)
must be requested (request list R2) and plugged in via --pipeline.
Usage: export_official.py <city> <layer.gpkg> [<layer2.gpkg> ...]  -> data/export/<name>_25834.gpkg, _8678.gpkg"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "fetch"))
from common import city_dir, manifest

TARGETS = {"25834": "EPSG:25834", "8678": "EPSG:8678"}   # 8678 = MGI 1901 / Balkans zone 6 (replaces deprecated 3908)

def bih_transformer(src="EPSG:25834", dst="EPSG:8678"):
    from pyproj.transformer import TransformerGroup
    tg = TransformerGroup(src, dst, always_xy=True)
    for t in tg.transformers:
        if t.area_of_use and t.area_of_use.name.startswith("Bosnia"):
            return t
    raise SystemExit("no Bosnia and Herzegovina operation available in PROJ for " + src + " -> " + dst)

def main(cid, layers, pipeline=None):
    import geopandas as gpd, shapely
    out_dir = city_dir(cid, "data", "export")
    for lay in layers:
        src = lay if os.path.isabs(lay) else city_dir(cid, "data", "layers", lay)
        g = gpd.read_file(src)
        name = os.path.splitext(os.path.basename(src))[0]
        for tag, epsg in TARGETS.items():
            p = os.path.join(out_dir, f"{name}_{tag}.gpkg")
            if os.path.exists(p): os.remove(p)
            if tag == "8678":
                t = bih_transformer()
                u = g.to_crs("EPSG:25834")
                u["geometry"] = shapely.transform(u.geometry.values, lambda xy: __import__("numpy").column_stack(t.transform(xy[:, 0], xy[:, 1])))
                out = u.set_crs(epsg, allow_override=True); op = t.description
            else:
                out = g.to_crs(epsg); op = "PROJ default (same datum family, exact)"
            out.to_file(p, driver="GPKG")
            manifest(cid, {"layer": f"export.{name}.{tag}", "path": os.path.relpath(p, city_dir(cid)), "crs": epsg, "operation": op,
                           "accuracy": "as source" if tag == "25834" else "~1 m (EPSG BiH 7-parameter); official RUGIPP transformation pending (R2)"})
            print("  ", p)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
