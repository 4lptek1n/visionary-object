# -*- coding: utf-8 -*-
"""Taranabilir statik sayfalar.

Hash yonlendirmeli tek sayfa uygulamasi arama motorlari icin tek bir adres
gorunur. 1stDibs'te her ilanin ve her kategorinin kendi adresi, kendi canonical
etiketi, kendi aciklamasi ve kendi Product / BreadcrumbList semasi var.
Burasi ayni sayin yapiyi ayni veriden uretir: index.html ile bu sayfalar tek
kaynaktan (js_data) beslenir, ayrisamazlar.
"""
import html as H
import json
import os

CATSLUG = {"tablo": "paintings-and-prints", "obje": "handmade-objects",
           "belge": "documents", "rugs": "persian-rug",
           "lighting": "lighting", "sculpture": "sculpture"}
CATNAME = {"tablo": "Paintings & Prints", "obje": "Handmade Objects",
           "belge": "Documents", "rugs": "Persian Rug",
           "lighting": "Lighting", "sculpture": "Sculpture"}


def esc(s):
    return H.escape(str(s or ""), quote=True)


def _spa(s):
    """Statik sayfa bir alt klasorde; uygulama baglantilarini yukari tasi."""
    return s.replace('href="#/', 'href="../index.html#/').replace(
        'href="#"', 'href="../index.html"')


def head(title, desc, canon, img, base, ld, extra=""):
    o = [
        '<!DOCTYPE html>', '<html lang="en">', '<head>',
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">',
        f'<title>{esc(title)}</title>',
        f'<meta name="description" content="{esc(desc)}">',
        f'<link rel="canonical" href="{base}/{canon}">',
        '<meta name="theme-color" content="#F4F2E3">',
        '<meta property="og:type" content="product">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(desc)}">',
        f'<meta property="og:url" content="{base}/{canon}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{esc(title)}">',
        f'<meta name="twitter:description" content="{esc(desc)}">',
    ]
    if img:
        o += [f'<meta property="og:image" content="{base}/{img}">',
              f'<meta name="twitter:image" content="{base}/{img}">']
    o += ['<link rel="icon" href="../favicon.png" sizes="32x32">',
          '<link rel="stylesheet" href="../app.css">',
          extra,
          '<script type="application/ld+json">' +
          json.dumps(ld, ensure_ascii=False, separators=(",", ":")) + '</script>',
          '</head>']
    return "\n".join(x for x in o if x)


def crumbs(items, base):
    """items: [(ad, href|None)] — sonuncusu baglantisiz."""
    li = []
    for i, (t, h) in enumerate(items):
        li.append(f'<a href="{h}">{esc(t)}</a>' if h else f'<span aria-current="page">{esc(t)}</span>')
    nav = '<nav class="crumbs" aria-label="Breadcrumb">' + ' <i>/</i> '.join(li) + '</nav>'
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList",
          "itemListElement": [
              {"@type": "ListItem", "position": i + 1, "name": t,
               **({"item": base + "/" + h.replace("../", "")} if h and not h.startswith("http") else {})}
              for i, (t, h) in enumerate(items)]}
    return nav, ld


def item_page(d, base, roleen):
    slug = d["slug"]
    cat = d["cat"]
    imgs = d["img"]
    cover = d.get("cov") or next((o for o in imgs if o["rol"] == "tam"), imgs[0] if imgs else None)
    # Sanatci bilinmiyorsa basliga "Unknown" yazmak arama sonucunda kotu duruyor
    # ve tiklanmayi dusuruyor. Ad varsa basa alinir, yoksa hic anilmaz.
    creator = d["creator"] or ""
    title = (f'{creator}, {d["title"]} For Sale' if creator
             else f'{d["title"]} For Sale | Visionary Object')
    desc = (f'For sale at Visionary Object: {d["title"]}'
            + (f', {d["medium"]}' if d["medium"] else "")
            + (f' by {creator}' if creator else "")
            + '. One of a kind, offered directly by the collector.')
    hw = (f'Height {d["dims"][1]} in, width {d["dims"][0]} in. ' if d["dims"] else "")

    ld_prod = {
        "@context": "https://schema.org", "@type": "Product",
        "@id": f'{base}/item/{slug}.html',
        "name": d["title"],
        "description": hw + d["desc"],
        "category": CATNAME[cat],
        "sku": f'VO-{d["no"]:02d}',
        "itemCondition": "https://schema.org/UsedCondition",
        "brand": {"@type": "Brand", "name": creator or "Visionary Object"},
        "image": [f'{base}/{o["f"]}' for o in imgs[:8]],
        "offers": {"@type": "Offer", "availability": "https://schema.org/InStock",
                   "priceCurrency": "USD", "price": 0,
                   "priceSpecification": {"@type": "PriceSpecification",
                                          "valueAddedTaxIncluded": False},
                   "url": f'{base}/item/{slug}.html',
                   "seller": {"@type": "Organization", "name": "Visionary Object"}},
    }
    if d["dims"]:
        ld_prod["height"] = {"@type": "QuantitativeValue", "value": d["dims"][1],
                             "unitCode": "INH"}
        ld_prod["width"] = {"@type": "QuantitativeValue", "value": d["dims"][0],
                            "unitCode": "INH"}
    if d["medium"]:
        ld_prod["material"] = d["medium"]

    nav, ld_crumb = crumbs([
        ("Home", "../index.html"),
        ("All Items", f"../category/all.html"),
        (CATNAME[cat], f"../category/{CATSLUG[cat]}.html"),
        (d["title"], None)], base)

    figs = "".join(
        f'<figure><img src="../{o["c"]}" srcset="../{o["c"]} 700w, ../{o["f"]} 1500w" '
        f'sizes="(max-width:760px) 92vw, 46vw" width="{o["w"]}" height="{o["h"]}" '
        f'loading="{"eager" if i == 0 else "lazy"}" decoding="async" '
        f'alt="{esc(d["title"])} - {esc(roleen.get(o["rol"], o["rol"]))}">'
        f'<figcaption>{esc(roleen.get(o["rol"], o["rol"])).capitalize()}</figcaption></figure>'
        for i, o in enumerate(imgs))

    rows = [("Creator", creator), ("Creation Year", d["period"]),
            ("Dimensions", (f'Height: {d["dims"][1]} in ({round(d["dims"][1]*2.54,2)} cm)<br>'
                            f'Width: {d["dims"][0]} in ({round(d["dims"][0]*2.54,2)} cm)<br>'
                            f'<span class="sub">{esc(d["dimsOf"])}</span>') if d["dims"] else ""),
            ("Medium", d["medium"]), ("Edition", d["edition"]),
            ("Period", d["period2"].replace("-", " ").title() if d["period2"] else ""),
            ("Condition", "Offered in the condition shown in the photographs."),
            ("Reference Number", d["ref"] or f'VO-{d["no"]:02d}'),
            ("Documentation", d["doc"]), ("Gallery Location", d["gallery"] or d["label"])]
    dl = "".join(f'<div><dt>{k}:</dt><dd>{v if k=="Dimensions" else esc(v)}</dd></div>'
                 for k, v in rows if v)

    body = f'''<body class="stat">
<a class="skip" href="#main">Skip to main content</a>
<p class="promo">One-of-a-kind antique art, direct from the collector <span>&middot; insured delivery worldwide</span> <a href="../index.html#/info/shipping">Terms apply. Details</a></p>
<header class="stat-head"><a class="wordmark" href="../index.html"><img src="../img/brand/mark-72.png" width="34" height="34" alt="" decoding="async"><span class="wm-t">Visionary<span>Object</span></span></a>
<a class="btn btn--line" href="../index.html#/item/{slug}">Open on the site <span class="arw" aria-hidden="true">&rarr;</span></a></header>
<main id="main" tabindex="-1"><div class="shell">
{nav}
<article class="stat-item">
  <p class="eyebrow">{esc(CATNAME[cat])}</p>
  <h1>{esc(d["title"])}</h1>
  <p class="stat-by">{esc(creator)}{(" &middot; " + esc(d["period"])) if d["period"] else ""}</p>
  <p class="stat-price">Price Upon Request</p>
  <div class="stat-gal">{figs}</div>
  <section><h2>About the Item</h2><p>{esc(d["desc"])}</p></section>
  <section><h2>Details</h2><dl class="stat-dl">{dl}</dl></section>
  <p class="stat-cta"><a class="btn btn--fill" href="../index.html#/item/{slug}">Contact the seller <span class="arw" aria-hidden="true">&rarr;</span></a></p>
</article>
</div></main>
<footer class="stat-foot"><div class="shell">
<p>Visionary Object &middot; one private collection, offered directly by the collector.</p>
<p><a href="../category/all.html">All items</a> &middot; <a href="../index.html#/museum">The Museum</a> &middot; <a href="../index.html#/info/shipping">Shipping</a> &middot; <a href="../index.html#/info/contact">Contact</a></p>
</div></footer>
</body></html>'''

    return head(title, desc, f"item/{slug}.html",
                cover["f"] if cover else "", base, [ld_prod, ld_crumb]) + body


def cat_page(items, cat, base):
    slug = "all" if cat is None else CATSLUG[cat]
    name = "All Items" if cat is None else CATNAME[cat]
    title = f"{name} - {len(items)} For Sale · Visionary Object"
    desc = (f"Browse {len(items)} one-of-a-kind {name.lower()} from a single private "
            "collection. Every piece photographed in full, measured and offered "
            "directly by the collector.")
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage",
           "name": name, "description": desc, "url": f"{base}/category/{slug}.html",
           "mainEntity": {"@type": "ItemList", "numberOfItems": len(items),
                          "itemListElement": [
                              {"@type": "ListItem", "position": i + 1,
                               "url": f'{base}/item/{d["slug"]}.html',
                               "name": d["title"]}
                              for i, d in enumerate(items)]}}]
    nav, ld_crumb = crumbs([("Home", "../index.html"),
                            ("All Items", "../category/all.html")] +
                           ([(name, None)] if cat else []), base)
    if not cat:
        nav, ld_crumb = crumbs([("Home", "../index.html"), ("All Items", None)], base)
    ld.append(ld_crumb)

    cards = ""
    for d in items:
        o = d.get("cov") or next((x for x in d["img"] if x["rol"] == "tam"), d["img"][0] if d["img"] else None)
        if not o:
            continue
        cards += (f'<li><a class="stat-thumb" href="../item/{d["slug"]}.html" tabindex="-1" '
                  f'aria-hidden="true"><img src="../{o["c"]}" width="{o["w"]}" '
                  f'height="{o["h"]}" loading="lazy" decoding="async" alt=""></a>'
                  f'<h2><a href="../item/{d["slug"]}.html">{esc(d["title"])}</a></h2>'
                  f'<p>{esc(d["creator"] or "Artist unrecorded")}'
                  + (f' &middot; {d["dims"][1]} &times; {d["dims"][0]} in' if d["dims"] else "")
                  + '</p><p class="stat-price">Price Upon Request</p></li>')

    others = "".join(
        f'<a href="{CATSLUG[c]}.html">{CATNAME[c]}</a>'
        for c in ("tablo", "obje", "belge") if c != cat)

    body = f'''<body class="stat">
<a class="skip" href="#main">Skip to main content</a>
<p class="promo">One-of-a-kind antique art, direct from the collector <span>&middot; insured delivery worldwide</span> <a href="../index.html#/info/shipping">Terms apply. Details</a></p>
<header class="stat-head"><a class="wordmark" href="../index.html"><img src="../img/brand/mark-72.png" width="34" height="34" alt="" decoding="async"><span class="wm-t">Visionary<span>Object</span></span></a>
<a class="btn btn--line" href="../index.html#/browse{'' if cat is None else '?cat=' + cat}">Open on the site <span class="arw" aria-hidden="true">&rarr;</span></a></header>
<main id="main" tabindex="-1"><div class="shell">
{nav}
<h1>{esc(name)}</h1>
<p class="stat-lede">{len(items)} pieces, each one of a kind, from a single private collection.</p>
<p class="stat-links"><a href="all.html">All Items</a>{others}</p>
<ul class="stat-grid">{cards}</ul>
</div></main>
<footer class="stat-foot"><div class="shell">
<p>Visionary Object &middot; one private collection, offered directly by the collector.</p>
<p><a href="all.html">All items</a> &middot; <a href="../index.html#/museum">The Museum</a> &middot; <a href="../index.html#/info/shipping">Shipping</a> &middot; <a href="../index.html#/info/contact">Contact</a></p>
</div></footer>
</body></html>'''
    cover = next((x for x in items[0]["img"] if x["rol"] == "tam"), None) if items else None
    return head(title, desc, f"category/{slug}.html",
                cover["f"] if cover else "", base, ld) + body


STAT_CSS = """
/* --- taranabilir statik sayfalar --- */
body.stat{background:var(--bg);color:var(--ink);font-family:var(--f-sans);}
.stat .shell{max-inline-size:var(--shell);margin-inline:auto;padding-inline:var(--gut);}
.stat-head{display:flex;align-items:center;justify-content:space-between;gap:1rem;
  padding:1.1rem clamp(1.1rem,4vw,2.6rem);border-block-end:1px solid var(--line);
  flex-wrap:wrap;}
.stat-head .wordmark{display:flex;align-items:center;gap:.55rem;text-decoration:none;color:var(--ink);}
.stat-head .wordmark img{inline-size:34px;block-size:34px;object-fit:contain;flex:0 0 auto}
.stat-head .wm-t{font-family:var(--f-serif);font-size:1.5rem;line-height:1}
.stat-head .wm-t span{display:block;font-family:var(--f-mono);font-size:.6rem;
  letter-spacing:.18em;color:var(--ink-3);text-transform:uppercase;}
.stat main{padding-block:2.5rem 4rem;}
.crumbs{font-size:var(--t-xs);color:var(--ink-3);margin-block-end:1.6rem;}
.crumbs a{color:var(--ink-2);}
.crumbs i{font-style:normal;margin-inline:.4rem;color:var(--ink-4,#9a958a);}
.stat h1{font-family:var(--f-serif);font-size:var(--t-h2);line-height:1.12;
  margin-block:.2rem .5rem;max-inline-size:24ch;}
.stat-by{color:var(--ink-2);}
.stat-lede{color:var(--ink-2);margin-block:.4rem 1.6rem;}
.stat-price{font-family:var(--f-mono);font-size:.95rem;margin-block:.9rem 1.8rem;}
.stat-gal{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,300px),1fr));
  gap:1.4rem;margin-block-end:3rem;}
.stat-gal figure{margin:0;}
.stat-gal img{inline-size:100%;block-size:auto;background:#fff;border:1px solid var(--line);}
.stat-gal figcaption{font-family:var(--f-mono);font-size:var(--t-xs);color:var(--ink-3);
  margin-block-start:.5rem;}
.stat section{margin-block-end:2.6rem;max-inline-size:70ch;}
.stat section h2{font-family:var(--f-serif);font-size:var(--t-h3);margin-block-end:.8rem;}
.stat section p{color:var(--ink-2);line-height:1.65;}
.stat-dl{display:grid;gap:.1rem;}
.stat-dl>div{display:grid;grid-template-columns:minmax(0,13rem) minmax(0,1fr);gap:1rem;
  padding-block:.7rem;border-block-start:1px solid var(--line);}
.stat-dl dt{font-family:var(--f-mono);font-size:var(--t-xs);letter-spacing:.06em;
  text-transform:uppercase;color:var(--ink-3);}
.stat-dl dd{margin:0;color:var(--ink);}
.stat-dl .sub{color:var(--ink-3);font-size:.9em;}
.stat-cta{margin-block-start:2rem;}
.stat-links{display:flex;flex-wrap:wrap;gap:1.2rem;margin-block-end:2rem;font-size:.95rem;}
.stat-grid{list-style:none;margin:0;padding:0;display:grid;gap:2rem 1.6rem;
  grid-template-columns:repeat(auto-fill,minmax(min(100%,230px),1fr));}
.stat-grid li{display:flex;flex-direction:column;}
.stat-grid .stat-thumb{display:grid;place-items:center;aspect-ratio:1;
  background:#fff;border:1px solid var(--line);padding:.9rem;}
.stat-grid img{max-inline-size:100%;max-block-size:100%;inline-size:auto;
  block-size:auto;object-fit:contain;}
.stat-grid h2{font-family:var(--f-serif);font-size:1.05rem;line-height:1.25;
  margin-block:.7rem .25rem;}
.stat-grid h2 a{text-decoration:none;color:var(--ink);}
.stat-grid h2 a:hover{text-decoration:underline;}
.stat-grid p{font-size:.85rem;color:var(--ink-2);margin:0;}
.stat-grid .stat-price{margin-block:.4rem 0;font-size:.8rem;}
.stat-foot{border-block-start:1px solid var(--line);padding-block:2rem 3rem;
  font-size:var(--t-xs);color:var(--ink-3);}
.stat-foot p{margin-block:.3rem;}
@media (max-width:640px){.stat-dl>div{grid-template-columns:1fr;gap:.2rem;}}
"""
