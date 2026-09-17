"""A5/A4 walk.tourism_parking.v0 — walking corridors between attractions and parking catchments.

Questions: "Where should tourist paths, facilities and parking go?"  "Where do we need parking?"
Evidence state: Estimated (network geometry is observed; flows are modelled, not counted).
Valid scale: street segment / neighbourhood.

Method
  1. Walking graph from Overture segments split at their connectors (motorways excluded),
     edge cost = length / 1.25 m/s (4.5 km/h), steps x1.5.
  2. Attractions: Overture places matched by name patterns in city.json (attractions_match),
     falling back to seed points; arrival points: bus station and parking areas.
  3. Corridor intensity: shortest paths between every pair (attraction, attraction) and
     (arrival, attraction); each path adds 1 to its segments  -> L4_walk_corridors.
  4. Parking catchment: walking minutes from the nearest parking to every node and building
     -> L4_parking_walk_minutes (buildings), share of centre floor area beyond 5 min.
"""
import json, math, os, re, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "fetch"))
from common import city, city_dir, jfield, manifest, now  # noqa: E402

SPEED = 1.25
EXCLUDE = {"motorway", "motorway_link"}
MATCH_DEFAULT_UNUSED = {
    "Stari grad (Kastel)": r"kastel|stari grad|стари град|каштел",
    "Arslanagića most": r"arslanagi|арсланаги",
    "Hercegovačka Gračanica": r"gra[čc]anica|грачаница|crkvina|црквина",
    "Manastir Tvrdoš": r"tvrdo[šs]|тврдош",
    "Trg slobode": r"trg slobode|трг слободе|platan",
    "Autobuska stanica": r"autobusk|аутобуск|bus station",
}

def build_graph(seg, crs):
    import networkx as nx
    from shapely.ops import substring
    G = nx.Graph(); edges = []
    for _, r in seg.iterrows():
        g = r.geometry
        if g is None or g.geom_type != "LineString": continue
        if r.get("subtype") not in (None, "road") or (r.get("class") in EXCLUDE): continue
        cuts = [0.0, 1.0]
        try:
            for c in json.loads(r["connectors"]) if isinstance(r.get("connectors"), str) else []:
                a = c.get("at")
                if a is not None: cuts.append(float(a))
        except Exception:
            pass
        cuts = sorted(set(round(x, 6) for x in cuts))
        L = g.length
        for a, b in zip(cuts[:-1], cuts[1:]):
            part = substring(g, a * L, b * L)
            if part.length < 0.5: continue
            p0, p1 = part.coords[0], part.coords[-1]
            u, v = (round(p0[0], 1), round(p0[1], 1)), (round(p1[0], 1), round(p1[1], 1))
            w = part.length / SPEED * (1.5 if r.get("class") == "steps" else 1.0)
            G.add_edge(u, v, t=w, seg=r["id"], cls=r.get("class"))
            edges.append((u, v, part, r["id"], r.get("class")))
    # keep the largest component
    comp = max(nx.connected_components(G), key=len)
    return G.subgraph(comp).copy(), edges

def main(cid):
    import geopandas as gpd, pandas as pd, networkx as nx
    from scipy.spatial import cKDTree
    c = city(cid); crs = c["crs"]["compute"]; L = city_dir(cid, "data", "layers")
    seg = gpd.read_file(os.path.join(L, "L0_segments.gpkg")).to_crs(crs)
    G, edges = build_graph(seg, crs)
    nodes = np.array(list(G.nodes)); tree = cKDTree(nodes); keys = list(G.nodes)
    def snap(x, y): return keys[tree.query([x, y])[1]]
    # attractions
    pl = gpd.read_file(os.path.join(L, "L0_places.gpkg")).to_crs(crs)
    def _txt(v):
        try: return json.dumps(json.loads(v) if isinstance(v, str) else v, ensure_ascii=False).lower()
        except Exception: return str(v).lower()
    pl["nm"] = pl["names"].map(_txt)
    pl["cat"] = pl["categories"].map(jfield).fillna("") if "categories" in pl else ""
    pl["bcat"] = pl["basic_category"].astype(str) if "basic_category" in pl else ""
    from pyproj import Transformer
    tf = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    att = []
    for A in c.get("attractions", []):
        sx, sy = tf.transform(*A["seed"])
        m = pl[pl.nm.str.contains(A["pattern"], regex=True, flags=re.I) & (pl.cat.isin(A["categories"]) | pl.bcat.isin(A["categories"]))]
        if len(m):
            pts = m.geometry.representative_point()
            dd = ((pts.x - sx) ** 2 + (pts.y - sy) ** 2) ** 0.5
            k = dd.idxmin()
            if dd[k] <= 1500:
                att.append((A["name"], pts[k].x, pts[k].y, f"overture ({m.loc[k, 'cat']}, {dd[k]:.0f} m from checked seed)", A.get("role", "attraction"))); continue
        att.append((A["name"], sx, sy, "seed: " + A.get("seed_source", "unverified"), A.get("role", "attraction")))
    # parking
    park = []
    for n in ("L0_land_use", "L0_infrastructure"):
        p = os.path.join(L, n + ".gpkg")
        if os.path.exists(p):
            g = gpd.read_file(p).to_crs(crs)
            cl = g["class"].astype(str) if "class" in g else pd.Series("", index=g.index)
            st = g["subtype"].astype(str) if "subtype" in g else pd.Series("", index=g.index)
            g = g[cl.str.contains("parking") | st.str.contains("parking")]
            park += [(n, geom.representative_point().x, geom.representative_point().y) for geom in g.geometry]
    catp = pl.get("categories", pd.Series("", index=pl.index)).astype(str).str.contains("parking")
    park += [("place", gg.x, gg.y) for gg in pl[catp].geometry.representative_point()]
    arrivals = [(f"parking {i}", x, y) for i, (_, x, y) in enumerate(park)]
    att_nodes = {a[0]: snap(a[1], a[2]) for a in att}
    # corridors
    use = {}
    targets = [a[0] for a in att if a[4] == "attraction"]
    sources = list(att_nodes.items()) + [(n, snap(x, y)) for n, x, y in arrivals[:60]]
    for sname, snode in sources:
        lengths, paths = nx.single_source_dijkstra(G, snode, weight="t", cutoff=3600)
        for t in targets:
            tn = att_nodes[t]
            if t == sname or tn not in paths: continue
            pth = paths[tn]
            for u, v in zip(pth[:-1], pth[1:]):
                k = frozenset((u, v))
                use[k] = use.get(k, 0) + 1
    rows = []
    for u, v, part, sid, cls in edges:
        n = use.get(frozenset((u, v)), 0)
        if n: rows.append({"segment": sid, "class": cls, "paths": n, "geometry": part})
    cor = gpd.GeoDataFrame(rows, crs=crs)
    # parking catchment
    pk_nodes = list({snap(x, y) for _, x, y in arrivals})
    dist = nx.multi_source_dijkstra_path_length(G, pk_nodes, weight="t", cutoff=3600) if pk_nodes else {}
    b = gpd.read_file(os.path.join(L, "L0_buildings.gpkg")).to_crs(crs)
    rp = b.geometry.representative_point()
    idx = tree.query(np.column_stack([rp.x, rp.y]))[1]
    b["walk_min_to_parking"] = [round(dist.get(keys[i], np.nan) / 60, 1) for i in idx]
    b["state"] = "Estimated"
    cx, cy = tf.transform(c["centre"]["lon"], c["centre"]["lat"])
    core = b[(rp.x - cx) ** 2 + (rp.y - cy) ** 2 < 800 ** 2]
    fa = core.geometry.area
    share_far = float(fa[core.walk_min_to_parking > 5].sum() / fa.sum()) if len(core) else None
    out = os.path.join(L, "L4_walk_v0")
    for name, gdf in (("_corridors", cor), ("_parking_minutes", b[[x for x in ["id", "class", "walk_min_to_parking", "state", "geometry"] if x in b]])):
        for ext, drv in ((".gpkg", "GPKG"), (".geojson", "GeoJSON")):
            fp = out + name + ext
            if os.path.exists(fp): os.remove(fp)
            gdf.to_crs("EPSG:4326").to_file(fp, driver=drv)
    pts = gpd.GeoDataFrame([{"name": a[0], "origin": a[3], "role": a[4]} for a in att], geometry=gpd.points_from_xy([a[1] for a in att], [a[2] for a in att]), crs=crs)
    pts.to_crs("EPSG:4326").to_file(out + "_attractions.geojson", driver="GeoJSON")
    pk = gpd.GeoDataFrame([{"source": a[0]} for a in park], geometry=gpd.points_from_xy([a[1] for a in park], [a[2] for a in park]), crs=crs)
    if len(pk): pk.to_crs("EPSG:4326").to_file(out + "_parking.geojson", driver="GeoJSON")
    summ = {"time": now(), "algorithm": "walk.tourism_parking.v0", "graph_nodes": G.number_of_nodes(), "graph_edges": G.number_of_edges(),
            "attractions": [{"name": a[0], "origin": a[3], "role": a[4]} for a in att], "parking_features": len(park),
            "centre_800m_floor_share_beyond_5min_of_parking": None if share_far is None else round(100 * share_far, 1),
            "top_corridor_segments": cor.groupby(["segment", "class"], as_index=False)["paths"].max().sort_values("paths", ascending=False).head(10).to_dict("records") if len(cor) else [],
            "state": "Estimated", "caveats": ["no counts: corridor intensity = number of shortest paths, not people",
                                              "parking = mapped parking areas only; street parking and zones (R4) missing",
                                              "attraction points come from name + category + distance to a checked seed; origin says which"]}
    json.dump(summ, open(out + "_summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    manifest(cid, {"layer": "L4.walk_v0", "algorithm": "A5/A4", "path": os.path.relpath(out + "_corridors.gpkg", city_dir(cid)), "state": "Estimated"})
    print(json.dumps(summ, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "trebinje")
