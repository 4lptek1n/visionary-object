# -*- coding: utf-8 -*-
"""3B muzeyi sitenin bir sayfasi haline getirir.

Yapilanlar:
  1. Gomulu 29 eserlik katalog ve 29 base64 gorsel cikarilir; yerine
     sitenin verisinden uretilen data.js gelir. Dosya ~2.0 MB'tan ~0.8 MB'a iner
     ve muzedeki her eser artik sitedeki ilanin ta kendisidir.
  2. Fiyat kaldirilir: sitede fiyat yok, muzede de olmayacak.
  3. Envanter numarasi sitenin numarasi olur (VO-NN).
  4. Iki dugme de o ilanin site sayfasina gider.
  5. Arayuz metinleri Ingilizceye cevrilir; site Ingilizce, muze onun sayfasi.
"""
import re
import sys

SRC = sys.argv[1] if len(sys.argv) > 1 else "muze_orj.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "site/museum/index.html"

s = open(SRC, encoding="utf-8").read()
n0 = len(s)
uygulanan, atlanan = [], []


def rep(old, new, etiket, zorunlu=True):
    global s
    if old in s:
        s = s.replace(old, new)
        uygulanan.append(etiket)
    else:
        atlanan.append(etiket)
        if zorunlu:
            raise SystemExit("BULUNAMADI: " + etiket)


# 1 ---- gomulu katalog + gorseller -> data.js
i = s.find("<script>const CATALOG=[")
j = s.find("</script>", i)
if i < 0 or j < 0:
    raise SystemExit("katalog blogu bulunamadi")
s = s[:i] + '<script src="data.js"></script>' + s[j + len("</script>"):]
uygulanan.append("katalog -> data.js")

# 2 ---- fiyat, kademe araligi, envanter, baglantilar
rep("""  T1:{name:"SALON DUVARI",       range:"$0 – 750",        zone:"z1"},
  T2:{name:"GALERİ NİŞİ",        range:"$750 – 3,000",    zone:"z2"},
  T3:{name:"VİTRİN — CAM FANUS", range:"$3,000 – 15,000", zone:"z3"},
  T4:{name:"ŞAHESER APSİSİ",     range:"$15,000 +",       zone:"z4"}""",
    """  T1:{name:"THE LONG WALL",      range:"twelve works",  zone:"z1"},
  T2:{name:"GALLERY NICHE",      range:"eight works",   zone:"z2"},
  T3:{name:"VITRINE, UNDER GLASS", range:"six works",   zone:"z3"},
  T4:{name:"THE APSE",           range:"three works",   zone:"z4"}""",
    "kademe adlari")

rep('$("mPrice").textContent = money(o.p);',
    '$("mPrice").textContent = "Price Upon Request";',
    "fiyat")

rep("""  const rows=[
    ["Teknik",      o.m],
    ["Dönem",       o.e],
    ["Ölçü (çerçeve dâhil)", `${inW}" × ${inH}"`],
    ["Metrik karşılık",      `${o.w} × ${o.h} cm`],
    ["Çerçeve",     o.tier==="T1" ? "Dönem ahşap çerçeve" : "Yaldızlı ahşap çerçeve"],
    ["Envanter no", "VM-"+o.id.toUpperCase().slice(0,6)],
    ["Köken",       "—"],
    ["Durum raporu","—"],
    ["Sertifika",   "—"]
  ];""",
    """  const rows=[
    ["Medium",      o.m],
    ["Creation Year", o.e || "—"],
    ["Height",      `${o.inH} in (${o.h} cm)`],
    ["Width",       `${o.inW} in (${o.w} cm)`],
    ["Framing",     o.frame],
    ["Reference",   o.ref],
    ["Photographs", o.shots + " in the listing"],
    ["Documentation", o.doc || "—"],
    ["Condition",   "As shown in the photographs"]
  ];""",
    "kunye satirlari")

rep("""  const ref="VM-"+o.id.toUpperCase().slice(0,6);
  $("mAsk").href = "mailto:info@visionarymuseum.com?subject="+
    encodeURIComponent(`Bilgi talebi — ${o.t} (${ref})`);
  $("mApt").href = "mailto:info@visionarymuseum.com?subject="+
    encodeURIComponent(`Özel görüşme talebi — ${o.t} (${ref})`);""",
    """  /* muze bir vitrin: her eser sitedeki kendi ilanina goturur */
  $("mAsk").href = o.url;
  $("mApt").href = o.url;""",
    "baglantilar")

# duvar ve vitrin etiketleri: fiyat yerine sanatci / referans
rep('map:labelTex(obj.t, "$"+obj.p.toLocaleString("en-US")), transparent:true',
    'map:labelTex(obj.t, obj.a || obj.ref), transparent:true',
    "duvar etiketi")
rep('map:labelTex(obj.t,"$"+obj.p.toLocaleString("en-US")), transparent:tr',
    'map:labelTex(obj.t, obj.a || obj.ref), transparent:tr',
    "vitrin etiketi")

# 3 ---- arayuz metinleri
UI = [
    ("ANTİKA &nbsp;·&nbsp; SANAT &nbsp;·&nbsp; KOLEKSİYON",
     "ANTIQUE &nbsp;·&nbsp; ART &nbsp;·&nbsp; COLLECTION"),
    ("GİRİŞİ ATLA", "SKIP THE ENTRANCE"),
    ("AYNI KADEMEDEN", "ELSEWHERE IN THIS ROOM"),
    ("KOLEKSİYON DEĞERİ", "PRICE"),
    ("BİLGİ &amp; TEKLİF AL", "VIEW THE LISTING"),
    ("ÖZEL GÖRÜŞME", "CONTACT THE SELLER"),
    ("YAKINLAŞTIRMAK İÇİN TIKLA", "CLICK TO ZOOM"),
    ("KOLEKSİYON HAZIRLANIYOR", "PREPARING THE COLLECTION"),
    ("YAKINDA AÇILIYOR", "OPENING SOON"),
    ("GİRİŞ HOLÜ", "ENTRANCE HALL"),
    ("SALON DUVARI", "THE LONG WALL"),
    ("GALERİ NİŞLERİ", "GALLERY NICHES"),
    ("VİTRİN SALONU", "THE VITRINE"),
    ("ŞAHESER APSİSİ", "THE APSE"),
    ("TABLOLAR KANADI AÇIK — DİĞER 3 KANAT YAKINDA",
     "THE PAINTING WING IS OPEN \u00b7 THREE MORE WINGS TO COME"),
    ("ZEMİNE TIKLA — YÜRÜ", "CLICK THE FLOOR TO WALK"),
    ("ESERE TIKLA — İNCELE", "CLICK A WORK TO INSPECT"),
    ("SÜRÜKLE — ETRAFA BAK", "DRAG TO LOOK AROUND"),
    ("Köken, durum raporu ve sertifika bilgileri katalog çalışması tamamlandıkça bu alana işlenecektir.",
     "Every figure here is read from the listing itself. Open the listing for the full set of photographs."),
    ("TABLOLAR", "PAINTINGS"),
    ("HALILAR", "PERSIAN RUG"),
    ("AYDINLATMA", "LIGHTING"),
    ("HEYKEL", "SCULPTURE"),
    ("ESER", "WORKS"),
    ("YAKINDA", "SOON"),
    ("ÇIKIŞ", "EXIT"),
]
for a, b in UI:
    if a in s:
        s = s.replace(a, b)
        uygulanan.append("metin: " + a[:26])
    else:
        atlanan.append("metin: " + a[:26])

# baslik ve aciklama
s = s.replace("Visionary Museum — Sanal Koleksiyon",
              "The Museum \u00b7 Visionary Object")
s = s.replace('<html lang="tr">', '<html lang="en">')

open(OUT, "w", encoding="utf-8").write(s)
print("giris  : %.2f MB" % (n0 / 1024 / 1024))
print("cikis  : %.2f MB" % (len(s) / 1024 / 1024))
print("uygulanan: %d" % len(uygulanan))
if atlanan:
    print("atlanan  :", ", ".join(atlanan))
