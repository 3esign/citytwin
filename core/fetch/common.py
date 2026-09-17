"""Shared helpers for source adapters. Every download is logged with sha256 and time."""
import hashlib, json, os, sys, time, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone

UA = "CityTwin-Research/0.1 (University Union - Nikola Tesla; contact poturaksemir@gmail.com)"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def city(city_id):
    with open(os.path.join(ROOT, "cities", city_id, "city.json"), encoding="utf-8") as f:
        return json.load(f)

def city_dir(city_id, *parts):
    p = os.path.join(ROOT, "cities", city_id, *parts)
    os.makedirs(p if not os.path.splitext(p)[1] else os.path.dirname(p), exist_ok=True)
    return p

def get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def s3_list(bucket_url, prefix, delimiter=None):
    """List keys (or common prefixes) of a public S3 bucket via the REST API."""
    ns = "{http://s3.amazonaws.com/doc/2006-03-01/}"
    out, token = [], None
    while True:
        q = f"?list-type=2&prefix={urllib.parse.quote(prefix)}"
        if delimiter: q += f"&delimiter={urllib.parse.quote(delimiter)}"
        if token: q += f"&continuation-token={urllib.parse.quote(token)}"
        root = ET.fromstring(get(bucket_url.rstrip("/") + "/" + q))
        tag = "CommonPrefixes" if delimiter else "Contents"
        key = "Prefix" if delimiter else "Key"
        out += [e.find(ns + key).text for e in root.iter(ns + tag)]
        t = root.find(ns + "NextContinuationToken")
        if t is None: return out
        token = t.text

def download(url, dest, retries=5):
    """Resumable-by-retry download to dest; returns sha256. Skips if dest exists."""
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return sha256(dest)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".part"
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f:
                while True:
                    b = r.read(1 << 20)
                    if not b: break
                    f.write(b)
            os.replace(tmp, dest)
            return sha256(dest)
        except Exception as e:
            print(f"  retry {i+1}/{retries} {url}: {e}", file=sys.stderr)
            time.sleep(5 * (i + 1))
    raise RuntimeError(f"download failed: {url}")

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def manifest(city_id, record):
    """Append one immutable line to cities/<id>/data/MANIFEST.jsonl."""
    record = {"time": now(), **record}
    p = city_dir(city_id, "data", "MANIFEST.jsonl")
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print("  manifest:", record.get("layer"), record.get("path"))

import urllib.parse  # noqa: E402  (used above)

def jfield(v, key="primary"):
    """Overture nested fields arrive as JSON text (GPKG) or dicts (GeoJSON); return v[key] or None."""
    if v is None: return None
    if isinstance(v, str):
        try: v = json.loads(v)
        except Exception: return None
    return v.get(key) if isinstance(v, dict) else None
