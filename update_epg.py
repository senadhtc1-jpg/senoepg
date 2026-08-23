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

# EPGShare koristi stari ID za Nova BH.
# U našem SenoEPG-u ga pretvaramo u 108.ba
ID_REMAP = {
    'Nova.BH.HD.(BIH).ba': '108.ba',
}

OUT_XML = Path("senoepg-bih.xml")
OUT_GZ = Path("senoepg-bih.xml.gz")

req = urllib.request.Request(
    SOURCE_URL,
    headers={"User-Agent": "SenoEPG-BiH/1.0 (+GitHub Actions)"}
)

with urllib.request.urlopen(req, timeout=120) as response:
    compressed = response.read()

xml_bytes = gzip.decompress(compressed)
source_root = ET.fromstring(xml_bytes)

new_root = ET.Element(
    "tv",
    {
        "generator-info-name": "SenoEPG BiH PRAVI - filtered EPGShare BA1",
        "generator-info-url": "https://epgshare01.online/",
    },
)

channel_count = 0
programme_count = 0

# Kanali
for channel in source_root.findall("channel"):
    source_id = channel.attrib.get("id")

    if source_id in KEEP_IDS:
        new_channel = copy.deepcopy(channel)

        # Nova BH: stari ID -> 108.ba
        new_channel.attrib["id"] = ID_REMAP.get(source_id, source_id)

        new_root.append(new_channel)
        channel_count += 1

# Programski raspored
for programme in source_root.findall("programme"):
    source_id = programme.attrib.get("channel")

    if source_id in KEEP_IDS:
        new_programme = copy.deepcopy(programme)

        # Nova BH program također mora koristiti 108.ba
        new_programme.attrib["channel"] = ID_REMAP.get(source_id, source_id)

        new_root.append(new_programme)
        programme_count += 1

ET.indent(new_root, space="  ")
tree = ET.ElementTree(new_root)
tree.write(OUT_XML, encoding="utf-8", xml_declaration=True)

with OUT_XML.open("rb") as src, gzip.open(OUT_GZ, "wb", compresslevel=9) as dst:
    dst.write(src.read())

print(f"Updated {OUT_XML}: {channel_count} channels, {programme_count} programme entries")
print(f"Updated {OUT_GZ}")
print("Nova BH EPG ID: 108.ba")
