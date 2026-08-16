# -*- coding: utf-8 -*-
"""Gorunur alanlara sizmis ic-katalog dilini temizler.

Iki katman:
  1. Genel kurallar (tum ilanlara): dosya adlari (IMG_1234), 'photographed as',
     'moved here from A123' gibi kaliplar.
  2. Ilana ozel duzeltmeler: baslik kisaltma, sanatci adi, capraz referans
     cumleleri, SEO acilislari.
Degisen her alan API ile guncellenir; degismeyene dokunulmaz.
"""
import json
import os
import re
import urllib.request

URL = "https://vtrwlajtotcnwusjlzgo.supabase.co"
ANON = os.environ["SUPABASE_ANON_KEY"]

def giris():
    g = json.dumps({"email": os.environ["SUPABASE_EPOSTA"],
                    "password": os.environ["SUPABASE_SIFRE"]}).encode()
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

def yama(slug, alanlar):
    g = json.dumps(alanlar).encode()
    r = urllib.request.Request(URL + "/rest/v1/ilanlar?slug=eq." + slug, g, method="PATCH")
    r.add_header("apikey", ANON); r.add_header("Authorization", "Bearer " + JETON)
    r.add_header("Content-Type", "application/json"); r.add_header("Prefer", "return=minimal")
    urllib.request.urlopen(r, timeout=60).read()

GORUNUR = ["baslik", "aciklama", "belge", "etiket", "seo_aciklama", "sanatci",
           "eser_adi", "teknik", "donem", "baski"]

# ---------------- 1. genel kurallar ----------------
GENEL = [
    (r"\s*[-,;]?\s*photographed as IMG_\d+[^.;)]*", ""),
    (r"\s*[-,;]?\s*the label was photographed as IMG_\d+[^.;)]*", ""),
    (r"\s*[-,;]?\s*label photographed as IMG_\d+[^.;)]*", ""),
    (r",?\s*(which was\s+)?filed with (the\s+)?listing [AB]\d{3}[^.;)]*", ""),
    (r",?\s*moved here from [AB]\d{3}", ""),
    (r"\s+in the raking light of IMG_\d+", " under raking light"),
    (r"\s+in IMG_\d+(\s*(/|and)\s*(IMG_)?\d+)*", ""),
    (r"\s+visible in IMG_\d+", ""),
    (r"\s*\(IMG_\d+\)", ""),
    (r"IMG_\d+,?\s*", ""),
    (r"\s+", " "),  # cift bosluklari topla (en sonda)
]

# ---------------- 2. ilana ozel ----------------
OZEL = {
 "ilan-67": {"aciklama": [
    (r";? ?so the surface could not be fully inspected", "")]},
 "ilan-124": {
   "sanatci": "R. Crespi",
   "baslik": "R. Crespi, 'Agee's Mark', Signed Giclee 22/600, Framed",
   "aciklama": [(r"^R\. CRESP\. \(certificate\); Crespi \(pencil signature on the sheet\)\.",
                 "R. Crespi.")],
   "seo_aciklama": "R. Crespi, 'Agee's Mark': a soft sage-green form between wind-shaped tree and arcaded ruin, giclee on Arches paper, pencil signed and numbered 22/600, framed."},
 "ilan-133": {
   "belge": "no certificate photographed",
   "aciklama": [(r"\s*Accompanied by a certificate: [^.]*catalogued as A083[^.]*\.", "")]},
 "ilan-145": {
   "aciklama": [(r"^Companion piece in the same manner as A\d{3}:",
                 "Companion piece to the paired silk panel in this collection:")],
   "seo_aciklama": "Chinese silk painting of an orange lily with butterflies and moths in russet, gold, turquoise and scarlet, gouache and ink on silk, framed."},
 "ilan-152": {"aciklama": [
    (r"Framed to match A\d{3}: ", "Framed with a ")]},
 "ilan-170": {
   "belge": "no certificate photographed with this lot",
   "etiket": "Fanch; 143/250",
   "aciklama": [(r"Inscribed on the reverse or mount: Fanch; 143/250;[^.]*\.",
                 "Inscribed on the reverse or mount: Fanch; 143/250.")]},
 "ilan-172": {"baslik": "Brittany Village Lane, Signed Serigraph Artist's Proof, Christian Title, Framed"},
 "ilan-200": {"baslik": "Christmas at Estill Fork, Alabama, Signed Drypoint 24/50, C. H. Anderson, Framed"},
 "ilan-213": {
   "etiket": "\"En Visite\" GRAU SALA (1911) ORIGINAL LITHOGRAPH #186/220 PENCIL SIGNED (typed label on the backing board)",
   "aciklama": [(r"\(typed label taped to a brown-paper backing board;[^)]*\)",
                 "(typed label taped to a brown-paper backing board)"),
                (r";?\s*label\s*$", "")]},
 "ilan-214": {
   "etiket": "",
   "aciklama": [(r"\s*Inscribed on the reverse or mount: \"En Visite\"[^.]*not to this picture\)\.", "")]},
 "ilan-221": {
   "aciklama": [(r";? the signature ends in a form close to that on listing B\d{3}", "")],
   "etiket": [(r";? the signature ends in a form close to that on listing B\d{3}", ""),
              (r"not legible in the photographs", "not fully legible in the photographs")]},
 "ilan-258": {"belge": "No certificate photographed with this listing."},
 "ilan-259": {
   "baslik": "Picasso Woman in Hat Offset Lithograph 49/200, Certificate, Framed",
   "aciklama": [(r"^Pablo Ruiz Picasso\. Detail photographs of the lower edge of a large colour print:",
                 "Pablo Ruiz Picasso. A large colour print in the manner of the late linocuts, photographed here in close detail along the lower edge:")],
   "seo_aciklama": "Woman in Hat after Picasso: offset lithograph on Arches paper numbered 49/200, pencil signature in the margin, with Spanish certificate, framed."},
 "ilan-267": {
   "aciklama": [(r"\s*The certificate is photographed as[^.]*\.", ""),
                (r"\s*The certificate is[^.]*listing B\d{3}\.", "")],
   "belge": [(r"\s*The certificate is photographed as[^.]*\.", ""),
             (r"\s*The certificate is[^.]*listing B\d{3}\.", "")]},
}

ilanlar = cek("ilanlar?select=slug," + ",".join(GORUNUR) + "&order=no.asc")
degisen = 0
for il in ilanlar:
    slug = il["slug"]
    yeni = {}
    for alan in GORUNUR:
        eski = il.get(alan) or ""
        v = eski
        ozel = OZEL.get(slug, {}).get(alan)
        if isinstance(ozel, str):
            v = ozel
        else:
            if isinstance(ozel, list):
                for kalip, yerine in ozel:
                    v = re.sub(kalip, yerine, v)
            for kalip, yerine in GENEL:
                v = re.sub(kalip, yerine, v)
            v = v.strip().strip(";,").strip()
            if eski.strip() == "":
                v = eski  # bos alani bosluk temizligiyle degistirme
        if v != eski:
            yeni[alan] = v
    if yeni:
        yama(slug, yeni)
        degisen += 1
        for alan in yeni:
            print("%-9s %-12s %d -> %d" % (slug, alan, len(il.get(alan) or ""), len(yeni[alan])))

print("degisen ilan:", degisen)

# ---------------- son kontrol ----------------
kalan = 0
for il in cek("ilanlar?select=slug," + ",".join(GORUNUR)):
    for alan in GORUNUR:
        v = il.get(alan) or ""
        if re.search(r"IMG_\d|moved here from|filed with|photographed as IMG|catalogued as [AB]\d{3}|listing [AB]\d{3}", v):
            print("KALAN:", il["slug"], alan, v[:100])
            kalan += 1
print("kalan ic referans:", kalan)
