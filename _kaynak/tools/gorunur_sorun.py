# -*- coding: utf-8 -*-
"""metin_rapor.json'dan yalnizca sitede GORUNUR alanlardaki sorunlari doker."""
import json, os
KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
r = json.load(open(os.path.join(KOK, "tools", "metin_rapor.json"), encoding="utf-8"))
gorunur = [x for x in r if any(a != "aciklama_not" for a, _ in x["sorunlar"])]
print("GORUNUR ALANDA SORUNLU:", len(gorunur))
for x in gorunur:
    for a, m in x["sorunlar"]:
        if a != "aciklama_not":
            print(x["slug"], "|", a, "|", m[:160].encode("ascii", "replace").decode())
