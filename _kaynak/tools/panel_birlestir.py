# -*- coding: utf-8 -*-
"""odeme.js'i panel.js'in sonuna ekler.

panel.js bir modul olarak yukleniyor; ayri dosya olsaydi kabuk(), sb, esc()
gibi ortak seyleri disari acmak gerekirdi. Tek dosyada tutmak daha basit.
Betik iki kez calistirilirsa ikinci kez hicbir sey yapmaz.
"""
import io
import os

Y = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(Y)
panel = os.path.join(KOK, "site", "admin", "panel.js")

# Her parca (dosya, icinde-varsa-ekleme nobetcisi) olarak tanimli.
PARCALAR = [
    ("panel-odeme-kaynak.js", "async function odemeSayfasi"),
    ("panel-analitik-kaynak.js", "async function analitikSayfasi"),
]

t = io.open(panel, encoding="utf-8").read()
for dosya, nobetci in PARCALAR:
    if nobetci in t:
        print("zaten eklenmis:", dosya)
        continue
    p = io.open(os.path.join(Y, dosya), encoding="utf-8").read()
    t = t.rstrip() + "\n\n" + p
    print("eklendi:", dosya, "(%d satir)" % p.count("\n"))
io.open(panel, "w", encoding="utf-8", newline="\n").write(t)
