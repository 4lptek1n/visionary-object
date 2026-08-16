# -*- coding: utf-8 -*-
"""Mevcut 270 ilani ve gorsellerini Supabase'e tasir. Bir kez calistirilir.

Calistirmadan once iki degeri kendi ortamina koy (bunlari ben gormem):

  Windows PowerShell:
    $env:SUPABASE_URL="https://xxxx.supabase.co"
    $env:SUPABASE_SERVICE_KEY="service_role anahtari"
    python tools\tasi.py

service_role anahtari veritabanindaki butun kurallari asar. Yalnizca kendi
bilgisayarinda ve GitHub Secrets icinde dursun; panele, siteye, hicbir dosyaya
yazma.

Gorsel kaynagi olarak site/img altindaki 1400 px webp dosyalari kullanilir:
zaten dogru yonde, dogru kirpimda ve sitenin kullandigi en buyuk boy o.
"""
import json
import os
import sys
import time
import urllib.request

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJE = os.environ.get("VO_PROJE", os.path.dirname(KOK))
URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

if not URL or not KEY:
    sys.exit("SUPABASE_URL ve SUPABASE_SERVICE_KEY ortam degiskenlerini ayarla.")


def istek(yol, yontem="GET", govde=None, tur="application/json", ek=None):
    r = urllib.request.Request(URL + yol, method=yontem)
    r.add_header("apikey", KEY)
    r.add_header("Authorization", "Bearer " + KEY)
    r.add_header("Content-Type", tur)
    for k, v in (ek or {}).items():
        r.add_header(k, v)
    veri = govde if isinstance(govde, (bytes, type(None))) else json.dumps(govde).encode()
    with urllib.request.urlopen(r, veri, timeout=120) as c:
        ham = c.read()
    return json.loads(ham) if ham and tur == "application/json" else ham


def ilan_kaydi(x):
    o = x.get("olcu") or {}
    f = x.get("facet") or {}
    return {
        "no": x["no"], "slug": x["slug"], "kat": x.get("kat", "tablo"),
        "durum": "yayinda" if x.get("yayinda", True) else "taslak",
        "baslik": x.get("baslik", ""), "aciklama": x.get("aciklama", ""),
        "sanatci": x.get("sanatci", ""), "eser_adi": x.get("eser_adi", ""),
        "donem": x.get("donem", ""), "teknik": x.get("teknik", ""),
        "baski": x.get("baski", ""), "ref": x.get("ref", ""),
        "galeri_adi": x.get("galeri_adi", ""), "etiket": x.get("etiket", ""),
        "biyografi": x.get("biyografi", ""), "aciklama_not": x.get("not", ""),
        "belge": x.get("belge", ""), "kaynak_dosya": x.get("kaynak_dosya", ""),
        "olcu_w": o.get("w"), "olcu_h": o.get("h"), "olcu_nesi": o.get("nesi") or "outside of frame",
        "fiyat": x.get("fiyat"), "para_birimi": "USD", "fiyat_gizli": True,
        "facet": {"subject": f.get("subject", []), "medium": f.get("medium", []),
                  "style": f.get("style", []), "framing": f.get("framing", []),
                  "period": f.get("period", ""), "color": f.get("color", [])},
    }


def main():
    veri = json.load(open(os.path.join(PROJE, "data", "ilanlar.json"), encoding="utf-8"))
    print("okunan ilan:", len(veri))

    print("ilanlar yaziliyor...")
    for i in range(0, len(veri), 50):
        parca = [ilan_kaydi(x) for x in veri[i:i + 50]]
        istek("/rest/v1/ilanlar", "POST", parca,
              ek={"Prefer": "resolution=merge-duplicates,return=minimal"})
        print("  %d / %d" % (min(i + 50, len(veri)), len(veri)))

    kimlik = {}
    for i in range(0, len(veri), 200):
        nolar = ",".join(str(x["no"]) for x in veri[i:i + 200])
        for r in istek("/rest/v1/ilanlar?select=id,no,slug&no=in.(%s)" % nolar):
            kimlik[r["no"]] = r["id"]

    print("gorseller yukleniyor (bu kisim uzun surer)...")
    t0, yuklenen, atlanan = time.time(), 0, 0
    kare_kayit = []
    for x in veri:
        ilan_id = kimlik.get(x["no"])
        if not ilan_id:
            print("  ATLANDI, id yok:", x["slug"]); continue
        for sira, k in enumerate(x.get("kareler", []), 1):
            ad = k["temel"].rsplit("/", 1)[-1]
            kaynak = os.path.join(PROJE, "site", k["temel"].replace("/", os.sep) + "-f.webp")
            if not os.path.exists(kaynak):
                atlanan += 1; continue
            yol = "%s/%s.webp" % (x["slug"], ad)
            with open(kaynak, "rb") as f:
                ham = f.read()
            try:
                istek("/storage/v1/object/gorseller/" + yol, "POST", ham,
                      tur="image/webp", ek={"x-upsert": "true", "Cache-Control": "31536000"})
                yuklenen += 1
            except Exception as e:
                print("  yukleme hatasi", yol, e); atlanan += 1; continue
            kare_kayit.append({"ilan_id": ilan_id, "sira": sira, "rol": k.get("rol", "detay"),
                               "yol": yol, "w": k.get("w"), "h": k.get("h"),
                               "kaynak": k.get("kaynak", "orijinal"), "alt_metin": ""})
        if len(kare_kayit) >= 200:
            istek("/rest/v1/kareler", "POST", kare_kayit, ek={"Prefer": "return=minimal"})
            kare_kayit = []
            print("  %d gorsel, %.0f sn" % (yuklenen, time.time() - t0))
    if kare_kayit:
        istek("/rest/v1/kareler", "POST", kare_kayit, ek={"Prefer": "return=minimal"})

    print("bitti. yuklenen gorsel: %d, atlanan: %d, sure %.0f sn" % (yuklenen, atlanan, time.time() - t0))
    print("simdi panele girip bir ilani ac; gorseller gorunuyorsa tasima tamamdir.")


if __name__ == "__main__":
    main()
