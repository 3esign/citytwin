"""L0 acceptance numbers for a city pack. Writes cities/<id>/data/L0_REPORT.md (+ .json)."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "fetch"))
from common import city, city_dir, now

def main(cid):
    import geopandas as gpd, networkx as nx, rasterio, numpy as np
    c = city(cid); L = city_dir(cid, "data", "layers"); crs = c["crs"]["compute"]
    rep = {"city": cid, "time": now()}
    def load(n):
        p = os.path.join(L, n + ".gpkg")
        return gpd.read_file(p).to_crs(crs) if os.path.exists(p) else None
    b = load("L0_buildings")
    if b is not None:
        b["area"] = b.geometry.area
        rep["buildings"] = {
            "count": int(len(b)), "footprint_m2_total": round(float(b.area.sum())),
            "median_footprint_m2": round(float(b.area.median()), 1),
            "with_height_pct": round(100 * float(b["height"].notna().mean()), 1) if "height" in b else 0,
            "with_floors_pct": round(100 * float(b["num_floors"].notna().mean()), 1) if "num_floors" in b else 0,
            "by_source": b["sources"].astype(str).str.extract(r'"dataset":"([^"]+)"')[0].value_counts().to_dict() if "sources" in b else {},
            "by_class": b["class"].fillna("unknown").value_counts().head(15).to_dict() if "class" in b else {},
        }
    s = load("L0_segments")
    if s is not None:
        from shapely.geometry import box as _box
        bb = c["bbox_core"]
        clipbox = gpd.GeoSeries([_box(bb["west"], bb["south"], bb["east"], bb["north"])], crs="EPSG:4326").to_crs(crs).iloc[0]
        s["len"] = s.geometry.intersection(clipbox).length
        roads = s[s["subtype"] == "road"] if "subtype" in s else s
        rep["segments"] = {"count": int(len(s)), "km_total": round(float(s.len.sum()) / 1000, 1),
                           "km_by_class": (roads.groupby(roads["class"].fillna("unknown"))["len"].sum() / 1000).round(1).sort_values(ascending=False).head(15).to_dict()}
        # topology proxy: endpoints snapped to 1 m
        G = nx.Graph()
        for geom in roads.geometry:
            if geom is None or geom.geom_type != "LineString": continue
            a, z = geom.coords[0], geom.coords[-1]
            G.add_edge((round(a[0]), round(a[1])), (round(z[0]), round(z[1])))
        comps = sorted((len(x) for x in nx.connected_components(G)), reverse=True)
        rep["segments"]["graph_nodes"] = G.number_of_nodes()
        rep["segments"]["largest_component_share_pct"] = round(100 * comps[0] / max(1, sum(comps)), 1) if comps else 0
        rep["segments"]["note"] = "Overture segments split at connectors, so endpoint graph is a fair proxy; exact graph uses connectors"
    for n in ["L0_places", "L0_water", "L0_land_use", "L0_infrastructure", "L0_divisions", "L0_addresses", "L0_land"]:
        g = load(n)
        rep[n] = int(len(g)) if g is not None else None
    p = load("L0_places")
    if p is not None and "categories" in p:
        rep["places_top_categories"] = p["categories"].astype(str).str.extract(r'"primary":"([^"]+)"')[0].value_counts().head(20).to_dict()
    d = load("L0_divisions")
    if d is not None and "names" in d:
        m = d[d["names"].astype(str).str.contains("Trebinje|Требиње", regex=True)]
        rep["boundary_candidates"] = [{"subtype": r.get("subtype"), "area_km2": round(r.geometry.area / 1e6, 1)} for _, r in m.iterrows()]
    t = os.path.join(L, "L0_terrain_dem30_horizon.tif")
    if os.path.exists(t):
        with rasterio.open(t) as r:
            a = r.read(1, masked=True)
            rep["dem"] = {"shape": list(a.shape), "min": float(a.min()), "max": float(a.max()), "nodata_pct": round(100 * float(np.ma.getmaskarray(a).mean()), 2)}
    w = os.path.join(L, "L0_landcover_worldcover2021_core.tif")
    if os.path.exists(w):
        names = {10: "tree", 20: "shrub", 30: "grass", 40: "crop", 50: "built", 60: "bare", 70: "snow", 80: "water", 90: "wetland", 95: "mangrove", 100: "moss"}
        with rasterio.open(w) as r:
            a = r.read(1); vals, cnt = np.unique(a, return_counts=True)
            rep["landcover_pct"] = {names.get(int(v), str(v)): round(100 * float(k) / a.size, 1) for v, k in zip(vals, cnt)}
    out = city_dir(cid, "data", "L0_REPORT.json")
    json.dump(rep, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    md = ["# L0 report — " + cid, "", "Generated " + rep["time"], "", "```json", json.dumps(rep, ensure_ascii=False, indent=1), "```"]
    open(out.replace(".json", ".md"), "w", encoding="utf-8").write("\n".join(md))
    print(json.dumps(rep, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "trebinje")
