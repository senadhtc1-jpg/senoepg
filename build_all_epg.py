#!/usr/bin/env python3
import copy
import gzip
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

SOURCES = {
    "BA": "https://epgshare01.online/epgshare01/epg_ripper_BA1.xml.gz",
    "HR": "https://epgshare01.online/epgshare01/epg_ripper_HR1.xml.gz",
    "RS": "https://epgshare01.online/epgshare01/epg_ripper_RS1.xml.gz",
}

OUT_XML = Path("senoepg-all.xml")
OUT_GZ = Path("senoepg-all.xml.gz")

def fetch_root(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "SenoEPG-ALL/1.0 (+GitHub Actions)"}
    )
    with urllib.request.urlopen(req, timeout=240) as r:
        data = r.read()
    return ET.fromstring(gzip.decompress(data))

new_root = ET.Element(
    "tv",
    {
        "generator-info-name": "SenoEPG ALL BA+HR+RS",
        "generator-info-url": "https://epgshare01.online/",
    },
)

counts = {}

for country, url in SOURCES.items():
    root = fetch_root(url)
    channel_count = 0
    programme_count = 0

    for ch in root.findall("channel"):
        old_id = ch.attrib.get("id", "")
        if not old_id:
            continue
        c = copy.deepcopy(ch)
        c.set("id", f"{country}_{old_id}")
        new_root.append(c)
        channel_count += 1

    for p in root.findall("programme"):
        old_id = p.attrib.get("channel", "")
        if not old_id:
            continue
        q = copy.deepcopy(p)
        q.set("channel", f"{country}_{old_id}")
        new_root.append(q)
        programme_count += 1

    counts[country] = (channel_count, programme_count)

# Posebno potvrđeni alias za Nova BH:
# BA izvor koristi Nova.BH.HD.(BIH).ba, ali u testu 108.ba radi.
nova_source = "BA_Nova.BH.HD.(BIH).ba"
nova_alias = "BA_108.ba"

source_channel = None
for ch in new_root.findall("channel"):
    if ch.attrib.get("id") == nova_source:
        source_channel = ch
        break

if source_channel is not None:
    alias_ch = copy.deepcopy(source_channel)
    alias_ch.set("id", nova_alias)
    for dn in alias_ch.findall("display-name"):
        if dn.text:
            dn.text = "Nova BH"
    new_root.append(alias_ch)

    nova_programmes = []
    for p in new_root.findall("programme"):
        if p.attrib.get("channel") == nova_source:
            q = copy.deepcopy(p)
            q.set("channel", nova_alias)
            nova_programmes.append(q)
    new_root.extend(nova_programmes)

ET.indent(new_root, space="  ")
ET.ElementTree(new_root).write(OUT_XML, encoding="utf-8", xml_declaration=True)

with OUT_XML.open("rb") as src, gzip.open(OUT_GZ, "wb", compresslevel=9) as dst:
    dst.write(src.read())

print("Created:", OUT_XML)
print("Created:", OUT_GZ)
for country, (channels, programmes) in counts.items():
    print(f"{country}: {channels} channels, {programmes} programmes")
print("Nova BH alias added:", nova_alias)
