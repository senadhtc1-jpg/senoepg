#!/usr/bin/env python3
import gzip
import urllib.request
from pathlib import Path

RS1_URL = "https://epgshare01.online/epgshare01/epg_ripper_RS1.xml.gz"

OUT_XML = Path("senoepg-rs.xml")
OUT_GZ = Path("senoepg-rs.xml.gz")

def download(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "SenoEPG-RS/1.0 (+GitHub Actions)"}
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()

data_gz = download(RS1_URL)
xml_data = gzip.decompress(data_gz)

OUT_XML.write_bytes(xml_data)
OUT_GZ.write_bytes(data_gz)

print(f"Updated {OUT_XML} and {OUT_GZ}")
print(f"XML size: {len(xml_data):,} bytes")
