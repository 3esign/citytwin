"""L0 vector ground from Overture Maps (AWS open data): buildings, streets, water, land use,
infrastructure, places, administrative areas. Bbox-filtered reads with DuckDB; nothing else downloaded.
Outputs per theme: GeoPackage (GIS) + GeoJSON (web face), EPSG:4326."""
import os, sys, json
import duckdb
from common import city, city_dir, manifest, s3_list

BUCKET = "https://overturemaps-us-west-2.s3.amazonaws.com"
THEMES = {  # layer id -> (theme, type, wanted columns, extra WHERE)
    "L0_buildings":      ("buildings", "building",       ["id", "subtype", "class", "height", "num_floors", "roof_shape", "is_underground", "names", "sources"], ""),
    "L0_building_parts": ("buildings", "building_part",  ["id", "building_id", "height", "num_floors", "min_height"], ""),
    "L0_segments":       ("transportation", "segment",   ["id", "subtype", "class", "subclass", "names", "connectors", "road_surface", "speed_limits", "access_restrictions", "sources"], ""),
    "L0_connectors":     ("transportation", "connector", ["id"], ""),
    "L0_water":          ("base", "water",               ["id", "subtype", "class", "names", "is_intermittent"], ""),
    "L0_land_use":       ("base", "land_use",            ["id", "subtype", "class", "names", "surface"], ""),
    "L0_land":           ("base", "land",                ["id", "subtype", "class", "names", "elevation"], ""),
    "L0_infrastructure": ("base", "infrastructure",      ["id", "subtype", "class", "names", "surface"], ""),
    "L0_places":         ("places", "place",             ["id", "names", "categories", "basic_category", "taxonomy", "confidence", "websites", "addresses", "sources"], ""),
    "L0_divisions":      ("divisions", "division_area",  ["id", "subtype", "class", "names", "country", "region", "admin_level", "division_id"], ""),
    "L0_addresses":      ("addresses", "address",        ["id", "number", "street", "unit", "postcode", "address_levels"], ""),
}

def latest_release():
    rel = [p.split("/")[1] for p in s3_list(BUCKET, "release/", "/")]
    return sorted(rel)[-1]

def main(cid, only=None):
    c = city(cid); b = c["bbox_core"]
    rel = latest_release(); print("Overture release", rel)
    con = duckdb.connect()
    con.execute("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs; SET s3_region='us-west-2';")
    out_dir = city_dir(cid, "data", "layers")
    for lid, (theme, typ, want, extra) in THEMES.items():
        if only and lid not in only: continue
        src = f"s3://overturemaps-us-west-2/release/{rel}/theme={theme}/type={typ}/*"
        try:
            cols = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM read_parquet('{src}', hive_partitioning=1) LIMIT 0").fetchall()]
        except Exception as e:
            print(f"  skip {lid}: {e}"); continue
        sel = []
        for w in want:
            if w not in cols: continue
            # nested values become JSON text so every GIS/web tool can read them
            sel.append(f'"{w}"')
        where = (f"bbox.xmin <= {b['east']} AND bbox.xmax >= {b['west']} AND "
                 f"bbox.ymin <= {b['north']} AND bbox.ymax >= {b['south']}") + (f" AND {extra}" if extra else "")
        tmp = f"t_{lid}"
        con.execute(f"CREATE OR REPLACE TABLE {tmp} AS SELECT {', '.join(sel)}, geometry FROM read_parquet('{src}', hive_partitioning=1) WHERE {where}")
        # flatten nested types to JSON strings
        for name, dtype, *_ in con.execute(f"DESCRIBE {tmp}").fetchall():
            if name != "geometry" and any(k in dtype for k in ("STRUCT", "[]", "MAP")):
                con.execute(f'ALTER TABLE {tmp} ALTER "{name}" TYPE VARCHAR USING CAST(to_json("{name}") AS VARCHAR)')
        gtype = con.execute(f"SELECT typeof(geometry) FROM {tmp} LIMIT 1").fetchone()
        geom = "geometry" if (gtype and str(gtype[0]).upper().startswith("GEOMETRY")) else "ST_GeomFromWKB(geometry)"
        n = con.execute(f"SELECT count(*) FROM {tmp}").fetchone()[0]
        print(f"  {lid}: {n} features")
        if n == 0:
            manifest(cid, {"layer": lid, "source": "S-001", "release": rel, "count": 0, "state": "Unavailable"}); continue
        others = ['"'+x[0]+'"' for x in con.execute(f"DESCRIBE {tmp}").fetchall() if x[0] != "geometry"]
        body = f"SELECT {', '.join(others)}, {geom} AS geom FROM {tmp}"
        gpkg = os.path.join(out_dir, f"{lid}.gpkg"); gj = os.path.join(out_dir, f"{lid}.geojson")
        for p in (gpkg, gj):
            if os.path.exists(p): os.remove(p)
        con.execute(f"COPY ({body}) TO '{gpkg}' WITH (FORMAT GDAL, DRIVER 'GPKG', SRS 'EPSG:4326')")
        con.execute(f"COPY ({body}) TO '{gj}' WITH (FORMAT GDAL, DRIVER 'GeoJSON', LAYER_CREATION_OPTIONS 'WRITE_BBOX=YES')")
        manifest(cid, {"layer": lid, "source": "S-001", "release": rel, "theme": f"{theme}/{typ}", "count": n,
                       "path": os.path.relpath(gpkg, city_dir(cid)), "state": "Observed",
                       "licence": "ODbL-1.0 (OSM-derived) / CDLA-Permissive-2.0; attribution: © OpenStreetMap contributors, Overture Maps Foundation"})
    con.close()

if __name__ == "__main__":
    cid = sys.argv[1] if len(sys.argv) > 1 else "trebinje"
    main(cid, set(sys.argv[2:]) or None)
