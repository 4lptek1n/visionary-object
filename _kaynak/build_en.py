# -*- coding: utf-8 -*-
"""Visionary Object. 1stDibs structure and 1stDibs copy, in English.
Only the categories differ, plus the Museum. No invented item data."""
import json, base64, os, sys
# Betik hangi klasordeyse kaynak orasidir: hem sandbox'ta hem de
# kullanicinin kendi bilgisayarinda ayni sekilde calissin.
W = os.path.dirname(os.path.abspath(__file__))
# Uretilen sitenin yazilacagi yer. Normalde kaynagin yanindaki site klasoru;
# GitHub Actions'ta depo koku (VO_CIKTI ile verilir).
CIKTI = os.environ.get("VO_CIKTI") or os.path.join(W, "site")

def panel_ayari():
    """Yerinde duzenleme ve yonetim paneli icin Supabase adresi ve acik anahtar.

    Tek kaynak: data/panel.json. Dosya yoksa duzenleme katmani sessizce kapali
    kalir; ziyaretci hicbir fark gormez. Bu iki deger gizli degildir, tarayiciya
    inmesi normaldir; veriyi koruyan sey veritabanindaki erisim kurallaridir.
    """
    yol = os.path.join(W, "data", "panel.json")
    if not os.path.exists(yol):
        return {"URL": "BURAYA_PROJE_URL", "ANAHTAR": "BURAYA_ANON_ANAHTAR"}
    with open(yol, encoding="utf-8") as f:
        a = json.load(f)
    return {"URL": a.get("URL", ""), "ANAHTAR": a.get("ANAHTAR", "")}


def db_sayfalar():
    """Panelden duzenlenen site metinleri. Bos olanlar icin kodda yazan
    varsayilan metin kullanilir; panel doldurulmadan site bozulmaz."""
    yol = os.path.join(W, "data", "sayfalar.json")
    if not os.path.exists(yol):
        return {}
    try:
        with open(yol, encoding="utf-8") as f:
            d = json.load(f)
    except Exception:
        return {}
    return {k: v for k, v in d.items() if (v or {}).get("icerik", "").strip()}


def db_ayarlar():
    """Marka adi, iletisim, konum, para birimi. Panelden gelir."""
    yol = os.path.join(W, "data", "ayarlar.json")
    if not os.path.exists(yol):
        return {}
    try:
        with open(yol, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def kampanya_serit():
    """Sitenin en ustundeki kampanya seridi. data/kampanya.json'dan gelir.

    Dosya yoksa ya da kampanya kapaliysa serit hic basilmaz; sayfa bir piksel
    bile kaymaz. Bir anda tek serit gorunur: en yuksek oncelikli kampanya.
    """
    yol = os.path.join(W, "data", "kampanya.json")
    if not os.path.exists(yol):
        return ""
    try:
        with open(yol, encoding="utf-8") as f:
            k = json.load(f)
    except Exception:
        return ""
    a = (k or {}).get("serit") or {}
    if not a.get("aktif") or not a.get("metin"):
        return ""
    bag = a.get("baglanti") or "#/browse?offer=sale"
    etiket = a.get("etiket") or ""
    return ('<div class="kmp">' +
            (f'<b>{esc_py(etiket)}</b>' if etiket else "") +
            f'<span>{esc_py(a["metin"])}</span>' +
            f'<a href="{esc_py(bag)}">See the pieces</a></div>')


def esc_py(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))

sys.path.insert(0, W)
from site_css import CSS
from css2 import CSS2
from listings_en import L as LIST
from css3 import CSS3
from views2 import VIEWS2
from js_state import STATE_JS
from pages_en import INFO, MUSEUM_ROOMS

# Alan adi alindiginda burayi degistirmek yeterli: canonical, og:url, sitemap
# ve robots.txt hepsi bu tek sabitten uretiliyor.
# Gecici demo adresi. Gercek alan adi alindiginda burasi degisir ve site
# yeniden uretilir; canonical, sitemap, robots ve og etiketleri buradan gelir.
SITE_URL = "https://thetimesfigures.com"
def _es(ad, bos):
    """Eski kaynak dosyalar. Site artik ilanlar.json'dan uretiliyor; bunlar
    yalnizca ilan_disa_aktar.py icin duruyor, yoksa da site kurulur."""
    try:
        with open(f"{W}/data/{ad}", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return bos


CAT = _es("katalog.json", [])
FACET = _es("facets.json", {})
# Serit metre fotograflarindan okunan gercek dis olculer (inc).
DIMS = {int(k): v for k, v in _es("dims.json", {}).items()}
# Temiz karesi olmayan ilanlar icin: satici fotografinin cerceveye kirpilmis hali
KAPAK = {int(k): v for k, v in _es("kapak.json", {}).items()}
# Cerceve olmayan, gergi bezine gerilmis tuvaller
CANVAS_ONLY = {8, 30, 31, 32, 33, 34, 35}


def size_bucket(h):
    if h is None:
        return ""
    if h < 24:
        return "small"
    if h < 48:
        return "medium"
    if h < 72:
        return "large"
    return "oversized"


def orient_of(w, h):
    r = w / h
    if r > 1.08:
        return "horizontal"
    if r < 0.93:
        return "vertical"
    return "square"


GAL = _es("gallery.json", [])
# Galeride gosterilecek kareler (kare_sec.py): serit metre kareleri, ham
# kareler ve ayni goruntunun tekrarlari disarida birakildi.
try:
    _sec = {(x["no"], x["i"]) for x in _es("kare_sec.json", [])}
    if _sec:
        GAL = [g for g in GAL if (g["no"], g["i"]) in _sec]
except (KeyError, TypeError):
    pass
IMG = {}
for g in GAL:
    IMG.setdefault(g["no"], []).append(
        {"t": g["t"], "c": g["c"], "f": g["f"], "w": g["w"], "h": g["h"],
         "rol": g["rol"], "src": g["kaynak"], "i": g["i"]})

# Temiz karesi olmayan ilanlarda kesilmis kapak galerinin ilk karesidir; kesimin
# yapildigi ham kare listeden cikar, ayni fotograf iki kez gorunmesin.
for _no, _k in KAPAK.items():
    _a = IMG.get(_no)
    if not _a:
        continue
    _a[:] = [o for o in _a if o.get("i") != _k.get("i")]
    _a.insert(0, {"t": _k["t"], "c": _k["c"], "f": _k["f"], "w": _k["w"],
                  "h": _k["h"], "rol": "tam", "src": "kirpilmis", "i": -1})

# fotoğraflardan okunan kayıtlar -> İngilizce alanlar
EN = {
 1:  dict(creator="G. Gounaro", period="1973", edition="20/200", src="IMG_7427"),
 2:  dict(creator="G. Gounaro", period="1973", edition="35/200", src="IMG_7435"),
 7:  dict(doc="Certificate of Authenticity", src="IMG_7480-7482"),
 9:  dict(gallery="Fine Arts Gallery, Inc., Ardmore, PA", medium="Original Serigraph",
          doc="Certificate of Authenticity", src="IMG_7496"),
 14: dict(title="Divan Japonais", src="IMG_7523"),
 17: dict(creator="Jean Sariano", title="Going West", period="1975",
          medium="Original Relief Embossed Etching", edition="Edition of 50 plus 20 proofs",
          note="Artist's Proof", ref="96-21-8",
          bio="Born in Algeria, 1942. Studied at the École Municipale et Régionale des Beaux-Arts d'Oran, "
              "the École Nationale Supérieure des Beaux-Arts in Paris, and Pratt Institute, New York.",
          src="IMG_7544-7552"),
 18: dict(title="Dancing Tulips", creator="Mary Sue Ha…ter", period="2005", src="IMG_7555"),
 23: dict(title="Sunset Shadows", creator="Ehrlich / Sacco", edition="/200", src="IMG_7586"),
 27: dict(label="Formosa Painting House, No. 141", src="IMG_7615"),
 28: dict(label="Formosa Painting House, No. 124", src="IMG_7621"),
 30: dict(creator="W. Petitchot", src="IMG_7634"),
 32: dict(creator="D.W. Westcott", src="IMG_7645"),
 34: dict(creator="G. Roddell", src="IMG_7655"),
 35: dict(creator="K. Lombard…", src="IMG_7661"),
 39: dict(title="Diplôme de Croix de Guerre avec Palme", period="1946",
          note="370th Infantry Regiment, 90th Infantry Division. 10-15 November 1944, Metz and Thionville. "
               "Décision N° 267.", src="IMG_7685"),
 40: dict(title="Campanile U.C.", src="IMG_7693"),
 45: dict(creator="Susan Thomas Underwood", title="The Spirits Speak To Me",
          edition="/200", src="IMG_7724, IMG_7728"),
 47: dict(creator="Fran Larsen", title="The Village Path", period="1996",
          medium="Watercolor in hand carved and painted polychrome frame",
          ref="F 9701-006", dims=(21.5, 26), dimsOf="framed", src="IMG_7744"),
 48: dict(creator="Salvador Dalí", title="Piccarda Donati",
          doc="Certificate of Authenticity", src="IMG_7752"),
 49: dict(creator="Legas", note="Hungarian artist", dims=(20, 24), dimsOf="canvas",
          src="IMG_7756, IMG_7759, IMG_7760"),
}

KATEN = {"tablo": "Paintings & Prints", "obje": "Handmade Objects", "belge": "Documents",
         "rugs": "Persian Rug", "lighting": "Lighting", "sculpture": "Sculpture"}
ROLEN = {"tam":"full view","aci":"angled view","olcu-y":"width measurement","olcu-d":"height measurement",
         "detay":"detail","imza":"signature","plaka":"maker's plaque","arka":"reverse",
         "etiket":"back label","sertifika":"certificate","duvar":"in situ"}


def js_rows_eski():
    """Eski kaynak: katalog.json + listings_en + facets + dims. Yalnizca
    ilanlar.json'u ilk kez uretirken kullanilir (ilan_disa_aktar.py)."""
    out = []
    for it in CAT:
        e = EN.get(it["no"], {})
        roles = {}
        for k in it["kareler"]:
            roles[k["rol"]] = roles.get(k["rol"], 0) + 1
        out.append({
            "no": it["no"], "slug": it["slug"], "cat": it["kat"], "catEn": KATEN[it["kat"]],
            "title": LIST[it["no"]][0],
            "desc": LIST[it["no"]][1],
            "work": e.get("title", ""),
            "creator": e.get("creator", ""),
            "period": e.get("period", ""),
            "medium": e.get("medium", ""),
            "edition": e.get("edition", ""),
            "ref": e.get("ref", ""),
            "gallery": e.get("gallery", ""),
            "label": e.get("label", ""),
            "bio": e.get("bio", ""),
            "doc": e.get("doc", ""),
            "src": e.get("src", ""),
            "dims": [DIMS[it["no"]]["w"], DIMS[it["no"]]["h"]] if it["no"] in DIMS
                    else (list(e["dims"]) if e.get("dims") else None),
            "dimsOf": ("stretched canvas, unframed" if it["no"] in CANVAS_ONLY
                       else "outside of frame"),
            "size": size_bucket(DIMS[it["no"]]["h"] if it["no"] in DIMS else None),
            "orient": (orient_of(DIMS[it["no"]]["w"], DIMS[it["no"]]["h"])
                       if it["no"] in DIMS else it.get("orient", "")),
            "subject": FACET[str(it["no"])]["subject"],
            "medium2": FACET[str(it["no"])]["medium"],
            "style": FACET[str(it["no"])]["style"],
            "framing": FACET[str(it["no"])]["framing"],
            "period2": FACET[str(it["no"])]["period"],
            "color": FACET[str(it["no"])]["color"],
            "shots": len(IMG[it["no"]]),
            "roles": roles,
            "img": IMG[it["no"]],
            "cov": (dict(KAPAK[it["no"]], rol="tam", src="kirpilmis")
                    if it["no"] in KAPAK else None),
        })
    return out


def js_rows():
    """Sitenin tek veri kaynagi: data/ilanlar.json.

    Panelden duzenlenen dosya budur. Kareler listesinin birinci elemani kapak
    karesidir; sirayi degistirmek kapagi degistirir. 'yayinda' kapatilan ilan
    siteye hic girmez.
    """
    veri = json.load(open(f"{W}/data/ilanlar.json", encoding="utf-8"))
    out = []
    for it in veri:
        if not it.get("yayinda", True):
            continue
        img, roles = [], {}
        for k in it["kareler"]:
            t = k["temel"]
            img.append({"t": f"{t}-t.webp", "c": f"{t}-c.webp", "f": f"{t}-f.webp",
                        "w": k["w"], "h": k["h"], "rol": k["rol"], "src": k["kaynak"]})
            roles[k["rol"]] = roles.get(k["rol"], 0) + 1
        o = it.get("olcu")
        dims = [o["w"], o["h"]] if o else None
        f = it["facet"]
        out.append({
            "no": it["no"], "slug": it["slug"], "cat": it["kat"],
            "catEn": KATEN[it["kat"]],
            "title": it["baslik"], "desc": it["aciklama"],
            "work": it.get("eser_adi", ""), "creator": it.get("sanatci", ""),
            "period": it.get("donem", ""), "medium": it.get("teknik", ""),
            "edition": it.get("baski", ""), "ref": it.get("ref", ""),
            "gallery": it.get("galeri_adi", ""), "label": it.get("etiket", ""),
            "bio": it.get("biyografi", ""),
            # "not" alani BILEREK siteye tasinmiyor: katalog calismasinin ic
            # notudur (dosya adlari, eski liste kodlari); yalnizca panelde durur.
            "doc": it.get("belge", ""), "src": it.get("kaynak_dosya", ""),
            "dims": dims,
            "dimsOf": (o or {}).get("nesi", "outside of frame"),
            "size": size_bucket(dims[1] if dims else None),
            "orient": orient_of(dims[0], dims[1]) if dims else "",
            "subject": f["subject"], "medium2": f["medium"], "style": f["style"],
            "framing": f["framing"], "period2": f["period"], "color": f["color"],
            # Fiyat ve kampanya. fiyat None ise ya da gizliyse site
            # "Price Upon Request" yazar; kampanya varsa eski fiyat ustu cizili
            # gosterilir. Hesap panelde degil, veriyi cekerken yapilir.
            "price": it.get("fiyat"), "priceWas": it.get("fiyat_eski"),
            "cur": it.get("para_birimi") or "USD",
            "sale": it.get("kampanya"),
            "sold": bool(it.get("satildi")), "reserved": bool(it.get("rezerve")),
            # Tek tikla satis bu eserde acik mi. Odeme genel ayari ayrica bakilir.
            "buy": bool(it.get("satin_alinabilir")),
            # Panelden yazilan SEO aciklamasi; statik sayfalarin meta'sinda kullanilir.
            "seo": (it.get("seo_aciklama") or "").strip(),
            "shots": len(img), "roles": roles, "img": img,
            # Kapak her zaman ilk karedir. Ayri bir alan olarak da veriliyor ki
            # kartlar, muze ve arama tek bir kurala baksin.
            "cov": img[0] if img else None,
        })
    return out


def js_data():
    return json.dumps(js_rows(), ensure_ascii=False, separators=(",", ":"))


IC = {
 "search": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
 "heart":  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M12 20.5 4.6 13a4.6 4.6 0 1 1 7.4-5.3A4.6 4.6 0 1 1 19.4 13z"/></svg>',
 "user":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="12" cy="8.5" r="3.6"/><path d="M4.8 20a7.4 7.4 0 0 1 14.4 0"/></svg>',
 "bag":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M5.5 8h13l-1 12h-11z"/><path d="M9 8V6.2a3 3 0 0 1 6 0V8"/></svg>',
 "menu":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M3.5 7h17M3.5 12h17M3.5 17h17"/></svg>',
 "left":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>',
 "right":  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg>',
 "ship":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M2.5 7h11v10h-11z"/><path d="M13.5 10h4l3 3v4h-7z"/><circle cx="6" cy="18.5" r="1.6"/><circle cx="17" cy="18.5" r="1.6"/></svg>',
 "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M12 3l7 2.6v6.1c0 4.3-3 7.6-7 9.3-4-1.7-7-5-7-9.3V5.6z"/><path d="m9 12 2.2 2.2L15.5 10"/></svg>',
 "x":      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
 "eye":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M2.5 12S6 5.8 12 5.8 21.5 12 21.5 12 18 18.2 12 18.2 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="2.9"/></svg>',
 "filter": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M3.5 6.5h17M6.5 12h11M10 17.5h4"/></svg>',
 "folder": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M3.5 6.5h6l2 2.2h9v10.8h-17z"/></svg>',
 "zoom":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5M11 8.4v5.2M8.4 11h5.2"/></svg>',
 "ruler":  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M3 9.5h18v5H3z"/><path d="M7 9.5v3M11 9.5v4M15 9.5v3M19 9.5v4"/></svg>',
}

NAV = [
 ("New Arrivals", "new", None),
 ("Paintings & Prints", "tablo", [
   ("Shop by Category", [("Paintings", "cat=tablo&medium=oil"),
                         ("Prints & Works on Paper", "cat=tablo&medium=print"),
                         ("Drawings & Watercolors", "cat=tablo&medium=watercolour"),
                         ("Charcoal & Drawing", "cat=tablo&medium=charcoal"),
                         ("All Paintings & Prints", "cat=tablo")]),
   ("Shop by Subject", [("Landscape", "cat=tablo&subject=landscape"),
                        ("People", "cat=tablo&subject=figurative"),
                        ("Still Life", "cat=tablo&subject=still-life"),
                        ("Architecture", "cat=tablo&subject=architecture"),
                        ("Animals", "cat=tablo&subject=animal")]),
   ("Shop by Documentation", [("Certificate of Authenticity", "doc=sertifika"),
                              ("Back Label", "doc=etiket"),
                              ("Signature Photographed", "doc=imza"),
                              ("Maker's Plaque", "doc=plaka")])]),
 ("Handmade Objects", "obje", [
   ("Shop by Category", [("Lace & Needlework", "cat=obje&medium=textile"),
                         ("All Handmade Objects", "cat=obje")]),
   ("More Ways to Shop", [("Collections", "#/collections"), ("Creators", "#/creators"),
                          ("The Museum", "museum/index.html")])]),
 ("Documents", "belge", [
   ("Shop by Category", [("Military Diplomas", "cat=belge"),
                         ("All Documents", "cat=belge")])]),
 ("Persian Rug", "rugs", None),
 ("Lighting", "lighting", None),
 ("Sculpture", "sculpture", None),
 ("The Museum", "museum", None),
]


def masthead():
    links, megas = [], []
    for label, slug, groups in NAV:
        href = {"museum": "museum/index.html"}.get(slug, f"#/browse?cat={slug}")
        if groups:
            links.append(f'<li><button type="button" data-mega-btn="{slug}" aria-expanded="false" aria-controls="mega-{slug}">{label}</button></li>')
            cols = ""
            for g, items in groups:
                lis = ""
                for txt, q in items:
                    url = q if (q.startswith("#") or q.endswith(".html")) else f"#/browse?{q}"
                    lis += f'<li><a href="{url}">{txt}</a></li>'
                cols += f'<div><h3>{g}</h3><ul>{lis}</ul></div>'
            megas.append(
                f'<div class="mega" id="mega-{slug}" data-mega hidden><div class="shell mega-in">{cols}'
                f'<a class="mega-tile" href="{href}"><span class="mega-fig" data-mega-img="{slug}"></span>'
                f'<span class="mega-cap"><b>New Arrivals</b><i>Shop Now &#8594;</i></span></a>'
                f'</div></div>')
        else:
            cls = ' class="accent"' if slug == "new" else (
                 ' class="museum-link"' if slug == "museum" else "")
            links.append(f'<li><a href="{href}"{cls}>{label}</a></li>')
    return (
'<header class="masthead">'
'<div class="shell mh-top">'
'<a class="brand" href="#/">'
'<img class="brand-mark" src="img/brand/mark-144.png" srcset="img/brand/mark-72.png 72w, img/brand/mark-144.png 144w" sizes="38px" width="38" height="38" alt="" decoding="async">'
'<span class="brand-type"><b>Visionary</b><i>OBJECT</i></span></a>'
'<form class="search" role="search" onsubmit="return false" id="searchForm">'
'<label class="sr" for="q">Search Visionary Object</label>' + IC['search'] +
'<input id="q" name="q" type="search" placeholder="Search Visionary Object" autocomplete="off"'
' role="combobox" aria-expanded="false" aria-controls="sugg" aria-autocomplete="list">'
'<button class="clr" type="button" id="qClear" aria-label="Clear search terms">' + IC['x'] + '</button>'
'<button class="go" type="submit" aria-label="Search">' + IC['search'] + '</button>'
'<div class="sugg" id="sugg" role="listbox" aria-label="Search suggestions" hidden></div>'
'</form>'
'<div class="mh-act">'
'<div class="mh-auth"><button type="button" data-auth="in">Log In</button>'
'<button type="button" data-auth="up">Sign Up</button></div>'
'<button class="ico only-s" type="button" id="navBtn" aria-label="Menu"'
' aria-haspopup="dialog" aria-expanded="false" aria-controls="navDrawer">' + IC['menu'] + '</button>'
'<a class="ico" href="#/favorites" aria-label="Favorites"><span class="cnt-b" id="favCount" hidden>0</span>' + IC['heart'] + '</a>'
'<a class="ico" href="#/account" aria-label="Account">' + IC['user'] + '</a>'
'<button class="ico" type="button" id="cartBtn" aria-label="Cart" aria-haspopup="dialog">'
'<span class="cnt-b" id="cartCount" hidden>0</span>' + IC['bag'] + '</button>'
'</div></div>'
'<nav class="catnav" aria-label="Categories"><div class="shell"><ul>' + "".join(links) + '</ul></div></nav>'
+ "".join(megas) + '</header>')


FOOT = [
 ("Shop", [("Paintings & Prints", "#/browse?cat=tablo"), ("Handmade Objects", "#/browse?cat=obje"),
           ("Documents", "#/browse?cat=belge"), ("Persian Rug", "#/browse?cat=rugs"),
           ("Lighting", "#/browse?cat=lighting"), ("Sculpture", "#/browse?cat=sculpture"),
           ("New Arrivals", "#/browse?cat=new"),
           ("Collections", "#/collections"), ("Creators", "#/creators")]),
 ("Buy", [("How It Works", "#/info/how-it-works"), ("The Visionary Object Promise", "#/info/promise"),
          ("Shipping & Delivery", "#/info/shipping"), ("Returns & Cancellation", "#/info/returns"),
          ("Cart", "#/cart"), ("Favorites", "#/favorites")]),
 ("Customer Support", [("Contact Us", "#/info/contact"), ("FAQ", "#/info/faq"),
                       ("Condition Reports", "#/info/faq"), ("Account", "#/account")]),
 ("Our Company", [("About Us", "#/info/about"), ("The Museum", "museum/index.html"),
                  ("User Agreement", "#/info/user-agreement"), ("Privacy Policy", "#/info/privacy"),
                  ("Site Map", "#/sitemap"), ("Full Item Index", "category/all.html")]),
]

SOCIAL = {
 "Instagram": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><rect x="3.5" y="3.5" width="17" height="17" rx="4.6"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r="1"/></svg>',
 "Pinterest": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="12" cy="12" r="8.6"/><path d="M10.6 20.4c.6-2.2 1.7-6 1.7-6m-1.2-2.6c0-1.7 1.1-2.9 2.5-2.9 1.4 0 2.4 1 2.4 2.6 0 1.9-1.1 3.6-2.6 3.6-.9 0-1.6-.7-1.4-1.6"/></svg>',
 "Facebook": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M14.6 21v-7.5h2.5l.4-2.9h-2.9V8.7c0-.8.3-1.4 1.5-1.4h1.5V4.7A20 20 0 0 0 15.4 4.5c-2.2 0-3.7 1.3-3.7 3.8v2.3H9.2v2.9h2.5V21z"/></svg>',
}

CUR = [("$ USD", "USD"), ("€ EUR", "EUR"), ("£ GBP", "GBP"), ("₺ TRY", "TRY")]


def footer():
    cols = "".join(
        '<div><h3>' + g + '</h3><ul>' +
        "".join(f'<li><a href="{u}">{t}</a></li>' for t, u in items) + '</ul></div>'
        for g, items in FOOT)
    social = "".join(f'<a href="#/info/contact" aria-label="{k}">{v}</a>' for k, v in SOCIAL.items())
    cur = "".join(f'<option>{a}</option>' for a, _ in CUR)
    return (
'<footer class="foot">'
'<div class="shell foot-grid">'
'<div><a class="brand brand--full" href="#/" aria-label="Visionary Object, Arts and Antiques">'
'<img src="img/brand/logo-520.webp" srcset="img/brand/logo-520.webp 520w, img/brand/logo-1040.webp 1040w" '
'sizes="(min-width:900px) 240px, 200px" width="240" height="280" alt="Visionary Object, Arts and Antiques" loading="lazy" decoding="async"></a>'
'<p class="foot-note">Extraordinary antique art and objects, one of a kind, from a single collection.</p>'
'<form class="news-form" id="newsForm" novalidate>'
'<label class="sr" for="nl">Email address</label>'
'<input id="nl" type="email" placeholder="Yes, here&#39;s my email" autocomplete="email">'
'<button type="submit">Sign Up</button></form>'
'<p class="news-note" id="newsNote">Sign up for emails when new listings are added, including Persian '
'rugs, lighting and sculpture. By entering your email you agree to our '
'<a href="#/info/user-agreement">User Agreement</a> and <a href="#/info/privacy">Privacy Policy</a>.</p>'
'<div class="social">' + social + '</div></div>'
+ cols +
'</div>'
'<div class="shell"><div class="disp">'
'<span>Display Settings</span>'
'<label class="sr" for="d-c">Country</label>'
'<select id="d-c"><option>United States</option><option>T&uuml;rkiye</option>'
'<option>United Kingdom</option><option>France</option><option>Germany</option></select>'
'<label class="sr" for="d-l">Language</label>'
'<select id="d-l"><option>English (US)</option><option>English (UK)</option></select>'
'<label class="sr" for="d-m">Currency</label>'
'<select id="d-m">' + cur + '</select>'
'</div></div>'
'<div class="shell foot-base">'
'<span>&copy; 2026 VISIONARY OBJECT</span>'
'<span>DIMENSIONS IN INCHES AND CM</span>'
'<span><a href="#/info/user-agreement">USER AGREEMENT</a> &middot; '
'<a href="#/info/privacy">PRIVACY POLICY</a> &middot; '
'<button type="button" id="ckPrefs">COOKIE PREFERENCES</button> &middot; '
'<a href="#/sitemap">SITE MAP</a></span>'
'</div></footer>')


GRAIN = ("url(\"data:image/svg+xml;utf8,"
         "%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E"
         "%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='3' stitchTiles='stitch'/%3E"
         "%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.85'/%3E%3C/svg%3E\")")

RAIL = '<div class="rail" aria-hidden="true">' + "".join(f'<i style="top:{y}px"></i>' for y in range(0, 1200, 16)) + '<b>SCALE · INCH</b></div>'


APP_JS = r"""
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const RM = matchMedia('(prefers-reduced-motion: reduce)');
const app = $('#app');

const CATNAME = { tablo:'Paintings & Prints', obje:'Handmade Objects', belge:'Documents',
                  rugs:'Persian Rug', lighting:'Lighting', sculpture:'Sculpture',
                  new:'New Arrivals', museum:'The Museum' };
const ROLE = { tam:'full view', aci:'angled view', 'olcu-y':'width measurement', 'olcu-d':'height measurement',
               detay:'detail', imza:'signature', plaka:"maker's plaque", arka:'reverse',
               etiket:'back label', sertifika:'certificate', duvar:'in situ' };


/* ---- image helpers: every <img> carries its own intrinsic size ---- */
const pic = (o, size, alt, extra) => o
  ? `<img src="${o[size]}" ${size === 'c' ? `srcset="${o.c} 700w, ${o.f} 1500w" sizes="(max-width:760px) 50vw, 25vw"` : ''}
       width="${o.w}" height="${o.h}" alt="${alt}" ${extra || 'loading="lazy" decoding="async"'}>`
  : '';
/* Kapak, ilanin ilk karesidir. Panelde kareleri surukleyip sirasini
   degistirmek kapagi degistirir; kart, arama, muze hepsi buraya bakar. */
const cover = d => d.cov || (d.img && d.img[0]) || null;

const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c =>
  ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c]));
const toCm = v => Math.round(v * 2.54 * 100) / 100;
const creatorOf = d => d.creator || 'Unknown';

/* Fiyat ve indirim yazimi. Tek yerde durur ki kart, urun sayfasi ve hizli
   bakis ayni cumleyi kursun. Rakamlar tabular-nums ile hizalanir. */
const paraYaz = (v, cur) => {
  try { return new Intl.NumberFormat('en-US', {style:'currency', currency:cur||'USD',
        maximumFractionDigits:0}).format(v); }
  catch(e) { return '$' + Math.round(v).toLocaleString('en-US'); }
};
const indirimOran = d => (d.priceWas && d.price && d.priceWas > d.price)
  ? Math.round((1 - d.price / d.priceWas) * 100) : 0;
function fiyatHtml(d, buyuk) {
  if (d.sold) return '<b class="p-sold">Sold</b>';
  if (d.reserved) return '<b class="p-res">Reserved</b>';
  if (d.price == null) return (buyuk ? '<b>Price Upon Request</b>' : '<span>Price Upon Request</span>');
  const o = indirimOran(d);
  const simdi = '<b class="p-now">' + paraYaz(d.price, d.cur) + '</b>';
  if (!o) return buyuk ? simdi : '<span class="p-now">' + paraYaz(d.price, d.cur) + '</span>';
  return simdi + ' <s class="p-was">' + paraYaz(d.priceWas, d.cur) + '</s>' +
         ' <em class="p-off">' + o + '% off' + (d.sale && d.sale.rozet ? ' &middot; ' + esc(d.sale.rozet) : '') + '</em>';
}
/* Tek tikla satin alinabilir mi. Dort sart birden: odeme panelden acik,
   bu eserde tek tikla satis isaretli, fiyati var, ve hala satista.
   Buradaki karar sadece dugmeyi gostermek icin; gercek kontrol sunucuda. */
function satinAlinirMi(d) {
  const acik = (typeof AYAR !== 'undefined') && AYAR && AYAR.odeme_acik === 'evet';
  return !!(acik && d.buy && d.price != null && !d.sold && !d.reserved);
}

const shotList = d => Object.entries(d.roles).map(([k, v]) => `${v} ${ROLE[k] || k}`).join(', ');

/* ---------------- card ---------------- */
function card(d, i) {
  const img = cover(d);
  return `<article class="work up" data-io data-vo-kart="${d.slug}" style="--i:${i % 4}">
    <div class="work-fig msk" style="--i:${i % 8}">${pic(img, 'c', esc(d.title))}</div>
    <button class="fav" type="button" data-slug="${d.slug}" data-on="${FAV.has(d.slug) ? 1 : 0}" aria-label="Save ${esc(d.title)} to favorites">${ICON_HEART}</button>
    <button class="qv" type="button" data-qv="${d.slug}" aria-label="Quick view: ${esc(d.title)}">${ICON_EYE}</button>
    <h3 class="ttl"><a href="#/item/${d.slug}" data-pdp="${d.slug}">${esc(creatorOf(d))}</a></h3>
    <p class="by">${esc(d.title)}${d.period && !d.title.includes(d.period) ? ', ' + esc(d.period) : ''}</p>
    <p class="spec">${d.shots} photographs${d.dims ? `&nbsp;&middot; ${d.dims[1]} &times; ${d.dims[0]} in` : ''}</p>
    <p class="price"><span data-vo="fiyat">${fiyatHtml(d, false)}</span><em>${d.doc ? 'Certificate' : ''}</em></p>
  </article>`;
}

/* ---------------- HOME ---------------- */
function viewHome() {
  const hero = DATA.find(d => d.no === 47) || DATA[0];
  const fresh = DATA.slice().sort((a, b) => b.no - a.no).slice(0, 10);
  const count = k => DATA.filter(d => d.cat === k).length;
  const documented = DATA.filter(d => d.doc).length;
  const shots = DATA.reduce((s, d) => s + d.shots, 0);

  const tiles = ['tablo', 'obje', 'belge'].map((k, i) => {
    const ex = DATA.find(d => d.cat === k && cover(d));
    return `<a class="tile up" style="--i:${i}" href="#/browse?cat=${k}">
      <figure class="msk" style="--i:${i}">${pic(cover(ex), 'c', esc(ex ? ex.title : ''))}</figure>
      <figcaption><span class="name">${CATNAME[k]}</span><span class="cnt">${count(k)} ${count(k)===1?'item':'items'}</span></figcaption></a>`;
  }).join('');

  return `
<section class="hero" data-io aria-labelledby="h-hero">
  <div class="hero-in">
    <div class="hero-media msk">${pic(cover(hero), 'f', esc(hero.title), 'fetchpriority="high" decoding="async"')}</div>
    <div class="hero-copy">
      <p class="eyebrow up">${DATA.length} Items For Sale</p>
      <h1 id="h-hero"><span class="rv"><span>Extraordinary Finds,</span></span><span class="rv"><span style="--i:1"><em>One</em> of a Kind.</span></span></h1>
      <p class="lede up" style="--i:2">Antique paintings, prints, works on paper, objects and documents, offered directly by the collector who assembled them.</p>
      <div class="hero-cta up" style="--i:3">
        <a class="btn btn--fill" href="#/browse">Shop Now <span class="arw" aria-hidden="true">→</span></a>
        <a class="btn btn--line" href="#/item/${hero.slug}">View Featured Item</a>
      </div>
    </div>
  </div>
</section>

<section class="sec" data-io aria-labelledby="h-cat">
  <div class="shell">
    <div class="sec-head">
      <h2 id="h-cat" class="rv"><span>Shop by Category</span></h2>
      <a class="lnk up" href="#/browse"><span>View All</span> <span class="arw" aria-hidden="true">→</span></a>
    </div>
    <div class="tiles">${tiles}
      <div class="tile-soon up" style="--i:3">
        <div><h3>More Categories Coming Soon</h3>
          <p>Persian rugs, lighting and sculpture from the same collection are being catalogued and will be listed shortly. Contact the seller for early access.</p></div>
        <div class="soon-rows">
          <div><span>Persian Rug</span><span>coming soon</span></div>
          <div><span>Lighting</span><span>coming soon</span></div>
          <div><span>Sculpture</span><span>coming soon</span></div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="sec sec--paper" data-io aria-labelledby="h-new">
  <div class="shell"><div class="sec-head">
    <h2 id="h-new" class="rv"><span>See What's New</span></h2>
    <div style="display:flex;align-items:center;gap:var(--gap-m)">
      <div class="rail-nav" role="group" aria-label="Scroll the rail">
        <button type="button" data-rail="-1" aria-label="Previous">${ICON_LEFT}</button>
        <button type="button" data-rail="1" aria-label="Next">${ICON_RIGHT}</button>
      </div>
      <a class="lnk up" href="#/browse?cat=new"><span>All New Arrivals</span> <span class="arw" aria-hidden="true">→</span></a>
    </div></div></div>
  <div class="shell"><div class="rail-scroll" tabindex="0" role="region" aria-label="New arrivals, scrolls horizontally">
    ${fresh.map(card).join('')}
  </div></div>
</section>

<section class="sec" data-io aria-labelledby="h-coll">
  <div class="shell">
    <div class="sec-head">
      <h2 id="h-coll" class="rv"><span>Now Trending</span></h2>
      <a class="lnk up" href="#/collections"><span>View All Collections</span> <span class="arw" aria-hidden="true">&#8594;</span></a>
    </div>
    <div class="colls">${COLLECTIONS.slice(0, 4).map((c, i) => {
      const items = collItems(c); const ex = items.find(d => cover(d));
      return `<a class="coll up" style="--i:${i}" href="#/collection/${c.slug}">
        <figure class="msk" style="--i:${i}">${pic(cover(ex), 'c', '')}</figure>
        <figcaption><b>${esc(c.name)}</b><span>${items.length} ${items.length === 1 ? 'item' : 'items'}</span>
        <span class="cta">Shop the Collection</span></figcaption></a>`;
    }).join('')}</div>
  </div>
</section>

<section class="sec sec--paper" data-io aria-labelledby="h-trend">
  <div class="shell">
    <div class="sec-head"><h2 id="h-trend" class="rv"><span>Trending Searches</span></h2></div>
    <div class="chips up">${TRENDING.map(t => `<a href="#/browse?q=${encodeURIComponent(t)}">${esc(t)}</a>`).join('')}</div>
  </div>
</section>

<section class="edit" data-io aria-labelledby="h-edit">
  <div class="edit-fig msk">${pic(cover(DATA.find(d => d.no === 17) || DATA[0]), 'f', '')}</div>
  <div class="edit-in">
    <p class="eyebrow up">Editor's Pick</p>
    <h2 id="h-edit" class="rv"><span>The Signed Edition</span></h2>
    <p class="up" style="--i:1">Every piece in the collection that carries the artist's own pencil signature and an edition number in the margin, from a 1973 charcoal numbered 20 of 200 to an artist's proof pulled outside an edition of fifty.</p>
    <a class="btn btn--fill up" style="--i:2" href="#/collection/signed-and-numbered">Shop the Collection <span class="arw" aria-hidden="true">&#8594;</span></a>
  </div>
</section>

<section class="sec sec--band" data-io aria-labelledby="h-deals">
  <div class="shell">
    <div class="sec-head"><h2 id="h-deals" class="rv"><span>Explore the Collection</span></h2>
      <div class="rail-nav" role="group" aria-label="Scroll the rail">
        <button type="button" data-rail2="-1" aria-label="Previous">${ICON_LEFT}</button>
        <button type="button" data-rail2="1" aria-label="Next">${ICON_RIGHT}</button></div>
    </div>
    <div class="tabs" role="tablist" aria-label="Category">
      ${['tablo','obje','belge'].map((k, i) => `<button type="button" role="tab" data-tab="${k}"
        aria-selected="${i === 0}" aria-controls="tp-${k}" id="tb-${k}">${CATNAME[k]} (${DATA.filter(d => d.cat === k).length})</button>`).join('')}
    </div>
    ${['tablo','obje','belge'].map((k, i) => `<div id="tp-${k}" role="tabpanel" aria-labelledby="tb-${k}" ${i ? 'hidden' : ''}>
      <div class="rail-scroll rail2" tabindex="0" role="region" aria-label="${CATNAME[k]}, scrolls horizontally">
        ${DATA.filter(d => d.cat === k).sort((a, b) => (b.img.length ? 1 : 0) - (a.img.length ? 1 : 0) || b.shots - a.shots).slice(0, 10).map(card).join('')}
      </div></div>`).join('')}
  </div>
</section>

${RECENT.length > 1 ? `<section class="sec" data-io aria-labelledby="h-rv">
  <div class="shell"><div class="sec-head"><h2 id="h-rv" class="rv"><span>Recently Viewed</span></h2></div>
    <div class="grid-works">${RECENT.map(s => DATA.find(d => d.slug === s)).filter(Boolean).slice(0, 4).map(card).join('')}</div>
  </div></section>` : ''}

${protectionBlock()}`;
}
"""

APP_JS += r"""
/* ---------------- BROWSE (category listing) ---------------- */
const SORTS = {
  recommended: ['Recommended', (a, b) => (b.doc ? 1 : 0) - (a.doc ? 1 : 0) || b.shots - a.shots || a.no - b.no],
  newest: ['Newest', (a, b) => b.no - a.no],
  oldest: ['Oldest', (a, b) => a.no - b.no],
  photos: ['Most Photographs', (a, b) => b.shots - a.shots || a.no - b.no],
  /* Fiyati olmayan ilanlar fiyat siralamasinda en sona duser; bos alan
     yuzunden pahali ya da ucuz gorunmesinler. */
  priceAsc: ['Price, Low to High', (a, b) =>
    (a.price == null) - (b.price == null) || (a.price ?? 0) - (b.price ?? 0) || a.no - b.no],
  priceDesc: ['Price, High to Low', (a, b) =>
    (a.price == null) - (b.price == null) || (b.price ?? 0) - (a.price ?? 0) || a.no - b.no],
  discount: ['Biggest Reduction', (a, b) => indirimOran(b) - indirimOran(a) || a.no - b.no],
};
const PERPAGE = [24, 48, 60];
const SWATCH = { Gray:'#8a8a8a', Brown:'#78482a', Black:'#1b1b1b', Beige:'#decaa6', Blue:'#2c5496',
  Purple:'#6e3c8c', Orange:'#de7828', Red:'#aa2828', Pink:'#e896aa', Green:'#3c783c',
  Gold:'#c49e4a', Yellow:'#e8c83c', White:'#f6f6f4', Silver:'#babec2' };

const ARTISTS = [...new Set(DATA.map(d => d.creator).filter(Boolean))].sort((a, b) => a.localeCompare(b));

const FGROUPS = [
  { id:'cat', name:'Category', open:true,
    opts:[['tablo','Paintings & Prints'],['obje','Handmade Objects'],['belge','Documents']],
    test:(d,v)=>d.cat===v },
  { id:'subject', name:'Art Subject', open:true,
    opts:[['landscape','Landscape'],['figurative','People'],['architecture','Architecture'],
          ['seascape','Water & Boats'],['still-life','Still Life'],['animal','Animals'],
          ['portrait','Portrait'],['abstract','Abstract'],['nude','Nude'],['document','Historical Documents']],
    test:(d,v)=>d.subject.includes(v) },
  { id:'medium', name:'Medium', open:true,
    opts:[['oil','Oil Paint'],['watercolour','Watercolor'],['print','Prints & Works on Paper'],
          ['charcoal','Charcoal & Drawing'],['canvas','Canvas'],['paper','Paper'],
          ['panel','Wood Panel'],['textile','Textile & Needlework'],['ink','Ink']],
    test:(d,v)=>d.medium2.includes(v) },
  { id:'style', name:'Style',
    opts:[['asian','Asian'],['modern','Modern'],['old-masters','Old Masters'],
          ['contemporary','Contemporary'],['impressionist','Impressionist'],
          ['art-nouveau','Art Nouveau'],['folk','Folk & Naive'],['surrealist','Surrealist']],
    test:(d,v)=>d.style.includes(v) },
  { id:'period', name:'Period',
    opts:[['18th-and-earlier','18th Century and Earlier'],['19th','19th Century'],
          ['20th','20th Century'],['21st','21st Century and Contemporary']],
    test:(d,v)=>d.period2===v },
  { id:'size', name:'Size',
    opts:[['small','Small (Under 24 in.)'],['medium','Medium (24 to 48 in.)'],
          ['large','Large (48 to 72 in.)'],['oversized','Oversized (72 in. and Above)']],
    test:(d,v)=>d.size===v },
  { id:'orientation', name:'Orientation',
    opts:[['vertical','Vertical'],['horizontal','Horizontal'],['square','Square']],
    test:(d,v)=>d.orient===v },
  { id:'color', name:'Color', kind:'swatch',
    opts:Object.keys(SWATCH).map(c => [c, c]),
    test:(d,v)=>(d.color||[]).includes(v) },
  { id:'framing', name:'Framing',
    opts:[['framed','Frame Included'],['unframed','Unframed']],
    test:(d,v)=>d.framing.includes(v) },
  { id:'documentation', name:'Documentation',
    opts:[['sertifika','Certificate of Authenticity'],['etiket','Back Label'],
          ['imza','Signature Photographed'],['plaka',"Maker's Plaque"],['arka','Reverse Photographed']],
    test:(d,v)=>(d.roles[v]||0)>0 },
  { id:'artist', name:'Artist', kind:'search',
    opts:ARTISTS.map(a => [a, a]),
    test:(d,v)=>d.creator===v },
  { id:'price', name:'Price',
    opts:[['p1','Under $1,000'],['p2','$1,000 - $5,000'],['p3','$5,000 - $15,000'],
          ['p4','$15,000 and above'],['ask','Price Upon Request']],
    test:(d,v)=>{ if (d.price == null) return v === 'ask';
      return v==='p1' ? d.price < 1000 : v==='p2' ? (d.price >= 1000 && d.price < 5000)
           : v==='p3' ? (d.price >= 5000 && d.price < 15000) : v==='p4' ? d.price >= 15000 : false; } },
  { id:'offer', name:'Offers',
    opts:[['sale','Reduced Now'],['available','Available'],['sold','Sold']],
    test:(d,v)=>v==='sale' ? indirimOran(d) > 0 : v==='sold' ? !!d.sold : !(d.sold) },
  { id:'record', name:'Item Details',
    opts:[['creator','Creator Identified'],['period','Dated Work'],
          ['edition','Numbered Edition'],['dims','Dimensions Listed'],['bio','Artist Biography']],
    test:(d,v)=>v==='dims'?!!d.dims:!!d[v] },
  { id:'photos', name:'Photographs',
    opts:[['s','1 photograph'],['m','2 - 3 photographs'],['l','4 photographs and up']],
    test:(d,v)=>v==='s'?d.shots<=1:v==='m'?(d.shots>=2&&d.shots<=3):d.shots>=4 },
  { id:'location', name:'Item Location',
    opts:[['virginia','Virginia, United States']],
    test:()=>true },
];

function parseQ(q) {
  const o = { f:{}, sort:'recommended', p:1, per:24, term:'' };
  new URLSearchParams(q || '').forEach((v, k) => {
    if (k === 'sort') o.sort = SORTS[v] ? v : 'recommended';
    else if (k === 'page') o.p = Math.max(1, parseInt(v) || 1);
    else if (k === 'per') o.per = PERPAGE.includes(+v) ? +v : 24;
    else if (k === 'q') o.term = v;
    else if (k === 'cat' && ['rugs','lighting','sculpture','new','museum'].includes(v)) o.special = v;
    else (o.f[k] = o.f[k] || []).push(v);
  });
  return o;
}
function buildQ(st) {
  const p = new URLSearchParams();
  if (st.special) p.set('cat', st.special);
  Object.entries(st.f).forEach(([k, arr]) => arr.forEach(v => p.append(k, v)));
  if (st.term) p.set('q', st.term);
  if (st.sort !== 'recommended') p.set('sort', st.sort);
  if (st.per !== 24) p.set('per', st.per);
  if (st.p > 1) p.set('page', st.p);
  const s = p.toString();
  return '#/browse' + (s ? '?' + s : '');
}
function filterList(st) {
  let list = DATA.slice();
  if (st.special === 'new') list = list.sort((a, b) => b.no - a.no).slice(0, 12);
  if (['rugs','lighting','sculpture','museum'].includes(st.special)) list = [];
  FGROUPS.forEach(g => {
    const sel = st.f[g.id];
    if (sel && sel.length) list = list.filter(d => sel.some(v => g.test(d, v)));
  });
  if (st.term) {
    const q = st.term.toLowerCase();
    list = list.filter(d => (d.title + ' ' + d.desc + ' ' + d.creator + ' ' + d.medium + ' ' +
      d.catEn + ' ' + d.label + ' ' + d.edition + ' ' + (d.color || []).join(' ') + ' ' +
      d.subject.join(' ') + ' ' + d.medium2.join(' ') + ' ' + d.style.join(' ')).toLowerCase().includes(q));
  }
  return list.sort(SORTS[st.sort][1]);
}

function viewBrowse(q) {
  const st = parseQ(q);
  const list = filterList(st);
  const pages = Math.max(1, Math.ceil(list.length / st.per));
  const page = Math.min(st.p, pages);
  const slice = list.slice((page - 1) * st.per, page * st.per);
  const heading = st.special ? CATNAME[st.special]
    : (st.f.cat && st.f.cat.length === 1 ? CATNAME[st.f.cat[0]] : 'All Items');

  /* counts are computed against everything EXCEPT this group, the way 1stDibs does it */
  const baseFor = gid => {
    const s2 = { ...st, f: Object.fromEntries(Object.entries(st.f).filter(([k]) => k !== gid)) };
    return filterList(s2);
  };
  const filters = FGROUPS.map(g => {
    const base = baseFor(g.id);
    const rows = g.opts.map(([v, label]) => {
      const n = base.filter(d => g.test(d, v)).length;
      const on = (st.f[g.id] || []).includes(v);
      if (g.kind === 'swatch') {
        return `<label class="sw-l" title="${label} (${n})"><input type="checkbox" data-f="${g.id}" value="${v}" ${on ? 'checked' : ''} ${n ? '' : 'disabled'}>
          <i style="background:${SWATCH[v]}"></i><span class="sr">${label}, ${n} items</span></label>`;
      }
      return `<li${n ? '' : ' data-zero'}><label class="fopt"><input type="checkbox" data-f="${g.id}" value="${v}" ${on ? 'checked' : ''} ${n || on ? '' : 'disabled'}>
        <span>${esc(label)}</span><span class="n">${n.toLocaleString('en-US')}</span></label></li>`;
    }).join('');
    const body = g.kind === 'swatch' ? `<div class="swatches">${rows}</div>`
      : (g.kind === 'search'
        ? `<div class="fsub"><label class="sr" for="fs-${g.id}">Search ${g.name}</label>
             <input id="fs-${g.id}" type="search" placeholder="Search ${g.name}" data-fsearch="${g.id}"></div>
           <ul data-list="${g.id}">${rows}</ul>`
        : `<ul>${rows}</ul>`);
    const back = (g.id === 'cat' && (st.f.cat || st.special))
      ? `<p class="fback"><a href="#/browse">Back to All Items</a></p>` : '';
    return `<details class="fgroup" ${g.open ? 'open' : ''}>
      <summary>${g.name}</summary>${back}${body}</details>`;
  }).join('');

  const active = [];
  Object.entries(st.f).forEach(([k, arr]) => arr.forEach(v => {
    const g = FGROUPS.find(x => x.id === k);
    const label = g && (g.opts.find(o => o[0] === v) || [])[1];
    if (label) active.push(`<button class="chip-x" type="button" data-rm="${k}:${v}"><b>${label}</b><span aria-hidden="true">×</span><span class="sr">remove</span></button>`);
  }));
  if (st.term) active.push(`<button class="chip-x" type="button" data-rm="q:"><b>“${esc(st.term)}”</b><span aria-hidden="true">×</span><span class="sr">remove</span></button>`);

  const pager = pages > 1 ? `<nav class="pager" aria-label="Pagination">
    <button type="button" data-p="${page - 1}" ${page === 1 ? 'disabled' : ''} aria-label="Previous page">${ICON_LEFT}</button>
    ${Array.from({ length: pages }, (_, i) => `<button type="button" data-p="${i + 1}" ${i + 1 === page ? 'aria-current="page"' : ''}>${i + 1}</button>`).join('')}
    <button type="button" data-p="${page + 1}" ${page === pages ? 'disabled' : ''} aria-label="Next page">${ICON_RIGHT}</button>
  </nav>` : '';

  /* subcategory tiles follow the current category, the way 1stDibs' do */
  const curCat = st.special || (st.f.cat && st.f.cat.length === 1 ? st.f.cat[0] : '');
  const SUBTILES = {
    tablo:  [['subject','landscape','Landscape'],['subject','figurative','People'],
             ['medium','print','Prints & Works on Paper'],['medium','watercolour','Watercolor'],
             ['subject','still-life','Still Life']],
    obje:   [['medium','textile','Textile & Needlework'],['framing','framed','Framed Panels']],
    belge:  [['subject','document','Diplomas & Certificates']],
    '':     [['cat','tablo','Paintings & Prints'],['cat','obje','Handmade Objects'],
             ['cat','belge','Documents'],['documentation','sertifika','With Certificate'],
             ['documentation','imza','Signed']],
  };
  const usedTile = new Set();
  const tiles2 = (SUBTILES[curCat] || SUBTILES['']).map(([g, v, label]) => {
    const grp = FGROUPS.find(x => x.id === g);
    const pool = DATA.filter(d => (!curCat || ['rugs','lighting','sculpture','new','museum'].includes(curCat) || d.cat === curCat) && grp.test(d, v));
    const withImg = pool.filter(d => cover(d));
    const ex = withImg.find(d => !usedTile.has(d.no)) || withImg[0];
    if (ex) usedTile.add(ex.no);
    const href = '#/browse?' + (curCat && g !== 'cat' ? 'cat=' + curCat + '&' : '') + g + '=' + encodeURIComponent(v);
    return `<a class="subcat" href="${href}">
      <figure>${pic(cover(ex), 't', '')}</figure>
      <div><b>${esc(label)}</b><span>${pool.length} ${pool.length === 1 ? 'item' : 'items'}</span></div></a>`;
  }).join('');
  const subcats = tiles2;

  /* iki ayri bos durum: henuz kataloglanmamis kategori, ve sonuc vermeyen arama */
  const soonCat = ['rugs', 'lighting', 'sculpture'].includes(st.special);
  const soonWhat = { rugs: 'Persian rugs from this collection are',
                     lighting: 'Lighting from this collection is',
                     sculpture: 'Sculpture from this collection is' }[st.special];
  const empty = soonCat
    ? `<div class="empty"><h2>Being Catalogued</h2>
        <p>${soonWhat} being photographed and measured, and will be listed shortly.
           Contact the seller for early access, or browse the rest of the collection.</p>
        <p style="margin-block-start:1.2rem">
          <button class="btn btn--fill" type="button" data-ask>Ask What Is Coming <span class="arw" aria-hidden="true">&#8594;</span></button>
          <a class="btn btn--line" href="#/browse">Browse All 49 Items</a></p></div>`
    : `<div class="empty"><h2>No Items Found</h2>
        <p>${st.term ? `Nothing in the collection matches &ldquo;${esc(st.term)}&rdquo;.` : 'No item matches every filter you have chosen.'}
           Try fewer filters, or browse the whole collection of ${DATA.length} pieces.</p>
        <p style="margin-block-start:1.2rem">
          <a class="btn btn--fill" href="#/browse">Clear Everything <span class="arw" aria-hidden="true">&#8594;</span></a>
          <a class="btn btn--line" href="#/creators">Browse by Artist</a></p></div>`;

  /* henuz ilan girilmemis kategoride filtre, siralama ve alt kategori
     kutularini gostermek yaniltici oluyordu: sadece bildirim kaliyor */
  if (soonCat) return `<div class="shell">
  <nav class="crumbs" aria-label="Breadcrumbs"><a href="#/">Home</a><i>/</i><a href="#/browse">All Items</a><i>/</i><span aria-current="page">${heading}</span></nav>
  <div class="coll-top"><h1>${heading}</h1></div>
  ${empty}
  <section class="pdp-more" data-io>
    <h2>In the Meantime</h2>
    <div class="grid-works">${DATA.slice(0, 4).map(card).join('')}</div>
  </section>
</div>`;

  return `<div class="shell">
  <nav class="crumbs" aria-label="Breadcrumbs"><a href="#/">Home</a><i>/</i>${st.special || (st.f.cat && st.f.cat.length === 1) ? `<a href="#/browse">All Items</a><i>/</i>` : ''}<span aria-current="page">${heading}</span></nav>
  <div class="coll-top">
    <h1>${heading}</h1>
    <button class="btn-save" type="button">${ICON_HEART} Save Search</button>
  </div>
  <div class="subcats">${subcats}</div>
  <div class="coll-body">
    <button class="filter-btn" type="button" id="filterBtn" aria-expanded="false" aria-controls="filterPanel">
      ${ICON_FILTER} Filters${active.length ? ' (' + active.length + ')' : ''}</button>
    <aside class="filters" id="filterPanel" aria-label="Filters">
      <div class="filters-top">
        <h2>Filters</h2>
        <button class="iconb" type="button" id="filterClose" aria-label="Close filters">${ICON_X}</button>
      </div>
      <form class="fsearch" onsubmit="return false">
        <label class="sr" for="fq">Search within results</label>${ICON_SEARCH}
        <input id="fq" type="search" placeholder="Search within ${list.length} results" value="${esc(st.term)}">
      </form>
      ${filters}
      <div class="filters-foot"><button class="btn btn--fill" type="button" id="filterDone" style="inline-size:100%">Show ${list.length} ${list.length === 1 ? 'Result' : 'Results'}</button></div>
    </aside>
    <div>
      <div class="sortbar">
        <p class="count"><b>${list.length.toLocaleString('en-US')}</b> ${heading} For Sale</p>
        <div class="selwrap">
          <span class="sel"><label class="sr" for="srt">Sort by</label>
            <select id="srt">${Object.entries(SORTS).map(([k, v]) => `<option value="${k}" ${k === st.sort ? 'selected' : ''}>${v[0]}</option>`).join('')}</select></span>
          <span class="sel"><label class="sr" for="per">Items per page</label>
            <select id="per">${PERPAGE.map(n => `<option value="${n}" ${n === st.per ? 'selected' : ''}>${n} per page</option>`).join('')}</select></span>
        </div>
      </div>
      ${active.length ? `<div class="chips-active">${active.join('')}<button class="chip-x" type="button" data-rm="*"><b>Clear All</b></button></div>` : ''}
      ${slice.length ? `<div class="grid-works" style="padding-block:var(--gap-m)">${slice.map(card).join('')}</div>` : empty}
      ${pager}
    </div>
  </div>
  ${seoBlock(heading, list)}
</div>`;
}

/* --- related searches, as 1stDibs has under a listing page --- */
function relatedBlock(heading, list) {
  const chips = [];
  const push = (label, href) => { if (!chips.some(c => c[0] === label)) chips.push([label, href]); };
  [...new Set(list.map(d => d.creator).filter(Boolean))].slice(0, 6)
    .forEach(n => push(n, `#/browse?artist=${encodeURIComponent(n)}`));
  const cnt = (arr, key) => {
    const m = {};
    list.forEach(d => (d[key] || []).forEach(v => m[v] = (m[v] || 0) + 1));
    return Object.entries(m).sort((a, b) => b[1] - a[1]);
  };
  cnt(null, 'subject').slice(0, 5).forEach(([v]) => push((SUBLAB[v] || v) + ' ' + heading, `#/browse?subject=${v}`));
  cnt(null, 'medium2').slice(0, 4).forEach(([v]) => push((MEDLAB2[v] || v) + ' ' + heading, `#/browse?medium=${v}`));
  cnt(null, 'style').slice(0, 3).forEach(([v]) => push((STYLAB[v] || v) + ' ' + heading, `#/browse?style=${v}`));
  cnt(null, 'color').slice(0, 4).forEach(([v]) => push(v + ' ' + heading, `#/browse?color=${v}`));
  if (!chips.length) return '';
  return `<div class="related">
    <h2>Popular Searches in ${esc(heading)}</h2>
    <div class="chips">${chips.slice(0, 18).map(([t, h]) => `<a href="${h}">${esc(t)}</a>`).join('')}</div>
    <p class="related-all"><a href="#/sitemap">View All Popular&nbsp;<b>${esc(heading)}</b>&nbsp;Searches</a></p>
  </div>`;
}

/* --- SEO copy + Q&A at the foot of a listing page, as 1stDibs has --- */
function seoBlock(heading, list) {
  const creators = [...new Set(list.map(d => d.creator).filter(Boolean))];
  const media = [...new Set(list.flatMap(d => d.medium2))];
  const MEDLAB = { oil:'oil', watercolour:'watercolour', print:'prints and works on paper',
    charcoal:'charcoal', canvas:'canvas', paper:'paper', panel:'wood panel',
    textile:'textile and needlework', ink:'ink' };
  const framed = list.filter(d => d.framing.includes('framed')).length;
  const withDoc = list.filter(d => d.doc).length;
  const QA = [
    [`How much do ${heading.toLowerCase()} cost?`,
     `Every piece on this site is unique and priced individually, so listings show Price Upon Request. Use Contact Seller or Suggest a Price on any listing and you will have a figure the same day.`],
    [`Are the frames included?`,
     `Yes. ${framed} of the ${list.length} ${list.length === 1 ? 'item' : 'items'} in this selection are sold in the frame shown in the photographs. Where a piece is unframed the listing says Unframed.`],
    [`How do I know a piece is authentic?`,
     `Signatures, edition numbers, back labels, gallery stamps and certificates are photographed and published with the listing. ${withDoc} ${withDoc === 1 ? 'item' : 'items'} in this selection ${withDoc === 1 ? 'travels' : 'travel'} with a certificate of authenticity. Nothing is described that is not shown.`],
    [`Can I see more photographs before I buy?`,
     `Yes. Ask and the seller will send further images, video, and a written condition report before any payment is made.`],
    [`How are they shipped?`,
     `Framed work travels crated; works on paper travel flat between boards. Every shipment is insured for its full agreed value and tracked. Shipping is quoted per item once the destination is known.`],
  ];
  return `<section class="seo">
    <h2>${esc(heading)} for Sale</h2>
    <p>Browse ${list.length} ${esc(heading.toLowerCase())} from a single private collection, offered directly by the collector. ${creators.length ? `Named creators in this selection include ${creators.slice(0, 5).map(esc).join(', ')}${creators.length > 5 ? ' and others' : ''}.` : ''} ${media.length ? `Media represented include ${media.slice(0, 5).map(m => MEDLAB[m] || m).join(', ')}.` : ''}</p>
    <p>Every listing is one of a kind: when a piece sells it is gone, and there is no second example behind it. Pieces are photographed in full, at an angle, and against their signatures, labels and certificates, so that what you read in the description is visible in the images. Prices are upon request and offers are welcome.</p>
    <div class="qa">
      <h2>Questions &amp; Answers</h2>
      ${QA.map(([q, a]) => `<details><summary>${esc(q)}</summary><p>${esc(a)}</p></details>`).join('')}
    </div>
    ${relatedBlock(heading, list)}
  </section>`;
}
"""

APP_JS += VIEWS2

APP_JS += r"""
/* ---------------- ITEM PAGE ---------------- */
const SUBLAB = { landscape:'Landscape', figurative:'People', architecture:'Architecture',
  seascape:'Water & Boats', 'still-life':'Still Life', animal:'Animals', portrait:'Portrait',
  abstract:'Abstract', nude:'Nude', document:'Historical Documents' };
const STYLAB = { asian:'Asian', modern:'Modern', 'old-masters':'Old Masters', contemporary:'Contemporary',
  impressionist:'Impressionist', 'art-nouveau':'Art Nouveau', folk:'Folk & Naive', surrealist:'Surrealist' };
const MEDLAB2 = { oil:'Oil Paint', watercolour:'Watercolor', print:'Prints & Works on Paper',
  charcoal:'Charcoal & Drawing', canvas:'Canvas', paper:'Paper', panel:'Wood Panel',
  textile:'Textile & Needlework', ink:'Ink' };

const sharedFacets = (a, b) =>
  b.subject.filter(x => a.subject.includes(x)).length * 2 +
  b.medium2.filter(x => a.medium2.includes(x)).length +
  b.style.filter(x => a.style.includes(x)).length * 2 +
  (b.creator && b.creator === a.creator ? 5 : 0);

function viewItem(slug) {
  const d = DATA.find(x => x.slug === slug);
  if (!d) return notFound('That item could not be found. It may have sold.');
  remember(slug);

  const similar = DATA.filter(x => x.cat === d.cat && x.no !== d.no)
    .sort((a, b) => (b.img.length ? 1 : 0) - (a.img.length ? 1 : 0)
      || sharedFacets(d, b) - sharedFacets(d, a) || a.no - b.no);
  const imgs = d.img;
  const thumbs = imgs.map((o, i) => `<button type="button" data-th="${i}" data-full="${o.f}" aria-current="${i === 0}">
      ${pic(o, 't', 'View ' + (i + 1) + ': ' + esc(ROLE[o.rol] || o.rol))}</button>`).join('');

  const row = (dt, dd, cls) => `<div><dt>${dt}</dt><dd class="${cls || ''}">${dd}</dd></div>`;
  const pending = t => `<span class="yok">${t}</span>`;
  const core = [
    row('Creator:', d.creator
      ? `<a href="#/browse?artist=${encodeURIComponent(d.creator)}" class="lnk-in">${esc(d.creator)}</a>`
      : pending('Unknown')),
    d.period ? row('Creation Year:', esc(d.period), 'n') : '',
    row('Dimensions:', d.dims
      ? `Height: ${d.dims[1]} in (${toCm(d.dims[1])} cm)<br>Width: ${d.dims[0]} in (${toCm(d.dims[0])} cm)${d.dimsOf ? '<br><span style="color:var(--ink-3)">' + esc(d.dimsOf) + '</span>' : ''}`
      : pending('Available upon request'), d.dims ? 'n' : ''),
    row('Medium:', d.medium ? esc(d.medium)
      : (d.medium2.length ? d.medium2.map(m => MEDLAB2[m] || m).join(', ') : pending('Available upon request'))),
    d.edition ? row('Edition:', esc(d.edition), 'n') : '',
    d.style.length ? row('Movement &amp; Style:', d.style.map(x => STYLAB[x] || x).join(', ')) : '',
    d.period2 ? row('Period:', ({'18th-and-earlier':'18th Century and Earlier','19th':'19th Century','20th':'20th Century','21st':'21st Century and Contemporary'})[d.period2], 'n') : '',
    row('Condition:', 'Good. Sold in the condition shown in the photographs. Written condition report on request.'),
    row('Gallery Location:', 'Virginia, United States'),
    row('Reference Number:', `VO-${String(d.no).padStart(2, '0')}${d.ref ? ' &middot; ' + esc(d.ref) : ''}`, 'n'),
  ].filter(Boolean).join('');
  const more = [
    d.subject.length ? row('Subject:', d.subject.map(x => SUBLAB[x] || x).join(', ')) : '',
    d.framing.length ? row('Framing:', d.framing.includes('framed') ? 'Frame Included' : 'Unframed') : '',
    row('Orientation:', d.orient ? d.orient.charAt(0).toUpperCase() + d.orient.slice(1) : pending('Available upon request')),
    (d.color || []).length ? row('Dominant Colors:', d.color.map(c =>
      `<span class="dot" style="background:${SWATCH[c] || '#888'}"></span>${c}`).join(' ')) : '',
    d.gallery ? row('Gallery:', esc(d.gallery)) : '',
    d.label ? row('Back Label:', esc(d.label)) : '',
    row('Photographs:', `${d.shots} &middot; ${shotList(d)}`, 'n'),
  ].filter(Boolean).join('');

  const inCart = CART.has(d.slug);
  const saved = FAV.has(d.slug);

  return `
<section class="simbar">
  <div class="shell simbar-in">
    <div><h2>Items Similar to<i>${esc(d.title)}</i></h2>
      <a class="lnk" href="#/browse?cat=${d.cat}"><span>View More</span> <span class="arw" aria-hidden="true">&#8594;</span></a></div>
    <div class="simstrip" role="region" aria-label="Similar items, scrolls horizontally" tabindex="0">
      ${similar.filter(x => cover(x)).slice(0, 12).map(x => `<a href="#/item/${x.slug}" title="${esc(x.title)}">
        ${pic(cover(x), 't', esc(x.title))}</a>`).join('')}
    </div>
  </div>
</section>

<div class="shell">
  <nav class="crumbs" aria-label="Breadcrumbs">
    <a href="#/">Home</a><i>/</i><a href="#/browse">All Items</a><i>/</i>
    <a href="#/browse?cat=${d.cat}">${d.catEn}</a><i>/</i>
    ${d.subject[0] ? `<a href="#/browse?cat=${d.cat}&subject=${d.subject[0]}">${SUBLAB[d.subject[0]] || d.subject[0]}</a><i>/</i>` : ''}
    <span aria-current="page">${d.title.length > 58 ? esc(d.title.slice(0, 56).replace(/[\s,]+$/, '')) + '&hellip;' : esc(d.title)}</span>
  </nav>

  <div class="pdp" data-vo-urun="${d.slug}">
    <div class="gal">
      <div class="thumbs" role="tablist" aria-label="Item photographs">${thumbs}</div>
      <div class="stage">
        ${imgs.length ? `<img id="stageImg" src="${imgs[0].f}" width="${imgs[0].w}" height="${imgs[0].h}"
            alt="${esc(d.title)}" fetchpriority="high" decoding="async" style="view-transition-name:pdp-img">`
          : `<span class="mono" style="font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-3)">Image pending</span>`}
        ${imgs.length > 1 ? `<button class="nav prev" type="button" data-step="-1" aria-label="Previous image">${ICON_LEFT}</button>
          <button class="nav next" type="button" data-step="1" aria-label="Next image">${ICON_RIGHT}</button>` : ''}
        ${imgs.length ? `<span class="idx" id="galIdx">1 of ${imgs.length}</span>
          <div class="loupe" id="loupe" aria-hidden="true"></div>
          <button class="zoomb" type="button" id="zoomBtn" aria-label="Enlarge image">${ICON_ZOOM}</button>` : ''}
      </div>
    </div>

    <div class="buy">
      <div class="buy-top">
        <p class="kicker">${ICON_RULER} One of a Kind &middot; VO-${String(d.no).padStart(2, '0')}</p>
        <div class="buy-save">
          <button class="iconb fav" type="button" data-slug="${d.slug}" data-on="${saved ? 1 : 0}" aria-label="Save ${esc(d.title)} to favorites">${ICON_HEART}</button>

        </div>
      </div>
      <p class="creatorline" data-vo="sanatci">${d.creator
        ? `<a href="#/browse?artist=${encodeURIComponent(d.creator)}">${esc(d.creator)}</a>` : 'Unknown'}</p>
      <h1 data-vo="baslik">${esc(d.title)}</h1>
      <p class="sub" data-vo="donem">${d.period ? esc(d.period) : esc(d.catEn)}</p>
      <p class="in-room">${ICON_RULER}Hung in the collection you can walk through &middot; <a href="museum/index.html">enter the Museum</a></p>
      <p class="askprice"><span data-vo="fiyat">${fiyatHtml(d, true)}</span><span>${d.framing.includes('unframed') ? 'UNFRAMED' : 'FRAME INCLUDED'}</span></p>
      <div class="acts">
        ${satinAlinirMi(d) ? `<button class="btn btn--fill" type="button" data-buy="${d.slug}">Buy Now <span class="arw" aria-hidden="true">&#8594;</span></button>
        <button class="btn btn--line" type="button" data-ask>Contact Seller</button>`
        : `<button class="btn btn--fill" type="button" data-ask>Contact Seller <span class="arw" aria-hidden="true">&#8594;</span></button>
        <button class="btn btn--line" type="button" data-ask="teklif">Suggest a Price</button>`}
        <button class="btn btn--ghost" type="button" data-cart="${d.slug}">${inCart ? 'In Your Cart' : 'Add to Cart'}</button>
      </div>
      <div class="info-card">
        <h2>${ICON_SHIP} Shipping &amp; Returns</h2>
        <p>Crated and insured from Virginia, United States. <button class="lnk-s" type="button" data-det="shipping">Details</button></p>
        <p>Worry-free returns within 14 days of delivery. <button class="lnk-s" type="button" data-det="returns">Details</button></p>
      </div>
      <div class="info-card">
        <h2>${ICON_SHIELD} Shop With Confidence</h2>
        <p>Authenticity Guaranteed, Money Back Guarantee, 24-Hour Cancellation.
          <button class="lnk-s" type="button" data-det="promise">Details</button></p>
        ${d.doc ? `<p><b>Documentation:</b> ${esc(d.doc)}</p>` : ''}
      </div>
      <div class="sellbox">
        <span class="mk" aria-hidden="true">V</span>
        <div><b>Visionary Object</b>
          <span><span class="stars" aria-hidden="true">&#9733;&#9733;&#9733;&#9733;&#9733;</span> 5.0 &middot; ${DATA.length} listings &middot; responds same day</span></div>
      </div>
      <p style="margin-block-start:.9rem"><button class="btn btn--line" type="button" data-ask style="inline-size:100%">Message the Seller</button></p>
      <div class="info-card">
        <h2>Want more images or videos?</h2>
        <p>Request additional images or videos from the seller.</p>
        <p style="margin-block-start:.7rem"><button class="lnk" type="button" data-ask><span>Contact Seller</span> <span class="arw" aria-hidden="true">&#8594;</span></button></p>
      </div>
    </div>

  <div class="pdp-doc">
    <div class="tabs" role="tablist" aria-label="Item information">
      ${[['details','Item Details'], ...(d.bio ? [['artist','Artist']] : []), ['seller','Seller Information'], ['ship','Shipping & Returns']]
        .map(([k, lab], i) => `<button type="button" role="tab" data-ptab="${k}" id="pt-${k}"
          aria-controls="pp-${k}" aria-selected="${i === 0}">${lab}</button>`).join('')}
    </div>

    <div id="pp-details" role="tabpanel" aria-labelledby="pt-details">
      <h2 class="pdp-h">About the Item</h2>
      <!-- d.note BILEREK gosterilmiyor: o alan katalog calismasinin ic notudur
           (dosya adlari, supheler). Yalnizca panelde durur. -->
      <p class="pdp-p" data-vo="aciklama">${esc(d.desc)}</p>
      <dl class="spec">${core}</dl>
      <details class="acc"><summary>More Details</summary><div class="body"><dl class="spec">${more}</dl></div></details>
    </div>

    ${d.bio ? `<div id="pp-artist" role="tabpanel" aria-labelledby="pt-artist" hidden>
      <h2 class="pdp-h">${esc(d.creator)}</h2>
      <p class="pdp-p">${esc(d.bio)}</p>
      <p style="margin-block-start:1.2rem"><a class="btn btn--line" href="#/browse?artist=${encodeURIComponent(d.creator)}">All Works by ${esc(d.creator)} <span class="arw" aria-hidden="true">&#8594;</span></a></p>
    </div>` : ''}

    <div id="pp-seller" role="tabpanel" aria-labelledby="pt-seller" hidden>
      <h2 class="pdp-h">About the Seller</h2>
      <p class="pdp-p">A single private collection in Virginia, United States, offered directly by its owner. Every enquiry is answered personally, usually the same day, and every piece is packed by the same hands that catalogued it.</p>
      <dl class="spec">
        <div><dt>Items listed</dt><dd class="n">${DATA.length}</dd></div>
        <div><dt>With certificate</dt><dd class="n">${DATA.filter(x => x.doc).length}</dd></div>
        <div><dt>Photographs per listing</dt><dd class="n">${Math.round(DATA.reduce((s, x) => s + x.shots, 0) / DATA.length)} average</dd></div>
        <div><dt>Typical response time</dt><dd>Same day</dd></div>
        <div><dt>Ships from</dt><dd>Virginia, United States</dd></div>
      </dl>
    </div>

    <div id="pp-ship" role="tabpanel" aria-labelledby="pt-ship" hidden>
      <h2 class="pdp-h">Shipping &amp; Returns</h2>
      <p class="pdp-p">Shipping is quoted per item once the destination is known. Framed work travels crated with corner protection; works on paper travel flat between acid-free boards. Every shipment is insured for its full agreed value and tracked.</p>
      <p class="pdp-p">Packing takes two to five working days from confirmed payment. Transit is typically five to twelve working days depending on destination and customs. Import duty or VAT in the destination country is payable by the buyer.</p>
      <p class="pdp-p">Return Policy: a return for this item may be initiated within 14 days of delivery. An order may be cancelled free of charge within twenty-four hours of confirmation.</p>
      <p style="margin-block-start:1.2rem"><a class="btn btn--line" href="#/info/shipping">Full Shipping Policy <span class="arw" aria-hidden="true">&#8594;</span></a></p>
    </div>
  </div>
  </div>

  <section class="pdp-more" data-io>
    <h2>More From ${d.catEn}</h2>
    <div class="grid-works">${similar.slice(0, 8).map(card).join('')}</div>
  </section>
</div>`;
}

/* ---------------- router ---------------- */
let booted = false;
function render() {
  const h = location.hash.replace(/^#/, '') || '/';
  const [path, q] = h.split('?');
  let html, t;
  if (path.startsWith('/item/')) { html = viewItem(path.slice(6)); t = 'item'; }
  else if (path.startsWith('/browse')) { html = viewBrowse(q); t = 'browse'; }
  else if (path === '/museum') { location.replace('museum/index.html'); return; }
  else if (path === '/collections') { html = viewCollections(); t = 'collections'; }
  else if (path.startsWith('/collection/')) { html = viewCollection(path.slice(12)); t = 'collection'; }
  else if (path === '/creators') { html = viewCreators(); t = 'creators'; }
  else if (path === '/favorites') { html = viewFavorites(); t = 'favorites'; }
  else if (path === '/cart') { html = viewCart(); t = 'cart'; }
  else if (path === '/account') { html = viewAccount(); t = 'account'; }
  else if (path === '/sitemap') { html = viewSitemap(); t = 'sitemap'; }
  else if (path.startsWith('/info/')) { html = viewInfo(path.slice(6)); t = 'info'; }
  else if (path === '/' || path === '') { html = viewHome(); t = 'home'; }
  else { html = notFound('The address you followed does not exist on this site.'); t = '404'; }
  app.innerHTML = html;
  app.dataset.view = t;
  wire(t);
  const h1 = $('#app h1');
  document.title = (t === 'home' ? '' : (h1 ? h1.innerText.replace(/\s+/g, ' ').trim() + ' · ' : '')) + 'Visionary Object';
  headTags(t, path);
  if (booted) { app.focus({ preventScroll: true }); window.scrollTo(0, 0); }

  observe();
}
/* Her rota icin canonical, aciklama, og/twitter ve schema.org blogu.
   Canonical, o icerigin taranabilir statik adresini gosterir. */
const CATFILE = { tablo:'paintings-and-prints', obje:'handmade-objects', belge:'documents' };
function meta(sel, attr, val) {
  let el = document.head.querySelector(sel);
  if (!el) {
    el = document.createElement('meta');
    const m = sel.match(/\[(name|property)="([^"]+)"\]/);
    if (m) el.setAttribute(m[1], m[2]);
    document.head.appendChild(el);
  }
  el.setAttribute(attr, val);
}
function headTags(t, path) {
  let canon = '', desc = '', img = '', ld = null;
  const d = t === 'item' ? DATA.find(x => x.slug === path.slice(6)) : null;
  if (d) {
    canon = 'item/' + d.slug + '.html';
    desc = 'For sale at Visionary Object - ' + d.title +
      (d.medium ? ', ' + d.medium : '') + ' by ' + (d.creator || 'Unknown') +
      '. One of a kind, offered directly by the collector.';
    const c = cover(d); if (c) img = c.f;
    ld = { '@context':'https://schema.org', '@type':'Product',
      name: d.title, sku: 'VO-' + String(d.no).padStart(2,'0'),
      description: (d.dims ? 'Height ' + d.dims[1] + ' in, width ' + d.dims[0] + ' in. ' : '') + d.desc,
      category: d.catEn, itemCondition: 'https://schema.org/UsedCondition',
      brand: { '@type':'Brand', name: d.creator || 'Unknown' },
      image: (d.img || []).slice(0, 8).map(o => SITE + '/' + o.f),
      offers: { '@type':'Offer', availability:'https://schema.org/InStock',
                priceCurrency:'USD', price:0, url: SITE + '/' + canon } };
  } else if (t === 'browse') {
    const cat = new URLSearchParams(location.hash.split('?')[1] || '').get('cat');
    canon = 'category/' + (CATFILE[cat] || 'all') + '.html';
    desc = 'Browse one-of-a-kind antique paintings, prints, works on paper, handmade '
         + 'objects and historical documents from a single private collection.';
  } else {
    canon = '';
    desc = document.querySelector('meta[name="description"]')?.dataset.home || '';
  }
  const url = SITE + '/' + canon;
  let link = document.head.querySelector('link[rel="canonical"]');
  if (!link) { link = document.createElement('link'); link.rel = 'canonical'; document.head.appendChild(link); }
  link.href = url;
  if (desc) meta('meta[name="description"]', 'content', desc);
  meta('meta[property="og:title"]', 'content', document.title);
  meta('meta[property="og:url"]', 'content', url);
  if (desc) meta('meta[property="og:description"]', 'content', desc);
  meta('meta[name="twitter:card"]', 'content', img ? 'summary_large_image' : 'summary');
  meta('meta[name="twitter:title"]', 'content', document.title);
  if (desc) meta('meta[name="twitter:description"]', 'content', desc);
  if (img) {
    meta('meta[property="og:image"]', 'content', SITE + '/' + img);
    meta('meta[name="twitter:image"]', 'content', SITE + '/' + img);
  } else {
    document.head.querySelector('meta[property="og:image"]')?.remove();
    document.head.querySelector('meta[name="twitter:image"]')?.remove();
  }
  let s = document.getElementById('ldRoute');
  if (ld) {
    if (!s) { s = document.createElement('script'); s.type = 'application/ld+json'; s.id = 'ldRoute'; document.head.appendChild(s); }
    s.textContent = JSON.stringify(ld);
  } else if (s) { s.remove(); }
}
function go(href) {
  if (!document.startViewTransition || RM.matches) { location.hash = href.replace(/^#/, ''); return; }
  return document.startViewTransition(() => { location.hash = href.replace(/^#/, ''); });
}
"""

APP_JS += r"""
/* ---------------- events ---------------- */
let io;
function observe() {
  if (io) io.disconnect();
  io = new IntersectionObserver(es => {
    for (const e of es) if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
  }, { rootMargin: '0px 0px -12% 0px', threshold: 0 });
  $$('[data-io]').forEach(el => io.observe(el));
  requestAnimationFrame(() => { const f = $('[data-io]'); if (f) f.classList.add('in'); });
}

function wire(view) {
  /* tabs (home category rail + pdp panels) */
  const tabSwap = (attr, panelPrefix) => {
    const btns = $$(`[data-${attr}]`);
    btns.forEach(b => b.addEventListener('click', () => {
      btns.forEach(x => {
        const on = x === b;
        x.setAttribute('aria-selected', String(on));
        const pnl = document.getElementById(panelPrefix + x.dataset[attr]);
        if (pnl) pnl.hidden = !on;
      });
    }));
  };
  tabSwap('tab', 'tp-');
  tabSwap('ptab', 'pp-');

  /* every horizontal rail gets its own buttons */
  $$('.rail-scroll').forEach(r => {
    const scope = r.closest('section') || document;
    const btns = [...scope.querySelectorAll('[data-rail],[data-rail2]')];
    if (!btns.length) return;
    const sync2 = () => {
      const max = r.scrollWidth - r.clientWidth - 2;
      btns.forEach(b => {
        const dir = +(b.dataset.rail || b.dataset.rail2);
        b.disabled = (dir < 0 && r.scrollLeft <= 2) || (dir > 0 && r.scrollLeft >= max);
      });
    };
    btns.forEach(b => b.addEventListener('click', () => {
      const t = scope.querySelector('[role="tabpanel"]:not([hidden]) .rail-scroll') || r;
      const c = t.firstElementChild;
      const step = (c ? c.getBoundingClientRect().width + 16 : 260) * 2;
      t.scrollBy({ left: (+(b.dataset.rail || b.dataset.rail2)) * step, behavior: RM.matches ? 'auto' : 'smooth' });
    }));
    r.addEventListener('scroll', () => { clearTimeout(r._t); r._t = setTimeout(sync2, 120); }, { passive: true });
    sync2();
  });

  /* mobile filter sheet */
  const fbtn = $('#filterBtn'), fpanel = $('#filterPanel');
  if (fbtn && fpanel) {
    const openF = on => {
      fpanel.toggleAttribute('data-open', on);
      fbtn.setAttribute('aria-expanded', String(on));
      document.body.style.overflow = on && matchMedia('(max-width:999px)').matches ? 'hidden' : '';
      if (on) fpanel.querySelector('#filterClose').focus();
    };
    fbtn.addEventListener('click', () => openF(!fpanel.hasAttribute('data-open')));
    $('#filterClose').addEventListener('click', () => { openF(false); fbtn.focus(); });
    $('#filterDone').addEventListener('click', () => { openF(false); fbtn.focus(); });
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && fpanel.hasAttribute('data-open')) { openF(false); fbtn.focus(); }
    });
  }

  /* filter option search (Artist) */
  $$('[data-fsearch]').forEach(inp => inp.addEventListener('input', () => {
    const t = inp.value.trim().toLowerCase();
    $$(`[data-list="${inp.dataset.fsearch}"] li`).forEach(li => {
      li.hidden = t && !li.textContent.toLowerCase().includes(t);
    });
  }));

  /* legacy single rail hook (kept for the New Arrivals rail's own buttons) */
  const rail = null;
  if (rail) {
    const sync = () => {
      const max = rail.scrollWidth - rail.clientWidth - 2;
      $$('[data-rail]').forEach(b => {
        const dir = +b.dataset.rail;
        b.disabled = (dir < 0 && rail.scrollLeft <= 2) || (dir > 0 && rail.scrollLeft >= max);
      });
    };
    $$('[data-rail]').forEach(b => b.addEventListener('click', () => {
      const c = rail.firstElementChild;
      const step = (c ? c.getBoundingClientRect().width + 16 : 260) * 2;
      rail.scrollBy({ left: (+b.dataset.rail) * step, behavior: RM.matches ? 'auto' : 'smooth' });
    }));
    rail.addEventListener('scroll', () => { clearTimeout(rail._t); rail._t = setTimeout(sync, 120); }, { passive: true });
    sync();
  }

  if (view === 'browse') {
    const st = parseQ((location.hash.split('?')[1] || ''));
    const nav = s => { s.p = 1; go(buildQ(s)); };
    $$('[data-f]').forEach(cb => cb.addEventListener('change', () => {
      const g = cb.dataset.f, v = cb.value;
      st.f[g] = st.f[g] || [];
      st.f[g] = cb.checked ? [...new Set([...st.f[g], v])] : st.f[g].filter(x => x !== v);
      if (!st.f[g].length) delete st.f[g];
      nav(st);
    }));
    $$('[data-rm]').forEach(b => b.addEventListener('click', () => {
      const raw = b.dataset.rm;
      if (raw === '*') { go('#/browse'); return; }
      const [g, v] = raw.split(':');
      if (g === 'q') st.term = '';
      else { st.f[g] = (st.f[g] || []).filter(x => x !== v); if (!st.f[g].length) delete st.f[g]; }
      nav(st);
    }));
    const srt = $('#srt');
    if (srt) srt.addEventListener('change', () => { st.sort = srt.value; st.p = 1; go(buildQ(st)); });
    const fq = $('#fq');
    if (fq) {
      let t;
      fq.addEventListener('input', () => { clearTimeout(t); t = setTimeout(() => { st.term = fq.value.trim(); st.p = 1; go(buildQ(st)); }, 350); });
    }
    const per = $('#per');
    if (per) per.addEventListener('change', () => { st.per = +per.value; st.p = 1; go(buildQ(st)); });
    $$('[data-p]').forEach(b => b.addEventListener('click', () => { st.p = +b.dataset.p; go(buildQ(st)); }));
  }

  if (view === 'item') {
    const imgs = $$('.thumbs button');
    const stage = $('#stageImg');
    const idx = $('#galIdx');
    let cur = 0;
    const show = n => {
      if (!stage || !imgs.length) return;
      cur = (n + imgs.length) % imgs.length;
      stage.src = imgs[cur].dataset.full;
      imgs.forEach((b, i) => b.setAttribute('aria-current', String(i === cur)));
      if (idx) idx.textContent = `${cur + 1} of ${imgs.length}`;
    };
    imgs.forEach((b, i) => b.addEventListener('click', () => show(i)));
    $$('[data-step]').forEach(b => b.addEventListener('click', () => show(cur + (+b.dataset.step))));
    const gal = $('.gal');
    if (gal) gal.addEventListener('keydown', e => {
      if (e.key === 'ArrowRight') { show(cur + 1); e.preventDefault(); }
      if (e.key === 'ArrowLeft') { show(cur - 1); e.preventDefault(); }
    });
    $$('[data-ask]').forEach(b => b.addEventListener('click', () => {
      /* Hangi dugmeden acildiysa talep turu o olur: bos = bilgi, teklif = teklif */
      $('#enqForm').dataset.tur = b.getAttribute('data-ask') || 'bilgi';
      $('#enq').showModal();
    }));
    const zb = $('#zoomBtn');
    const all = imgs.map(b => b.dataset.full);
    if (zb) zb.addEventListener('click', () => lbOpen(all, cur));
    if (stage) stage.addEventListener('click', () => lbOpen(all, cur));

    /* ---- buyutec ----
       Fotografin kendi cozunurluguyle sinirli: buyutme orani, dosyanin gercek
       piksel genisliginin ekranda kapladigi genislige oranidir. Boylece
       goruntu suni sekilde buyutulup bulaniklasmiyor; ne kadar detay varsa
       o kadar gosteriliyor. */
    const lens = $('#loupe'), kap = stage ? stage.closest('.stage') : null;
    if (lens && stage && kap && matchMedia('(hover:hover) and (pointer:fine)').matches) {
      let kr = null, ir = null, oran = 2;
      const R = () => parseFloat(getComputedStyle(lens).inlineSize) / 2 || 120;
      const olc = () => {
        kr = kap.getBoundingClientRect();
        ir = stage.getBoundingClientRect();
        const dogal = stage.naturalWidth || ir.width;
        oran = Math.min(3.2, Math.max(1.6, dogal / Math.max(1, ir.width)));
        lens.style.backgroundImage = `url("${stage.currentSrc || stage.src}")`;
        lens.style.backgroundSize = `${ir.width * oran}px ${ir.height * oran}px`;
      };
      const ro = new ResizeObserver(olc);
      ro.observe(kap);
      stage.addEventListener('load', olc);
      const ac = e => {
        if (!ir || !ir.width) olc();
        const x = e.clientX - ir.left, y = e.clientY - ir.top;
        if (x < 0 || y < 0 || x > ir.width || y > ir.height) return kapat();
        const r = R();
        lens.style.left = (e.clientX - kr.left - r) + 'px';
        lens.style.top = (e.clientY - kr.top - r) + 'px';
        lens.style.backgroundPosition =
          `${-(x * oran - r)}px ${-(y * oran - r)}px`;
        if (!lens.hasAttribute('data-on')) {
          lens.setAttribute('data-on', '');
          kap.setAttribute('data-loupe', '');
        }
      };
      const kapat = () => { lens.removeAttribute('data-on'); kap.removeAttribute('data-loupe'); };
      kap.addEventListener('pointerenter', olc);
      kap.addEventListener('pointermove', e => {
        if (e.pointerType !== 'mouse' || e.target.closest('button')) return kapat();
        ac(e);
      });
      kap.addEventListener('pointerleave', kapat);
      window.addEventListener('scroll', () => { if (lens.hasAttribute('data-on')) olc(); },
                              { passive: true });
    }
  }
}

/* internal links: view transition */
document.addEventListener('click', e => {
  const a = e.target.closest('a[href^="#/"]');
  if (!a || e.metaKey || e.ctrlKey || e.shiftKey) return;
  e.preventDefault();
  const pdp = a.dataset.pdp;
  if (pdp) {
    const fig = a.closest('.work') && a.closest('.work').querySelector('.work-fig img');
    if (fig && !RM.matches) {
      fig.style.viewTransitionName = 'pdp-img';
      const t = go(a.getAttribute('href'));
      if (t && t.finished) t.finished.finally(() => { fig.style.viewTransitionName = ''; });
      else fig.style.viewTransitionName = '';
      return;
    }
  }
  go(a.getAttribute('href'));
});

/* mega menu */
let openBtn = null;
function closeMega() {
  if (!openBtn) return;
  const m = document.getElementById('mega-' + openBtn.dataset.megaBtn);
  if (m) { m.hidden = true; m.removeAttribute('data-open'); }
  openBtn.setAttribute('aria-expanded', 'false');
  openBtn = null;
}
function openMega(btn) {
  if (openBtn === btn) return closeMega();
  closeMega();
  const m = document.getElementById('mega-' + btn.dataset.megaBtn);
  if (!m) return;
  m.hidden = false; m.setAttribute('data-open', '');
  btn.setAttribute('aria-expanded', 'true');
  openBtn = btn;
}
$$('[data-mega-btn]').forEach(btn => {
  btn.addEventListener('click', () => openMega(btn));
  btn.addEventListener('pointerenter', () => {
    if (matchMedia('(hover:hover) and (pointer:fine)').matches) openMega(btn);
  });
});
$('.masthead').addEventListener('pointerleave', () => {
  if (matchMedia('(hover:hover) and (pointer:fine)').matches) closeMega();
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && openBtn) { const b = openBtn; closeMega(); b.focus(); }
});
document.addEventListener('click', e => { if (openBtn && !e.target.closest('.masthead')) closeMega(); });

/* contact dialog */
const enq = $('#enq');
$$('[data-close]').forEach(b => b.addEventListener('click', () => enq.close()));

/* Talep formu. Artik gercekten gonderiliyor: Supabase'deki talep-gonder
   fonksiyonuna duser, panelde Gelen kutusunda gorunur. Fonksiyon adresi
   yoksa form eskisi gibi sadece tesekkur eder. */
function talepGonder(govde) {
  const a = window.VO_AYAR;
  if (!a || !a.URL || String(a.URL).indexOf('BURAYA') === 0) return Promise.resolve({ tamam: true });
  return fetch(a.URL + '/functions/v1/talep-gonder', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', apikey: a.ANAHTAR,
               Authorization: 'Bearer ' + a.ANAHTAR },
    body: JSON.stringify(govde)
  }).then(c => c.json());
}

$('#enqForm').addEventListener('submit', e => {
  e.preventDefault();
  const f = e.target;
  const mail = f.querySelector('#f-mail');
  const gecerli = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(mail.value.trim());
  const ok = gecerli && f.querySelector('#f-name').value.trim();
  f.querySelectorAll('input[required]').forEach(i => i.setAttribute('aria-invalid', String(!i.value.trim())));
  mail.setAttribute('aria-invalid', String(!gecerli));
  if (!ok) { f.querySelector('[aria-invalid="true"]').focus(); return; }

  const dugme = f.querySelector('button[type="submit"]');
  dugme.disabled = true;
  const slug = (location.hash.indexOf('#/item/') === 0) ? location.hash.slice(7).split('?')[0] : '';
  talepGonder({
    slug: slug, tur: f.dataset.tur || 'bilgi',
    ad: f.querySelector('#f-name').value.trim(),
    eposta: mail.value.trim(),
    mesaj: f.querySelector('#f-msg').value.trim() || 'Bilgi talebi',
    website: f.querySelector('#f-site') ? f.querySelector('#f-site').value : ''
  }).then(() => {
    f.hidden = true; $('#enqOk').hidden = false;
  }).catch(() => {
    f.hidden = true; $('#enqOk').hidden = false;
  }).then(() => { dugme.disabled = false; });
});

/* Tek tikla satin alma. Fiyat sunucuda dogrulanir; buradan giden tek sey
   eserin slug'i. Odeme kapaliysa ya da anahtar girilmemisse fonksiyon 503
   doner ve kullaniciya mesaj gosterilir. */
function satinAl(slug, dugme) {
  const a = window.VO_AYAR;
  if (!a || !a.URL) return;
  const eskiYazi = dugme.textContent;
  dugme.disabled = true; dugme.textContent = 'Opening checkout...';
  fetch(a.URL + '/functions/v1/odeme-baslat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', apikey: a.ANAHTAR,
               Authorization: 'Bearer ' + a.ANAHTAR },
    body: JSON.stringify({ slug: slug })
  }).then(c => c.json().then(d => ({ kod: c.status, d: d })))
    .then(v => {
      if (v.d && v.d.url) { location.href = v.d.url; return; }
      dugme.disabled = false; dugme.textContent = eskiYazi;
      enq.showModal();
    })
    .catch(() => { dugme.disabled = false; dugme.textContent = eskiYazi; enq.showModal(); });
}
document.addEventListener('click', e => {
  const b = e.target.closest && e.target.closest('[data-buy]');
  if (b) satinAl(b.getAttribute('data-buy'), b);
});

"""

APP_JS += STATE_JS

APP_JS += r"""
fillMegaImages();
syncCounts();
window.addEventListener('hashchange', render);
render();
booted = true;

/* ---------------- sayac (cerezsiz, birinci taraf) ----------------
   Hicbir kisisel veri toplanmaz: yalnizca sayfa yolu, geldigi site ve gun.
   Cerez yok, parmak izi yok, IP kaydi yok. Ayni sayfa ayni oturumda bir kez
   sayilir. Panele giris yapmis olan (yani site sahibi) sayilmaz. */
(function () {
  const a = window.VO_AYAR;
  if (!a || !a.URL || String(a.URL).indexOf('BURAYA') === 0) return;
  let yonetici = false;
  try {
    const ref = a.URL.replace('https://', '').split('.')[0];
    yonetici = !!localStorage.getItem('sb-' + ref + '-auth-token');
  } catch (e) { /* depolama kapali: ziyaretci say */ }
  if (yonetici) return;
  const gorulen = new Set();
  function say() {
    let yol = location.hash && location.hash.length > 1 ? location.hash : '#/';
    yol = yol.split('?')[0].slice(0, 180);
    if (gorulen.has(yol)) return;
    gorulen.add(yol);
    let kaynak = '';
    try { kaynak = document.referrer ? new URL(document.referrer).hostname : ''; } catch (e) {}
    if (kaynak === location.hostname) kaynak = '';
    fetch(a.URL + '/rest/v1/ziyaretler', {
      method: 'POST', keepalive: true,
      headers: { 'Content-Type': 'application/json', apikey: a.ANAHTAR,
                 Authorization: 'Bearer ' + a.ANAHTAR, Prefer: 'return=minimal' },
      body: JSON.stringify({ yol: yol, kaynak: kaynak.slice(0, 120) })
    }).catch(function () {});
  }
  say();
  window.addEventListener('hashchange', say);
})();
"""



def pages_js():
    return json.dumps({k: [v[0], v[1], [[h, ps] for h, ps in v[2]]] for k, v in INFO.items()},
                      ensure_ascii=False, separators=(",", ":"))


def museum_js():
    return json.dumps([list(r) for r in MUSEUM_ROOMS], ensure_ascii=False, separators=(",", ":"))


def shells():
    t = open(f"{W}/_shells.txt", encoding="utf-8").read()
    return (t.replace("{X}", IC["x"]).replace("{LEFT}", IC["left"]).replace("{RIGHT}", IC["right"]))


def build():
    fonts = open(f"{W}/sitefonts.css", encoding="utf-8").read()
    SITE_LD = json.dumps([
        {"@context": "https://schema.org", "@type": "Organization",
         "name": "Visionary Object", "url": SITE_URL + "/",
         "logo": SITE_URL + "/img/brand/mark-288.png",
         "address": {"@type": "PostalAddress",
                     "addressRegion": "Virginia", "addressCountry": "US"},
         "description": "A single private collection of antique paintings, prints, "
                        "works on paper, handmade objects and historical documents, "
                        "offered directly by the collector."},
        {"@context": "https://schema.org", "@type": "WebSite",
         "name": "Visionary Object", "url": SITE_URL + "/",
         "potentialAction": {"@type": "SearchAction",
                             "target": {"@type": "EntryPoint",
                                        "urlTemplate": SITE_URL + "/#/browse?q={search_term_string}"},
                             "query-input": "required name=search_term_string"}},
    ], ensure_ascii=False, separators=(",", ":"))
    SHELLS = shells()
    icons = "".join(f"const ICON_{k.upper()}={json.dumps(v)};" for k, v in IC.items())
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Visionary Object: Antique Paintings, Prints and Handmade Objects</title>
<meta name="description" data-home="Shop antique paintings, prints, works on paper, handmade objects and historical documents. One-of-a-kind pieces from a single private collection, offered directly by the collector and shipped insured worldwide." content="Shop antique paintings, prints, works on paper, handmade objects and historical documents. One-of-a-kind pieces from a single private collection, offered directly by the collector and shipped insured worldwide.">
<meta name="theme-color" content="#F4F2E3">
<link rel="canonical" href="{SITE_URL}/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Visionary Object">
<meta property="og:title" content="Visionary Object">
<meta property="og:url" content="{SITE_URL}/">
<meta property="og:description" content="Extraordinary antique art and objects, one of a kind, from a single private collection.">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="Visionary Object">
<meta name="twitter:description" content="Extraordinary antique art and objects, one of a kind, from a single private collection.">
<link rel="icon" href="favicon.png" sizes="32x32">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta property="og:image" content="{SITE_URL}/img/brand/logo-1040.webp">
<meta name="twitter:image" content="{SITE_URL}/img/brand/logo-1040.webp">
<script type="application/ld+json">{SITE_LD}</script>
<style>{fonts}</style>
<style>{CSS}{CSS2}{CSS3}
:root{{--grain-src:{GRAIN}}}
</style>
</head>
<body>
<a class="skip" href="#app">Skip to main content</a>
<div class="grain" aria-hidden="true"></div>
{RAIL}
{kampanya_serit()}
<p class="promo">One-of-a-kind antique art, direct from the collector <span>&middot; insured delivery worldwide</span> <a href="#/info/shipping">Terms apply. Details</a></p>
{masthead()}

<main id="app" tabindex="-1"></main>

{footer()}
{SHELLS}

<dialog id="enq" closedby="any" aria-labelledby="enqTitle">
  <div class="dbox">
    <button class="dclose" data-close type="button" aria-label="Close">×</button>
    <p class="eyebrow" style="margin-block-end:.8rem">Contact Seller</p>
    <h2 id="enqTitle" style="font-size:var(--t-h3)">Request details</h2>
    <p style="color:var(--ink-2);font-size:.95rem;margin-block:.6rem 1.4rem">Ask for a condition report, additional images or a shipping quote. Typical response time: same day.</p>
    <form id="enqForm" novalidate>
      <div class="fld"><label for="f-name">Full name</label>
        <input id="f-name" name="name" type="text" required autocomplete="name" maxlength="80">
        <span class="err">Please enter your name.</span></div>
      <div class="fld"><label for="f-mail">Email</label>
        <input id="f-mail" name="email" type="email" required autocomplete="email">
        <span class="err">Please enter a valid email address.</span></div>
      <div class="fld"><label for="f-msg">Message</label>
        <textarea id="f-msg" name="message" rows="3" placeholder="Which item, and what would you like to know?"></textarea></div>
      <div aria-hidden="true" style="position:absolute;inset-inline-start:-9999px" tabindex="-1">
        <label for="f-site">Leave this empty</label>
        <input id="f-site" name="website" type="text" autocomplete="off" tabindex="-1"></div>
      <button class="btn btn--fill" type="submit" style="inline-size:100%">Send <span class="arw" aria-hidden="true">→</span></button>
      <p style="font-size:var(--t-xs);color:var(--ink-3);margin-block-start:.8rem">We reply from the collection directly. Your details are used only to answer this message.</p>
    </form>
    <div id="enqOk" hidden>
      <p class="eyebrow">Received</p>
      <h2 style="font-family:var(--f-serif);font-size:var(--t-h3);margin-block:.6rem">Thank you.</h2>
      <p style="color:var(--ink-2)">Thank you. Your message has been sent to the seller, who typically responds the same day.</p>
      <button class="btn btn--line" data-close type="button" style="margin-block-start:1.4rem">Close</button>
    </div>
  </div>
</dialog>

<script>const SITE={json.dumps(SITE_URL)};const DATA={js_data()};const PAGES={pages_js()};const DBSAYFA={json.dumps(db_sayfalar(), ensure_ascii=False)};const AYAR={json.dumps(db_ayarlar(), ensure_ascii=False)};const MUSEUM={museum_js()};{icons}</script>
<script>{APP_JS}</script>
<!-- Yerinde duzenleme. Giris yapmamis ziyaretci icin bu dosya hicbir sey yapmaz
     ve hicbir sey indirmez: once tarayicida oturum anahtari var mi diye bakar. -->
<script>window.VO_AYAR={json.dumps(panel_ayari())}</script>
<script src="vo-duzenle.js" defer></script>
</body>
</html>'''
    os.makedirs(CIKTI, exist_ok=True)
    out = os.path.join(CIKTI, "index.html")
    open(out, "w", encoding="utf-8", newline="\n").write(html)
    print(out, f"{len(html)/1024/1024:.2f} MB")
    print("em dash:", html.count("—"), "| en dash:", html.count("–"))
    static_build(fonts)


def odeme_sonrasi():
    """Stripe'tan donen ziyaretcinin gordugu sayfa.

    Tek basina duran bir dosya: sitenin app.css'ini kullanir, baska hicbir
    sey indirmez. Siparis numarasi adres cubugunda gelir; sayfa onu sadece
    gosterir, hicbir sorgu yapmaz.
    """
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Order received &middot; Visionary Object</title>
<link rel="stylesheet" href="../app.css">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
</head>
<body>
<div class="grain" aria-hidden="true"></div>
<main id="app" tabindex="-1" style="max-inline-size:44rem;margin-inline:auto;
     padding-block:clamp(4rem,12vh,9rem);padding-inline:var(--gap-m);text-align:center">
  <p class="eyebrow">Order received</p>
  <h1 style="font-family:var(--f-serif);font-size:var(--t-h1);margin-block:.8rem 1.2rem">Thank you.</h1>
  <p style="color:var(--ink-2);font-size:1.05rem">Your payment went through and the piece is now
     reserved for you. A confirmation is on its way to the email address you gave at checkout.</p>
  <p style="color:var(--ink-3);font-size:var(--t-xs);margin-block-start:1.6rem">
     Order reference <code id="ref">&mdash;</code></p>
  <p style="margin-block-start:2.4rem">
     <a class="btn btn--fill" href="{SITE_URL}/">Back to the collection
       <span class="arw" aria-hidden="true">&#8594;</span></a></p>
  <p style="color:var(--ink-3);font-size:var(--t-xs);margin-block-start:2rem">
     Questions about shipping or condition? Reply to the confirmation email and
     it reaches the collector directly.</p>
</main>
<script>
  var s = new URLSearchParams(location.search).get('oturum') || '';
  if (s) document.getElementById('ref').textContent = s.slice(-12).toUpperCase();
</script>
</body>
</html>
'''


def static_build(fonts):
    """Taranabilir sayfalar, stil dosyasi, favicon, sitemap ve robots."""
    import static_pages as SP
    S = CIKTI
    os.makedirs(f"{S}/item", exist_ok=True)
    os.makedirs(f"{S}/category", exist_ok=True)

    open(f"{S}/app.css", "w", encoding="utf-8", newline="\n").write(
        fonts.replace("url(data:", "url(data:") + CSS + CSS2 + CSS3 +
        f":root{{--grain-src:{GRAIN}}}" + SP.STAT_CSS)
    open(f"{S}/favicon.svg", "w", encoding="utf-8", newline="\n").write(
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'>"
        "<rect width='32' height='32' fill='#222'/>"
        "<text x='16' y='23' font-family='Georgia,serif' font-size='19' fill='#F4F2E3'"
        " text-anchor='middle'>V</text></svg>")

    rows = js_rows()
    urls = ["", "museum/index.html", "category/all.html"]
    for d in rows:
        open(f'{S}/item/{d["slug"]}.html', "w", encoding="utf-8", newline="\n").write(SP.item_page(d, SITE_URL, ROLEN))
        urls.append(f'item/{d["slug"]}.html')
    open(f"{S}/category/all.html", "w", encoding="utf-8", newline="\n").write(SP.cat_page(rows, None, SITE_URL))
    for c in ("tablo", "obje", "belge", "rugs", "lighting", "sculpture"):
        sub = [d for d in rows if d["cat"] == c]
        if not sub:
            continue
        open(f"{S}/category/{SP.CATSLUG[c]}.html", "w", encoding="utf-8", newline="\n").write(
            SP.cat_page(sub, c, SITE_URL))
        urls.append(f"category/{SP.CATSLUG[c]}.html")

    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append(f'<url><loc>{SITE_URL}/{u}</loc>'
                  f'<changefreq>weekly</changefreq>'
                  f'<priority>{"1.0" if u == "" else "0.8" if u.startswith("category") else "0.7"}</priority></url>')
    sm.append('</urlset>')
    open(f"{S}/sitemap.xml", "w", encoding="utf-8", newline="\n").write("\n".join(sm))
    # 3B muzenin katalogu da ayni veriden
    import museum_data
    os.makedirs(f"{S}/museum", exist_ok=True)
    open(f"{S}/museum/data.js", "w", encoding="utf-8", newline="\n").write(museum_data.js(rows))

    open(f"{S}/robots.txt", "w", encoding="utf-8", newline="\n").write(
        "User-agent: *\nAllow: /\nDisallow: /order/\nDisallow: /_kaynak/\n\n"
        "Sitemap: " + SITE_URL + "/sitemap.xml\n")

    # Odeme sonrasi donus sayfasi. Stripe buraya yollar; siparis numarasi
    # adreste gelir. Sayfa hicbir gizli bilgi tasimaz.
    os.makedirs(f"{S}/order", exist_ok=True)
    open(f"{S}/order/success.html", "w", encoding="utf-8", newline="\n").write(
        odeme_sonrasi())

    # GitHub Pages, adi 404.html olan dosyayi her bilinmeyen adreste gosterir.
    # Bu olmadan ziyaretci GitHub'in kendi hata sayfasina duser.
    open(f"{S}/404.html", "w", encoding="utf-8", newline="\n").write(f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>Page not found &middot; Visionary Object</title>
<link rel="stylesheet" href="/app.css">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
</head>
<body>
<div class="grain" aria-hidden="true"></div>
<main id="app" tabindex="-1" style="max-inline-size:44rem;margin-inline:auto;
     padding-block:clamp(4rem,14vh,10rem);padding-inline:var(--gap-m);text-align:center">
  <p class="eyebrow">404</p>
  <h1 style="font-family:var(--f-serif);font-size:var(--t-h1);margin-block:.8rem 1.2rem">This page is not in the collection.</h1>
  <p style="color:var(--ink-2)">The address may have changed, or the piece may have moved.
     Everything that is here can be reached from the gallery.</p>
  <p style="margin-block-start:2.2rem">
    <a class="btn btn--fill" href="{SITE_URL}/">Back to the collection <span class="arw" aria-hidden="true">&#8594;</span></a>
    <a class="btn btn--line" href="{SITE_URL}/category/all.html" style="margin-inline-start:.5rem">All items</a></p>
</main>
</body>
</html>
''')
    print(f"statik sayfa: {len(rows)} ilan + 4 kategori · sitemap {len(urls)} adres")

    # Panelin ayar dosyasi da tek kaynaktan uretilir: data/panel.json.
    # Boylece Supabase adresi iki ayri yerde tutulmaz.
    a = panel_ayari()
    kls = os.path.join(CIKTI, "admin")
    if os.path.isdir(kls):
        with open(os.path.join(kls, "config.js"), "w", encoding="utf-8", newline="\n") as f:
            f.write("/* build_en.py tarafindan data/panel.json'dan uretilir. Elle duzenleme. */\n"
                    "window.VO = " + json.dumps({"URL": a["URL"], "ANAHTAR": a["ANAHTAR"],
                                                 "SITE": SITE_URL}, ensure_ascii=False) + ";\n")
        print("panel ayari yazildi:", "bagli" if not a["URL"].startswith("BURAYA") else "henuz bagli degil")


if __name__ == "__main__":
    build()
