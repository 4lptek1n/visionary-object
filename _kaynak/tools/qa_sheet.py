# -*- coding: utf-8 -*-
"""Her ilan icin kontak sayfasi uretir: gozle denetim icin.

Ilk 56 ilan buyuk boy (4 ilan/sayfa, c kareler), gerisi 8 ilan/sayfa (t kareler).
Cikti: ayirma/qa_sheets/buyuk_NN.jpg ve kucuk_NN.jpg
Her satirda: VO-no | baslik | sanatci ve ilanin TUM kareleri rol etiketiyle.
"""
import json
import os
from PIL import Image, ImageDraw, ImageFont

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERI = json.load(open(os.path.join(KOK, "data", "ilanlar.json"), encoding="utf-8"))
IMG = os.path.join(KOK, "site")
CIKTI = os.path.join(KOK, "ayirma", "qa_sheets")
os.makedirs(CIKTI, exist_ok=True)

try:
    F = ImageFont.truetype("arial.ttf", 15)
    FK = ImageFont.truetype("arial.ttf", 12)
except Exception:
    F = ImageFont.load_default(); FK = F

ROLTR = {"tam": "TAM", "aci": "aci", "detay": "det", "imza": "IMZA",
         "sertifika": "SERT", "etiket": "etk", "plaka": "plk",
         "arka": "arka", "olcu": "OLCU"}


def yukle(temel, boy):
    yol = os.path.join(IMG, (temel + "-%s.webp" % boy).replace("/", os.sep))
    try:
        return Image.open(yol).convert("RGB")
    except Exception:
        im = Image.new("RGB", (160, 160), (200, 60, 60))
        ImageDraw.Draw(im).text((10, 70), "YOK", fill="white", font=F)
        return im


def sayfa_yap(grup, ad, kare_h, boy):
    genis = 1500
    satirlar = []
    for il in grup:
        n = len(il["kareler"])
        satirlar.append((il, n))
    yuk = sum(kare_h + 44 for _ in satirlar) + 10
    tuval = Image.new("RGB", (genis, yuk), (244, 242, 227))
    ciz = ImageDraw.Draw(tuval)
    y = 6
    for il, n in satirlar:
        baslik = "VO-%02d  %s  |  %s  |  %s" % (
            il["no"], il["slug"], (il.get("sanatci") or "-")[:30], (il["baslik"] or "")[:70])
        ciz.text((8, y), baslik, fill=(20, 20, 20), font=F)
        y += 22
        x = 8
        for k in il["kareler"]:
            im = yukle(k["temel"], boy)
            oran = kare_h / im.height
            w = max(40, int(im.width * oran))
            im = im.resize((w, kare_h))
            if x + w > genis - 8:
                break
            tuval.paste(im, (x, y))
            ciz.rectangle([x, y + kare_h - 16, x + 44, y + kare_h], fill=(20, 20, 20))
            ciz.text((x + 3, y + kare_h - 15), ROLTR.get(k["rol"], k["rol"])[:5],
                     fill=(244, 242, 227), font=FK)
            x += w + 6
        y += kare_h + 22
    tuval.save(os.path.join(CIKTI, ad), quality=72)


buyukler = [il for il in VERI if il["no"] <= 56]
kucukler = [il for il in VERI if il["no"] > 56]

s = 0
for i in range(0, len(buyukler), 4):
    s += 1
    sayfa_yap(buyukler[i:i+4], "buyuk_%02d.jpg" % s, 230, "c")
print("buyuk sayfa:", s)

s = 0
for i in range(0, len(kucukler), 8):
    s += 1
    sayfa_yap(kucukler[i:i+8], "kucuk_%02d.jpg" % s, 130, "t")
print("kucuk sayfa:", s)
