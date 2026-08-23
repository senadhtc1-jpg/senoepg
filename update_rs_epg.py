#!/usr/bin/env python3
import copy
import gzip
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

RS1_URL = "https://epgshare01.online/epgshare01/epg_ripper_RS1.xml.gz"

ALIASES = {
    'Prva 1': 'Prva.HD.(RS).rs',
    'Prva Plus': 'Prva.plus.(RS).rs',
    'Prva Max': 'Prva.MAX.rs',
    'Prva World': 'Prva.World.(RS).rs',
    '10868': 'Prva.Life.rs',

    'RTS 1': 'RTS.1.HD.rs',
    'RTS 2': 'RTS.2.HD.rs',
    'RTS 3': 'RTS.3.HD.rs',
    'rts-drama': 'RTS.Drama.(RS).rs',
    'rts-kolo': 'RTS.Kolo.(RS).rs',
    'rts-trezor': 'RTS.Trezor.rs',
    'rts-zivot': 'RTS.Život.rs',

    'RTRS': 'RTRS.rs',
    'Nova S': 'NOVA.S.HD.(RS).rs',
    'n1-rs': 'N1.HD.(RS).rs',
    'k-cn-music': 'K::CN.Music.2.(RS).rs',

    'tv1000-balkan': 'Viasat.Kino.(RS).exTV1000.rs',
    'national-geographic': 'National.Geographic.HD.(RS).rs',
    'ng-wild-hd': 'Nat.Geo.Wild.HD.(RS).rs',
    'history-channel': 'History.HD.(RS).rs',
    'History 2 Channel': 'History.2.HD.rs',
    'discovery-europe': 'Discovery.Channel.HD.(RS).rs',
    'discovery-animal': 'Animal.Planet.HD.(RS).rs',
    'discovery-tlc': 'TLC.HD.(RS).rs',
    'grand-narodna-tv': 'Grand.(RS).rs',
}

OUT_XML = Path("senoepg-rs.xml")
OUT_GZ = Path("senoepg-rs.xml.gz")

req = urllib.request.Request(
    RS1_URL,
    headers={"User-Agent": "SenoEPG-RS/2.0 (+GitHub Actions)"}
)
with urllib.request.urlopen(req, timeout=180) as r:
    root = ET.fromstring(gzip.decompress(r.read()))

channels = {c.attrib.get("id", ""): c for c in root.findall("channel")}
programmes = list(root.findall("programme"))
existing = set(channels)

for alias_id, source_id in ALIASES.items():
    if alias_id in existing:
        continue
    src_ch = channels.get(source_id)
    if src_ch is None:
        print(f"WARNING: nema izvornog kanala za alias {alias_id} -> {source_id}")
        continue

    ch = copy.deepcopy(src_ch)
    ch.set("id", alias_id)
    root.append(ch)
    existing.add(alias_id)

    for p in programmes:
        if p.attrib.get("channel") == source_id:
            cp = copy.deepcopy(p)
            cp.set("channel", alias_id)
            root.append(cp)

root.set("generator-info-name", "SenoEPG RS - original M3U compatible")

ET.indent(root, space="  ")
ET.ElementTree(root).write(OUT_XML, encoding="utf-8", xml_declaration=True)

with OUT_XML.open("rb") as src, gzip.open(OUT_GZ, "wb", compresslevel=9) as dst:
    dst.write(src.read())

print(f"Updated {OUT_XML} and {OUT_GZ}")
print(f"Channels: {len(root.findall('channel'))}")
print(f"Programmes: {len(root.findall('programme'))}")
