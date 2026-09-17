"""Build the public export of CityTwin (code, docs, minified layers for GitHub Pages).
Whitelist only: internal logs, knowledge notes, raw data and private links never leave.
Usage: python tools/export_public.py <city> <dest_dir>"""
import json, os, re, shutil, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WHITELIST = ["ARCHITECTURE.md", "PHASES.md", "requirements.txt", ".gitignore", "research", "core", "faces/serve.js",
             "tools/bootstrap.ps1", "tools/run.ps1", "tools/export_public.py"]
LAYERS = {  # file -> properties kept (None = all)
    "L0_land_use.geojson": ["subtype", "class"], "L0_water.geojson": ["subtype", "class"],
    "L0_segments.geojson": ["subtype", "class"], "L4_solar_v0.geojson": ["kwh_yr", "kwp", "irr_kwh_m2_yr", "beam_loss_pct", "is_public", "public_hint", "height_est", "state"],
    "L4_walk_v0_corridors.geojson": ["class", "paths"], "L4_walk_v0_parking_minutes.geojson": ["walk_min_to_parking", "state"],
    "L4_walk_v0_attractions.geojson": None, "L4_walk_v0_parking.geojson": None, "L4_heat_v0_cells.geojson": None,
}
JSONS = ["L4_solar_v0_summary.json", "L4_solar_v0_top_public.json", "L4_walk_v0_summary.json", "L4_heat_v0_summary.json", "L0Q_summary.json"]
SCRUB = [(re.compile(r"\(Semir: \"decide these yourself\"\)"), "(decided by the authors)"), (re.compile(r"Semir, 2026-09-17\."), "Authors, 2026-09-17.")]

def rnd(c):
    return [rnd(x) for x in c] if isinstance(c, list) and c and isinstance(c[0], list) else [round(v, 6) for v in c]

def copy(rel, dest):
    src = os.path.join(ROOT, rel); dst = os.path.join(dest, rel)
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    else:
        os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copy2(src, dst)

def main(cid, dest):
    os.makedirs(dest, exist_ok=True)
    for rel in WHITELIST: copy(rel, dest)
    for f in ("README.md", "LICENSE"):
        shutil.copy2(os.path.join(ROOT, "public", f), os.path.join(dest, f))
    p = os.path.join(dest, "PHASES.md"); s = open(p, encoding="utf-8").read()
    for rx, rep in SCRUB: s = rx.sub(rep, s)
    s = s.replace("`docs/PRESENTATION.md`", "the presentation")
    open(p, "w", encoding="utf-8").write(s)
    os.makedirs(os.path.join(dest, "cities", cid, "registry"), exist_ok=True)
    shutil.copy2(os.path.join(ROOT, "cities", cid, "city.json"), os.path.join(dest, "cities", cid, "city.json"))
    shutil.copy2(os.path.join(ROOT, "cities", cid, "registry", "sources.jsonl"), os.path.join(dest, "cities", cid, "registry", "sources.jsonl"))
    # Pages site
    docs = os.path.join(dest, "docs"); lay = os.path.join(docs, "layers"); os.makedirs(lay, exist_ok=True)
    html = open(os.path.join(ROOT, "faces", "web", "index.html"), encoding="utf-8").read()
    html = html.replace("location.origin + '/layers/' + p", "new URL('layers/' + p, location.href).href").replace("fetch('/layers/' + p", "fetch('layers/' + p")
    html = html.replace("<title>Digitalno Trebinje</title>", "<title>Digitalno Trebinje</title>\n<meta name=\"description\" content=\"CityTwin pilot for Trebinje — S. Poturak, D. Golubović Matić (University Union – Nikola Tesla). Contact: poturaksemir@gmail.com\">")
    html = html.replace("Svi rezultati modela su <b>procjene</b>, ne mjerenja.</div>",
                        "Svi rezultati modela su <b>procjene</b>, ne mjerenja.<br>Autori: doc. dr Semir Poturak, prof. dr Darinka Golubović Matić — Fakultet za menadžment u građevinarstvu, Univerzitet „Union – Nikola Tesla“. Kontakt: poturaksemir@gmail.com · <a href=\"https://github.com/3esign/citytwin\">GitHub</a></div>")
    open(os.path.join(docs, "index.html"), "w", encoding="utf-8").write(html)
    open(os.path.join(docs, ".nojekyll"), "w").close()
    src = os.path.join(ROOT, "cities", cid, "data", "layers")
    total = 0
    for f, keep in LAYERS.items():
        fp = os.path.join(src, f)
        if not os.path.exists(fp): print("missing", f); continue
        g = json.load(open(fp, encoding="utf-8"))
        feats = []
        for ft in g["features"]:
            if not ft.get("geometry"): continue
            pr = ft.get("properties") or {}
            if keep is not None: pr = {k: pr[k] for k in keep if k in pr and pr[k] is not None}
            ft = {"type": "Feature", "properties": pr, "geometry": {"type": ft["geometry"]["type"], "coordinates": rnd(ft["geometry"]["coordinates"])}}
            feats.append(ft)
        out = os.path.join(lay, f)
        json.dump({"type": "FeatureCollection", "features": feats}, open(out, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        total += os.path.getsize(out); print(f, len(feats), os.path.getsize(out))
    for f in JSONS:
        if os.path.exists(os.path.join(src, f)): shutil.copy2(os.path.join(src, f), os.path.join(lay, f))
    print("layers bytes", total)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
