# -*- coding: utf-8 -*-
"""3B muzenin katalogu, sitenin kendi verisinden uretilir.

Muze bir sus: kendi verisi yok, kendi fiyati yok, kendi gorseli yok.
Duvarlarindaki her eser sitedeki bir ilandir; basligi, sanatcisi, teknigi,
olcusu ve fotografi build_en.js_rows() ciktisindan gelir.

Muzenin mimarisi sabit sayida yuva tasiyor:
  T1 SALON DUVARI  12 yuva
  T2 GALERI NISI    8 yuva
  T3 VITRIN         6 yuva
  T4 APSIS          3 yuva
Toplam 29. Hangi ilanin hangi yuvaya girdigi asagidaki kurala gore secilir.
"""
import json

SLOTS = {"T1": 12, "T2": 8, "T3": 6, "T4": 3}


def _cm(inches):
    return round(inches * 2.54)


def build(rows):
    ok = [d for d in rows if d.get("img") and d.get("dims")]

    def cover(d):
        """Sitenin kapak kuralinin aynisi: ilanin ilk karesi.
        Muzede ilanin kapak fotografi disinda bir kare asilmaz."""
        return d.get("cov") or d["img"][0]

    def temiz_kapak(d):
        return cover(d)["src"] in ("temiz", "kirpilmis")

    def height(d):
        return d["dims"][1]

    # T4 apsis: belgesi ve adi olan en buyuk uc eser
    def weight(d):
        return (2 if d["doc"] else 0) + (1 if d["creator"] else 0)

    rest = sorted(ok, key=lambda d: (0 if temiz_kapak(d) else 1, -weight(d), -height(d)))
    t4 = rest[:SLOTS["T4"]]
    rest = [d for d in rest if d not in t4]

    # T3 vitrin: el yapimi objeler, belgeler ve en kucuk isler
    rest.sort(key=lambda d: (0 if temiz_kapak(d) else 1,
                             0 if d["cat"] in ("obje", "belge") else 1, height(d)))
    t3 = rest[:SLOTS["T3"]]
    rest = [d for d in rest if d not in t3]

    # T2 galeri nisleri: kalanlarin en buyukleri
    rest.sort(key=lambda d: (0 if temiz_kapak(d) else 1, -height(d)))
    t2 = rest[:SLOTS["T2"]]
    rest = [d for d in rest if d not in t2]

    # T1 salon duvari
    t1 = rest[:SLOTS["T1"]]

    cat, img = [], {}
    for tier, group in (("T1", t1), ("T2", t2), ("T3", t3), ("T4", t4)):
        for d in group:
            w_in, h_in = d["dims"][0], d["dims"][1]
            c = cover(d)
            cat.append({
                "id": d["slug"],
                "t": d["title"],
                "a": d["creator"] or d["catEn"],
                "m": d["medium"] or ", ".join(d["medium2"][:2]) or "Mixed media",
                "e": d["period"] or {"18th-and-earlier": "18th century and earlier",
                                     "19th": "19th century", "20th": "20th century",
                                     "21st": "21st century"}.get(d["period2"], ""),
                "tier": tier,
                "w": _cm(w_in), "h": _cm(h_in),
                "inW": w_in, "inH": h_in,
                "ar": round(w_in / h_in, 4),
                "ref": "VO-%02d" % d["no"],
                "url": "../index.html#/item/" + d["slug"],
                "frame": "Unframed, stretched canvas" if "unframed" in d["framing"]
                         else "Frame included",
                "doc": d["doc"] or "",
                "shots": d["shots"],
            })
            img[d["slug"]] = "../" + c["f"]
    return cat, img


def js(rows):
    cat, img = build(rows)
    return ("/* Bu dosya build_en.py tarafindan uretilir. Elle duzenlemeyin. */\n"
            "const CATALOG=" + json.dumps(cat, ensure_ascii=False, separators=(",", ":")) +
            ";\nconst IMG=" + json.dumps(img, ensure_ascii=False, separators=(",", ":")) + ";\n")
