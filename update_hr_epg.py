#!/usr/bin/env python3
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

RS1_IDS = {
    "Nova.Series.rs",
}

OUT_XML = Path("senoepg-hr.xml")
OUT_GZ = Path("senoepg-hr.xml.gz")

def fetch_root(url):
    req = urllib.request.Request(url, headers={"User-Agent": "SenoEPG-HR/1.0 (+GitHub Actions)"})
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

def add_from(root, keep_ids):
    for ch in root.findall("channel"):
        cid = ch.attrib.get("id", "")
        if cid in keep_ids and cid not in seen_channels:
            new_root.append(ch)
            seen_channels.add(cid)
    for p in root.findall("programme"):
        if p.attrib.get("channel", "") in keep_ids:
            new_root.append(p)

add_from(hr_root, HR1_IDS)
add_from(rs_root, RS1_IDS)

ET.indent(new_root, space="  ")
ET.ElementTree(new_root).write(OUT_XML, encoding="utf-8", xml_declaration=True)

with OUT_XML.open("rb") as src, gzip.open(OUT_GZ, "wb", compresslevel=9) as dst:
    dst.write(src.read())

print(f"Updated {OUT_XML} and {OUT_GZ}")
print(f"Channels: {len(seen_channels)}")
