# -*- coding: utf-8 -*-
"""odeme.js'i panel.js'in sonuna ekler.

panel.js bir modul olarak yukleniyor; ayri dosya olsaydi kabuk(), sb, esc()
gibi ortak seyleri disari acmak gerekirdi. Tek dosyada tutmak daha basit.
Betik iki kez calistirilirsa ikinci kez hicbir sey yapmaz.
"""
import io
import os

Y = os.path.dirname(os.path.abspath(__file__))
panel = os.path.join(Y, "panel.js")
parca = os.path.join(Y, "odeme.js")

t = io.open(panel, encoding="utf-8").read()
if "async function odemeSayfasi" in t:
    print("zaten eklenmis")
else:
    p = io.open(parca, encoding="utf-8").read()
    io.open(panel, "w", encoding="utf-8", newline="\n").write(t.rstrip() + "\n\n" + p)
    print("eklendi: %d satir" % p.count("\n"))
