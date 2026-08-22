#!/usr/bin/env python3
import copy
import gzip
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HR1_URL = "https://epgshare01.online/epgshare01/epg_ripper_HR1.xml.gz"
RS1_URL = "https://epgshare01.online/epgshare01/epg_ripper_RS1.xml.gz"

HR1_IDS = {
    'HTV1.HD.hr',
    'HTV2.HD.hr',
    'HTV3.HD.hr',
    'HTV4.HD.hr',
    'Nova.TV.HD.hr',
    'Nova.Family.hr',
    'Doma.TV.HD.hr',
    'Z1.hr',
    'RTL.HD.hr',
    'RTL.2.HD.hr',
    'RTL.Living.hr',
    'RTL.Crime.hr',
    'RTL.Passion.hr',
    'RTL.Adria.hr',
    'AXN.hr',
    'STAR.Channel.hr',
    'STAR.Life.hr',
    'STAR.Crime.hr',
    'STAR.Movies.hr',
    'Klasik.TV.hr',
    'HBO.HD.hr',
    'HBO.2.HD.hr',
    'HBO.3.HD.hr',
    'CineStar.TV.1.hr',
    'CineStar.TV.Action.and.Thriller.hr',
    'CineStar.TV.Premiere.1.HD.hr',
    'CineStar.TV.Premiere.2.HD.hr',
    'CineStar.TV.Comedy.and.Family.hr',
    'CineStar.TV.Fantasy.hr',
    'Cinemax.HD.hr',
    'Cinemax.2.HD.hr',
    'Kino.TV.HD.hr',
    'Epic.Drama.hr',
    'DIVA.hr',
    'Doku.TV.HD.hr',
    'Discovery.Channel.hr',
    'National.Geographic.hr',
    'National.Geographic.Wild.hr',
    'Viasat.History.hr',
    'Viasat.Nature.hr',
    '24Kitchen.hr',
    'BBC.Earth.hr',
    'TLC.hr',
    'E!.hr',
    'HGTV.hr',
    'Laudato.TV.hr',
    'Osjeèka.TV.hr',
    'Slavonska.TV.hr',
    'Plava.Vinkovacka.hr',
    'MrezaZG.hr',
    'TV.Jadran.hr',
    'Televizija.Dalmacija.hr',
    'Klape.i.Tambure.hr',
    'Libertas.TV.hr',
    'RTV.Banovina.hr',
    'Nickelodeon.hr',
    'RTL.Kockica.HD.hr',
    'Nick.Jr.HR.hr',
    'MTV.hr',
    'Jugoton.hr',
    'CMC.hr',
}

RS1_SOURCE_ID = "Nova.Series.rs"
RS1_ALIAS_ID = "Nova.Serije.hr"

OUT_XML = Path("senoepg-hr.xml")
OUT_GZ = Path("senoepg-hr.xml.gz")

def fetch_root(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "SenoEPG-HR/1.1 (+GitHub Actions)"}
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        data = r.read()
    return ET.fromstring(gzip.decompress(data))

hr_root = fetch_root(HR1_URL)
rs_root = fetch_root(RS1_URL)

new_root = ET.Element(
    "tv",
    {
        "generator-info-name": "SenoEPG HR - HR1 plus selected RS1",
        "generator-info-url": "https://epgshare01.online/",
    },
)

seen_channels = set()

for ch in hr_root.findall("channel"):
    cid = ch.attrib.get("id", "")
    if cid in HR1_IDS and cid not in seen_channels:
        new_root.append(copy.deepcopy(ch))
        seen_channels.add(cid)

for p in hr_root.findall("programme"):
    if p.attrib.get("channel", "") in HR1_IDS:
        new_root.append(copy.deepcopy(p))

for ch in rs_root.findall("channel"):
    if ch.attrib.get("id", "") == RS1_SOURCE_ID:
        cloned = copy.deepcopy(ch)
        cloned.set("id", RS1_ALIAS_ID)

        names = cloned.findall("display-name")
        if names:
            names[0].text = "Nova Serije"

        new_root.append(cloned)
        seen_channels.add(RS1_ALIAS_ID)
        break

for p in rs_root.findall("programme"):
    if p.attrib.get("channel", "") == RS1_SOURCE_ID:
        cloned = copy.deepcopy(p)
        cloned.set("channel", RS1_ALIAS_ID)
        new_root.append(cloned)

ET.indent(new_root, space="  ")
ET.ElementTree(new_root).write(
    OUT_XML,
    encoding="utf-8",
    xml_declaration=True
)

with OUT_XML.open("rb") as src, gzip.open(OUT_GZ, "wb", compresslevel=9) as dst:
    dst.write(src.read())

print(f"Updated {OUT_XML} and {OUT_GZ}")
print(f"Channels: {len(seen_channels)}")
print(f"Nova Serije alias: {RS1_SOURCE_ID} -> {RS1_ALIAS_ID}")
