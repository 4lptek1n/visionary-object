# -*- coding: utf-8 -*-
"""Butun ilan metinlerini tarar, supheli olanlari raporlar.

Aranan seyler:
  - musteri gormemesi gereken ic analiz dili (IMG_..., 'does not belong',
    'could not be resolved', 'plausible', katalog kodlari)
  - Ingilizce alana kacmis Turkce
  - bozuk/asiri kisa/asiri uzun alanlar
  - ayni baslik iki ilanda
  - sanatci alaninda ad disi metin (soru isareti, 'or', parantezli tahmin)
Cikti: tools/metin_rapor.json + ozet ekrana.
"""
import json
import os
import re
import sys
import urllib.request

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = "https://vtrwlajtotcnwusjlzgo.supabase.co"
ANON = os.environ.get("SUPABASE_ANON_KEY", "")
EPOSTA = os.environ.get("SUPABASE_EPOSTA", "")
SIFRE = os.environ.get("SUPABASE_SIFRE", "")

def giris():
    g = json.dumps({"email": EPOSTA, "password": SIFRE}).encode()
    r = urllib.request.Request(URL + "/auth/v1/token?grant_type=password", g)
    r.add_header("apikey", ANON); r.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(r, timeout=40) as c:
        return json.loads(c.read())["access_token"]

JETON = giris()

def cek(yol):
    r = urllib.request.Request(URL + "/rest/v1/" + yol)
    r.add_header("apikey", ANON); r.add_header("Authorization", "Bearer " + JETON)
    r.add_header("Range", "0-9999")
    with urllib.request.urlopen(r, timeout=120) as c:
        return json.loads(c.read())

ilanlar = cek("ilanlar?select=id,no,slug,baslik,aciklama,sanatci,eser_adi,donem,"
              "teknik,baski,ref,etiket,biyografi,aciklama_not,belge,seo_baslik,"
              "seo_aciklama,galeri_adi&order=no.asc")
print("ilan:", len(ilanlar))

IC_DIL = [
    r"IMG_\d", r"does not belong", r"does NOT belong", r"could not be",
    r"cannot be judged", r"katalog [A-Z]\d", r"olcu karel", r"galeride degil",
    r"plausible alternat", r"the same hand appears", r"whether the piece",
    r"not this", r"probably does not", r"unresolved", r"unclear whether",
    r"\bB\d{3}\b", r"\bA\d{3}\b", r"batch", r"frame_", r"\.jpe?g", r"\.webp",
    r"Photoroom", r"tape measure", r"measuring tape",
]
TURKCE = r"[çğışöüÇĞİŞÖÜ]|\b(ve|ile|icin|tablo|olcu|imza|kare|sayfa|adet)\b"

sorunlar = []
basliklar = {}
for il in ilanlar:
    s = []
    b = (il["baslik"] or "").strip()
    a = (il["aciklama"] or "").strip()
    nt = (il["aciklama_not"] or "").strip()
    sn = (il["sanatci"] or "").strip()

    if b.lower() in basliklar:
        s.append(("baslik", "AYNI BASLIK: %s ile" % basliklar[b.lower()]))
    else:
        basliklar[b.lower()] = il["slug"]

    for alan, deger in (("baslik", b), ("aciklama", a), ("seo_aciklama", il["seo_aciklama"] or ""),
                        ("eser_adi", il["eser_adi"] or ""), ("teknik", il["teknik"] or ""),
                        ("donem", il["donem"] or ""), ("baski", il["baski"] or ""),
                        ("belge", il["belge"] or ""), ("etiket", il["etiket"] or "")):
        for kalip in IC_DIL:
            if re.search(kalip, deger, re.I):
                s.append((alan, "IC DIL '%s': ...%s..." % (kalip, deger[:90])))
                break
        if re.search(TURKCE, deger):
            s.append((alan, "TURKCE?: %s" % deger[:80]))

    if sn:
        if re.search(r"\?|/| or |unread|illegib|possibly|likely|attributed", sn, re.I):
            s.append(("sanatci", "SUPHELI AD: %s" % sn))
        if len(sn) > 40:
            s.append(("sanatci", "COK UZUN: %s" % sn[:60]))
    if len(b) > 95:
        s.append(("baslik", "UZUN (%d)" % len(b)))
    if len(a) < 80:
        s.append(("aciklama", "KISA (%d)" % len(a)))
    if nt and re.search("|".join(IC_DIL), nt, re.I):
        s.append(("aciklama_not", "IC ANALIZ NOTU (sitede gorunmuyorsa sorun degil): %s" % nt[:70]))

    if s:
        sorunlar.append({"no": il["no"], "slug": il["slug"], "sorunlar": s})

with open(os.path.join(KOK, "tools", "metin_rapor.json"), "w", encoding="utf-8") as f:
    json.dump(sorunlar, f, ensure_ascii=False, indent=1)

print("sorunlu ilan:", len(sorunlar))
tur_say = {}
for x in sorunlar:
    for alan, m in x["sorunlar"]:
        anahtar = m.split(":")[0].split(" '")[0]
        tur_say[anahtar] = tur_say.get(anahtar, 0) + 1
for k, v in sorted(tur_say.items(), key=lambda z: -z[1]):
    print(" %4d  %s" % (v, k))
print()
for x in sorunlar[:25]:
    print("--", x["slug"])
    for alan, m in x["sorunlar"][:4]:
        print("   [%s] %s" % (alan, m.encode("ascii", "replace").decode()))
