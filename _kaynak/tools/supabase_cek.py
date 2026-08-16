# -*- coding: utf-8 -*-
"""Supabase'deki veriyi cekip siteyi kurmaya hazir hale getirir.

GitHub Actions bunu calistirir; elle de calistirilabilir. Yaptigi is:
  1. ilanlar, kareler, sayfalar, ayarlar tablolarini okur
  2. eksik gorselleri Supabase deposundan indirip 190/640/1400 px webp uretir
  3. data/ilanlar.json, data/sayfalar.json, data/ayarlar.json yazar

Sonra build_en.py calisir ve siteyi bunlardan uretir. Ziyaretci hicbir zaman
Supabase'e baglanmaz; gordugu her sey statik dosyadir.
"""
import io
import json
import os
import sys
import urllib.error
import urllib.request

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJE = os.environ.get("VO_PROJE", KOK)
# Gorseller sitenin kokune yazilir. build_en.py ile ayni yeri gosterir:
# VO_CIKTI verilmisse orasi, verilmemisse proje icindeki site klasoru.
IMGKOK = os.environ.get("VO_CIKTI") or os.path.join(PROJE, "site")
URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
ANON = os.environ.get("SUPABASE_ANON_KEY", "")
EPOSTA = os.environ.get("SUPABASE_EPOSTA", "")
SIFRE = os.environ.get("SUPABASE_SIFRE", "")
SERVIS = os.environ.get("SUPABASE_SERVICE_KEY", "")
BOYUT = [("t", 190, 70), ("c", 640, 72), ("f", 1400, 72)]

if not URL:
    sys.exit("SUPABASE_URL gerekli.")


def _giris():
    """Okuma yetkisi icin jeton uretir.

    Tercih edilen yol: acik anon anahtari + bir yayinci hesabinin e-posta ve
    sifresi. Boylece butun kurallari asan service_role anahtarina hic gerek
    kalmaz; yayin akisi da sinirli yetkiyle calisir.

    service_role verilmisse o kullanilir; eski kurulumlar bozulmasin diye.
    """
    if SERVIS:
        return SERVIS, SERVIS
    if not (ANON and EPOSTA and SIFRE):
        sys.exit("SUPABASE_ANON_KEY, SUPABASE_EPOSTA ve SUPABASE_SIFRE gerekli "
                 "(ya da SUPABASE_SERVICE_KEY).")
    govde = json.dumps({"email": EPOSTA, "password": SIFRE}).encode()
    r = urllib.request.Request(URL + "/auth/v1/token?grant_type=password", govde)
    r.add_header("apikey", ANON)
    r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r, timeout=40) as c:
            d = json.loads(c.read())
    except urllib.error.HTTPError as e:
        sys.exit("Giris yapilamadi: %s %s" % (e.code, e.read()[:200]))
    return ANON, d["access_token"]


APIKEY, JETON = _giris()
KEY = JETON  # geriye donuk uyum


def tablo(ad, secim="*", sira=None, sayfa=1000):
    cikti, bas = [], 0
    while True:
        y = "%s/rest/v1/%s?select=%s" % (URL, ad, secim)
        if sira:
            y += "&order=" + sira
        r = urllib.request.Request(y)
        r.add_header("apikey", APIKEY)
        r.add_header("Authorization", "Bearer " + JETON)
        r.add_header("Range", "%d-%d" % (bas, bas + sayfa - 1))
        with urllib.request.urlopen(r, timeout=120) as c:
            parca = json.loads(c.read())
        cikti += parca
        if len(parca) < sayfa:
            return cikti
        bas += sayfa


def gorsel_indir(yol):
    r = urllib.request.Request("%s/storage/v1/object/gorseller/%s" % (URL, yol))
    r.add_header("apikey", APIKEY)
    r.add_header("Authorization", "Bearer " + JETON)
    with urllib.request.urlopen(r, timeout=180) as c:
        return c.read()


def webp_uret(ham, klasor, ad):
    from PIL import Image, ImageOps
    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
    except Exception:
        pass
    im = ImageOps.exif_transpose(Image.open(io.BytesIO(ham))).convert("RGB")
    os.makedirs(klasor, exist_ok=True)
    for etiket, cap, kal in BOYUT:
        c = im.copy()
        if max(c.size) > cap:
            c.thumbnail((cap, cap), Image.LANCZOS)
        c.save(os.path.join(klasor, "%s-%s.webp" % (ad, etiket)), "WEBP", quality=kal, method=5)
    return im.size


def kampanya_uygula(ilanlar, kampanyalar, simdi):
    """Her ilana uyan kampanyalari bulur, en iyisini uygular.

    Kurallar:
      - Kampanya aktif olacak ve tarih araligi tutacak.
      - Kapsam: hepsi / kategori / sanatci / secili ilan.
      - Birden fazla kampanya uyuyorsa once oncelik, esitse en buyuk indirim.
      - Indirimler ust uste binmez; tek kampanya uygulanir.
      - en_dusuk verilmisse fiyat onun altina inmez.
      - Satilmis ilana indirim islenmez.
    """
    uygun = []
    for k in kampanyalar:
        if not k.get("aktif"):
            continue
        if k.get("baslangic") and k["baslangic"] > simdi:
            continue
        if k.get("bitis") and k["bitis"] < simdi:
            continue
        uygun.append(k)
    if not uygun:
        return None

    def kapsiyor(k, il):
        kap, deger = k.get("kapsam"), k.get("kapsam_deger") or []
        if kap == "hepsi":
            return True
        if kap == "kategori":
            return il.get("kat") in deger
        if kap == "sanatci":
            return (il.get("sanatci") or "").strip() in deger
        if kap == "secili":
            return il.get("slug") in deger
        return False

    def indirimli(k, fiyat):
        yeni = fiyat - (fiyat * float(k["deger"]) / 100 if k["tur"] == "yuzde" else float(k["deger"]))
        if k.get("en_dusuk") is not None:
            yeni = max(yeni, float(k["en_dusuk"]))
        return max(0.0, round(yeni, 2))

    serit = None
    for il in ilanlar:
        il["_kampanya"] = None
        if il.get("fiyat") is None or il.get("fiyat_gizli") or il.get("durum") == "satildi":
            continue
        aday = [k for k in uygun if kapsiyor(k, il)]
        if not aday:
            continue
        fiyat = float(il["fiyat"])
        aday.sort(key=lambda k: (-int(k.get("oncelik") or 0), indirimli(k, fiyat)))
        k = aday[0]
        yeni = indirimli(k, fiyat)
        if yeni >= fiyat:
            continue
        il["_kampanya"] = {"ad": k["ad"], "rozet": k.get("rozet") or "",
                           "yuzde": round((1 - yeni / fiyat) * 100)}
        il["_eski_fiyat"] = fiyat
        il["fiyat"] = yeni

    for k in sorted(uygun, key=lambda x: -int(x.get("oncelik") or 0)):
        if k.get("serit_aktif") and (k.get("serit_metin") or "").strip():
            serit = {"aktif": True, "metin": k["serit_metin"],
                     "etiket": k.get("serit_etiket") or "",
                     "baglanti": "#/browse?offer=sale"}
            break
    return serit


def main():
    ilanlar = tablo("ilanlar", sira="no.asc")
    kareler = tablo("kareler", sira="ilan_id.asc,sira.asc")
    sayfalar = tablo("sayfalar")
    ayarlar = tablo("ayarlar")
    try:
        kampanyalar = tablo("kampanyalar")
    except Exception:
        kampanyalar = []          # tablo henuz yoksa kampanyasiz devam
    import datetime
    simdi = datetime.datetime.now(datetime.timezone.utc).isoformat()
    serit = kampanya_uygula(ilanlar, kampanyalar, simdi)
    indirimli_adet = sum(1 for i in ilanlar if i.get("_kampanya"))
    print("ilan %d, kare %d, kampanya %d, indirimli ilan %d"
          % (len(ilanlar), len(kareler), len(kampanyalar), indirimli_adet))

    kmap = {}
    for k in kareler:
        kmap.setdefault(k["ilan_id"], []).append(k)

    cikti, yeni = [], 0
    for il in ilanlar:
        if il["durum"] == "arsiv":
            continue
        slug = il["slug"]
        klasor = os.path.join(IMGKOK, "img", slug)
        kare_cikti = []
        for sira, k in enumerate(sorted(kmap.get(il["id"], []), key=lambda x: x["sira"]), 1):
            ad = "%02d" % sira
            # Tasimadan gelen kareler zaten site/img altinda duruyor; yol
            # dogrudan onlari gosterir, indirmeye gerek yok.
            if (k["yol"] or "").startswith("img/"):
                kare_cikti.append({"temel": k["yol"], "rol": k["rol"],
                                   "kaynak": k.get("kaynak") or "orijinal",
                                   "w": k.get("w") or 0, "h": k.get("h") or 0})
                continue
            son = os.path.join(klasor, "%s-f.webp" % ad)
            w, h = k.get("w"), k.get("h")
            if not os.path.exists(son):
                try:
                    w, h = webp_uret(gorsel_indir(k["yol"]), klasor, ad)
                    yeni += 1
                except Exception as e:
                    print("  gorsel alinamadi:", k["yol"], e)
                    continue
            kare_cikti.append({"temel": "img/%s/%s" % (slug, ad), "rol": k["rol"],
                               "kaynak": k.get("kaynak") or "orijinal",
                               "w": w or 0, "h": h or 0})
        if not kare_cikti:
            continue
        cikti.append({
            "no": il["no"], "slug": slug, "kat": il["kat"],
            "yayinda": il["durum"] in ("yayinda", "rezerve", "satildi"),
            "baslik": il["baslik"], "aciklama": il["aciklama"], "sanatci": il["sanatci"],
            "eser_adi": il["eser_adi"], "donem": il["donem"], "teknik": il["teknik"],
            "baski": il["baski"], "ref": il["ref"], "galeri_adi": il["galeri_adi"],
            "etiket": il["etiket"], "biyografi": il["biyografi"], "not": il["aciklama_not"],
            "belge": il["belge"], "kaynak_dosya": il["kaynak_dosya"],
            "olcu": ({"w": float(il["olcu_w"]), "h": float(il["olcu_h"]),
                      "nesi": il["olcu_nesi"] or "outside of frame"}
                     if il["olcu_w"] and il["olcu_h"] else None),
            "fiyat": float(il["fiyat"]) if il["fiyat"] is not None and not il["fiyat_gizli"] else None,
            "fiyat_eski": (float(il["_eski_fiyat"]) if il.get("_eski_fiyat")
                           else (float(il["fiyat_eski"]) if il.get("fiyat_eski") else None)),
            "kampanya": il.get("_kampanya"),
            "para_birimi": il.get("para_birimi") or "USD",
            "satildi": il["durum"] == "satildi", "rezerve": il["durum"] == "rezerve",
            "one_cikan": bool(il.get("one_cikan")),
            "facet": il["facet"], "kareler": kare_cikti,
        })

    veri = os.path.join(PROJE, "data")
    os.makedirs(veri, exist_ok=True)
    with open(os.path.join(veri, "kampanya.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"serit": serit or {"aktif": False}}, f, ensure_ascii=False, indent=1)

    for ad, icerik in (("ilanlar", cikti),
                       ("sayfalar", {s["anahtar"]: s for s in sayfalar}),
                       ("ayarlar", {a["anahtar"]: a["deger"] for a in ayarlar})):
        with open(os.path.join(veri, ad + ".json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(icerik, f, ensure_ascii=False, indent=1)
    print("yazildi: %d ilan, %d yeni gorsel uretildi" % (len(cikti), yeni))


if __name__ == "__main__":
    main()
