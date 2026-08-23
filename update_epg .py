#!/usr/bin/env python3
import copy
import gzip
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

SOURCE_URL = "https://epgshare01.online/epgshare01/epg_ripper_BA1.xml.gz"

KEEP_IDS = {
    'Alfa.(Sarajevo).ba',
    'Alternativna.TV.ba',
    'BHT.1.HD.ba',
    'BN.HD.(BIH).ba',
    'BN.Music.HD.(BIH).ba',
    'City.TV.HD.ba',
    'Face.HD.ba',
    'Federalna.TV.ba',
    'Hayat.2.ba',
    'Hayat.Folk.Box.ba',
    'Hayat.HD.ba',
    'Hayat.Music.Box.ba',
    'Hayatovci.ba',
    'Izvorna.TV.ba',
    'Kanal.6.ba',
    'MTV.Igman.HD.ba',
    'N1.HD.(BH)/(BIH).ba',
    'NTV.IC.Kakanj.ba',
    'Nova.BH.HD.(BIH).ba',
    'O.Kanal.HD.ba',
    'OBN.(BIH).ba',
    'Pink.BH.ba',
    'RTV.BIR.HD.ba',
    'RTV.HIT.ba',
    'RTV.Sana.ba',
    'RTV.TK.ba',
    'RTV.Visoko.ba',
    'RTV.Zenica.HD.ba',
    'RTV7.ba',
    'RTVHB.HD.ba',
    'Sevdah.TV.ba',
    'TV.Bugojno.ba',
    'TV.Sarajevo.HD.(BH).ba',
    'TV.Vogošća.HD.ba',
    'TV5.HD.(BH).ba',
    'Televizija.Hema.ba',
}

# Originalni tvg-id iz Senadove M3U -> pravi EPG ID.
ALIASES = {
    '108.ba': 'Nova.BH.HD.(BIH).ba',   # zadržava i već provjereni Nova BH ID
    'Hayat Plus': 'Hayat.2.ba',
    'hayat-music': 'Hayat.Music.Box.ba',
    'BiH BN': 'BN.HD.(BIH).ba',
    'n1': 'N1.HD.(BH)/(BIH).ba',
    'izvorna-tv': 'Izvorna.TV.ba',
}

OUT_XML = Path("senoepg-bih.xml")
OUT_GZ = Path("senoepg-bih.xml.gz")

req = urllib.request.Request(
    SOURCE_URL,
    headers={"User-Agent": "SenoEPG-BiH/2.0 (+GitHub Actions)"}
)
with urllib.request.urlopen(req, timeout=180) as response:
    source_root = ET.fromstring(gzip.decompress(response.read()))

new_root = ET.Element(
    "tv",
    {
        "generator-info-name": "SenoEPG BiH - original M3U compatible",
        "generator-info-url": "https://epgshare01.online/",
    },
)

for ch in source_root.findall("channel"):
    if ch.attrib.get("id") in KEEP_IDS:
        new_root.append(copy.deepcopy(ch))

for p in source_root.findall("programme"):
    if p.attrib.get("channel") in KEEP_IDS:
        new_root.append(copy.deepcopy(p))

def add_aliases(root, aliases):
    channels = {c.attrib.get("id", ""): c for c in root.findall("channel")}
    programmes = list(root.findall("programme"))
    existing = set(channels)

    for alias_id, source_id in aliases.items():
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

add_aliases(new_root, ALIASES)

ET.indent(new_root, space="  ")
ET.ElementTree(new_root).write(OUT_XML, encoding="utf-8", xml_declaration=True)

with OUT_XML.open("rb") as src, gzip.open(OUT_GZ, "wb", compresslevel=9) as dst:
    dst.write(src.read())

print(f"Updated {OUT_XML} and {OUT_GZ}")
print(f"Channels: {len(new_root.findall('channel'))}")
print(f"Programmes: {len(new_root.findall('programme'))}")
