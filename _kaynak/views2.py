# -*- coding: utf-8 -*-
"""The pages 1stDibs has that we were missing, plus the Museum, which is ours."""

VIEWS2 = r"""
/* ---------------- curated collections (all real facets) ---------------- */
const COLLECTIONS = [
  { slug:'signed-and-numbered', name:'Signed & Numbered',
    blurb:'Limited editions with the artist’s pencil signature and edition number in the margin.',
    q:'#/browse?doc=imza', test:d => (d.roles['imza']||0) > 0 },
  { slug:'with-certificate', name:'With Certificate',
    blurb:'Pieces that travel with their own certificate of authenticity.',
    q:'#/browse?doc=sertifika', test:d => (d.roles['sertifika']||0) > 0 },
  { slug:'works-on-paper', name:'Works on Paper',
    blurb:'Serigraphs, etchings, engravings, lithographs and watercolours.',
    q:'#/browse?medium=print', test:d => d.medium2.includes('print') || d.medium2.includes('watercolour') },
  { slug:'oil-on-canvas', name:'Oil on Canvas',
    blurb:'Painted in oil, stretched and framed as found.',
    q:'#/browse?medium=oil', test:d => d.medium2.includes('oil') },
  { slug:'gilt-frames', name:'In Gilt Frames',
    blurb:'Carved, moulded and gilded frames, included in the sale.',
    q:'#/browse?color=Gold', test:d => (d.color||[]).includes('Gold') },
  { slug:'asian-works', name:'Asian Works',
    blurb:'Japanese, Chinese and Formosan pieces, several with their original back labels.',
    q:'#/browse?style=asian', test:d => d.style.includes('asian') },
  { slug:'still-life', name:'Still Life',
    blurb:'Flowers, fruit and vessels, from the Dutch manner to mid-century.',
    q:'#/browse?subject=still-life', test:d => d.subject.includes('still-life') },
  { slug:'the-archive', name:'The Archive',
    blurb:'Documents issued rather than made to be sold: diplomas, certificates, awards.',
    q:'#/browse?cat=belge', test:d => d.cat === 'belge' },
];
const collItems = c => DATA.filter(c.test);

const TRENDING = ['Watercolour','Signed','Certificate of Authenticity','Gilt Frame','Sunflowers',
                  'Japanese','Serigraph','Dali','Croix de Guerre','Lace'];

/* ---------------- THE MUSEUM ---------------- */
function viewMuseum(q) {
  const want = new URLSearchParams(q || '').get('room');
  /* bir odaya baglanti verildiyse o oda basa alinir: kaydirma yok, jank yok */
  const ORDER = want ? [...MUSEUM].sort((a, b) => (b[4] === want) - (a[4] === want)) : MUSEUM;
  const rooms = ORDER.map(([no, name, cat, blurb, slug], i) => {
    const pool = DATA.filter(d => d.cat === slug && cover(d));
    const ex = pool[i % (pool.length || 1)];
    const n = pool.length;
    /* odanin icindeki gercek eserler: oda artik bir vitrin, bir resim degil */
    const strip = pool.slice(0, 5).map(d =>
      `<a href="#/item/${d.slug}" title="${esc(d.title)}">${pic(cover(d), 't', esc(d.title))}</a>`).join('');
    return `<article class="room up${want === slug ? ' room--on' : ''}" id="room-${slug}" style="--i:${i % 4}">
      <div class="room-fig msk" style="--i:${i % 4}">${ex ? pic(cover(ex), 'f', esc(ex.title))
        : `<span class="mono" style="font-size:.68rem;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-3)">Being catalogued</span>`}</div>
      <div>
        <p class="room-no">Room ${esc(no)}</p>
        <h2>${esc(name)}</h2>
        <p class="sub">${esc(cat)} · ${n ? n + (n === 1 ? ' item' : ' items') : 'being catalogued'}</p>
        <p>${esc(blurb)}</p>
        ${strip ? `<div class="room-strip">${strip}</div>` : ''}
        ${n ? `<a class="btn btn--line" href="#/browse?cat=${slug}">Enter the Room <span class="arw" aria-hidden="true">→</span></a>`
            : `<a class="btn btn--line" href="#/info/contact">Ask What Is Coming</a>`}
      </div>
    </article>`;
  }).join('');
  const hero = DATA.find(d => d.no === 4) || DATA[0];
  return `
<section class="mz-hero" data-io>
  ${cover(hero) ? `<img src="${cover(hero).f}" width="${cover(hero).w}" height="${cover(hero).h}" alt="" aria-hidden="true" fetchpriority="high">` : ''}
  <div class="in">
    <p class="eyebrow up">Visionary Object</p>
    <h1 id="h-mz"><span class="rv"><span>A collection</span></span><span class="rv"><span style="--i:1">arranged as rooms.</span></span></h1>
    <p class="up" style="--i:2">Marketplaces are lists. A collection is a sequence. These five rooms are how the pieces were kept before they were listed, and the order still tells you something the grid cannot.</p>
  </div>
</section>
<section class="sec" data-io aria-labelledby="h-rooms">
  <div class="shell">
    <div class="sec-head"><h2 id="h-rooms" class="rv"><span>Five Rooms</span></h2>
      <a class="lnk up" href="#/browse"><span>Skip to the Grid</span> <span class="arw" aria-hidden="true">→</span></a></div>
    <nav class="room-jump" aria-label="Rooms">${MUSEUM.map(([no, name, cat, blurb, slug]) =>
      `<a href="#/museum?room=${slug}"${want === slug ? ' aria-current="true"' : ''}>${esc(name)}</a>`).join('')}</nav>
    <div class="rooms">${rooms}</div>
  </div>
</section>
${protectionBlock()}`;
}

/* ---------------- COLLECTIONS ---------------- */
function viewCollections() {
  const cards = COLLECTIONS.map((c, i) => {
    const items = collItems(c);
    const ex = items.find(d => cover(d));
    return `<a class="coll up" style="--i:${i % 4}" href="#/collection/${c.slug}">
      <figure class="msk" style="--i:${i % 4}">${pic(cover(ex), 'c', '')}</figure>
      <figcaption><b>${esc(c.name)}</b><span>${items.length} ${items.length === 1 ? 'item' : 'items'}</span>
        <span class="cta">Shop the Collection</span></figcaption></a>`;
  }).join('');
  return `<div class="shell">
    <nav class="crumbs" aria-label="Breadcrumbs"><a href="#/">Home</a><i>/</i><span aria-current="page">Collections</span></nav>
    <div class="coll-top"><h1>Collections</h1></div>
    <p style="color:var(--ink-2);max-inline-size:64ch;margin-block-end:var(--gap-m)">Eight edits drawn from the collection, each one built on something the pieces have in common rather than on what happens to be new.</p>
    <div class="colls" data-io>${cards}</div>
  </div>`;
}

function viewCollection(slug) {
  const c = COLLECTIONS.find(x => x.slug === slug);
  if (!c) return notFound('That collection could not be found.');
  const items = collItems(c);
  return `<div class="shell">
    <nav class="crumbs" aria-label="Breadcrumbs"><a href="#/">Home</a><i>/</i>
      <a href="#/collections">Collections</a><i>/</i><span aria-current="page">${esc(c.name)}</span></nav>
    <div class="coll-top"><h1>${esc(c.name)}</h1>
      <button class="btn-save" type="button">${ICON_HEART} Save Search</button></div>
    <p style="color:var(--ink-2);max-inline-size:64ch">${esc(c.blurb)}</p>
    <h2 class="count" style="margin-block:var(--gap-m) var(--gap-s)"><b>${items.length}</b> ${esc(c.name)} For Sale</h2>
    <div class="grid-works">${items.map(card).join('')}</div>
    ${items.length ? '' : `<div class="empty"><h3>No Items Found</h3><p>This edit is empty for the moment.</p></div>`}
  </div>`;
}

/* ---------------- CREATORS ---------------- */
function viewCreators() {
  const map = {};
  DATA.forEach(d => { const k = d.creator || 'Unknown'; (map[k] = map[k] || []).push(d); });
  const names = Object.keys(map).filter(k => k !== 'Unknown').sort((a, b) => a.localeCompare(b));
  const rows = names.map(n => `<a href="#/browse?artist=${encodeURIComponent(n)}"><span>${esc(n)}</span><em>${map[n].length}</em></a>`).join('');
  return `<div class="shell">
    <nav class="crumbs" aria-label="Breadcrumbs"><a href="#/">Home</a><i>/</i><span aria-current="page">Creators</span></nav>
    <div class="coll-top"><h1>Creators</h1></div>
    <p style="color:var(--ink-2);max-inline-size:64ch;margin-block-end:var(--gap-m)">Every artist whose signature, stamp or label is legible on a piece in the collection. ${map['Unknown'] ? map['Unknown'].length : 0} further works carry a signature that has not been identified; if you recognise a hand, write to us.</p>
    <div class="cols3">${rows}</div>
    <p style="margin-block-start:var(--gap-m)"><a class="btn btn--line" href="#/browse">Browse All ${DATA.length} Items <span class="arw" aria-hidden="true">→</span></a></p>
  </div>`;
}

/* ---------------- FAVORITES ---------------- */
function viewFavorites() {
  const items = DATA.filter(d => FAV.has(d.slug));
  return `<div class="shell">
    <nav class="crumbs" aria-label="Breadcrumbs"><a href="#/">Home</a><i>/</i><span aria-current="page">Favorites</span></nav>
    <div class="coll-top"><h1>Favorites</h1></div>
    ${items.length
      ? `<h2 class="count" style="margin-block:var(--gap-s) var(--gap-m)"><b>${items.length}</b> Saved ${items.length === 1 ? 'Item' : 'Items'}</h2>
         <div class="grid-works">${items.map(card).join('')}</div>`
      : `<div class="statepage"><h2 style="font-size:var(--t-h3)">Nothing saved yet</h2>
         <p>Tap the heart on any listing to keep it here while you decide. Saved items stay on this device.</p>
         <a class="btn btn--fill" href="#/browse">Shop the Collection <span class="arw" aria-hidden="true">→</span></a></div>`}
  </div>`;
}

/* ---------------- CART ---------------- */
function viewCart() {
  const items = DATA.filter(d => CART.has(d.slug));
  /* Fiyati girilmis eserler gercek fiyatiyla gorunur ve toplanir; fiyati
     gizli olanlar teklife kalir. Iki durum ayni sepette durabilir. */
  const fiyatli = items.filter(d => d.price != null && !d.sold);
  const toplam = fiyatli.reduce((t, d) => t + d.price, 0);
  const cur = (fiyatli[0] || {}).cur;
  const alinabilir = items.filter(d => satinAlinirMi(d));
  return `<div class="shell">
    <nav class="crumbs" aria-label="Breadcrumbs"><a href="#/">Home</a><i>/</i><span aria-current="page">Cart</span></nav>
    <div class="coll-top"><h1>Your Cart</h1></div>
    ${items.length ? `
      <div class="coll-body" style="grid-template-columns:minmax(0,1fr) 340px">
        <div>${items.map(d => `<div class="minirow">
          ${pic(cover(d), 't', '')}
          <div><b><a href="#/item/${d.slug}">${esc(d.title)}</a></b>
            <span>${esc(d.creator || 'Unknown')} · VO-${String(d.no).padStart(2, '0')}</span>
            <span>${fiyatHtml(d)}</span>
            ${satinAlinirMi(d) ? `<span style="margin-block-start:.3rem"><button class="btn btn--kucuk btn--line" type="button" data-buy="${d.slug}">Buy Now</button></span>` : ''}</div>
          <button type="button" data-uncart="${d.slug}">Remove</button></div>`).join('')}</div>
        <aside class="filters">
          <div class="info-card"><h2>Order Summary</h2>
            <p>${items.length} ${items.length === 1 ? 'item' : 'items'}${fiyatli.length && fiyatli.length < items.length ? `, ${fiyatli.length} priced` : ''}</p>
            <p><b>${fiyatli.length ? paraYaz(toplam, cur) + (fiyatli.length < items.length ? ' + quote' : '') : 'Price Upon Request'}</b></p>
            <p style="font-size:var(--t-xs);color:var(--ink-3)">${alinabilir.length === 1 && items.length === 1
              ? 'One-of-a-kind pieces are checked out one at a time.'
              : 'Each piece is one of a kind; ask once and we quote the lot together.'}</p>
            ${alinabilir.length === 1 && items.length === 1
              ? `<p style="margin-block-start:1rem"><button class="btn btn--fill" type="button" data-buy="${alinabilir[0].slug}" style="inline-size:100%">Checkout <span class="arw" aria-hidden="true">→</span></button></p>`
              : `<p style="margin-block-start:1rem"><button class="btn btn--fill" type="button" data-ask="teklif" style="inline-size:100%">Request a Quote <span class="arw" aria-hidden="true">→</span></button></p>`}
          </div>
          <div class="info-card"><h2>${ICON_SHIELD} Shop With Confidence</h2>
            <p>Authenticity Guaranteed, Money Back Guarantee, 24-Hour Cancellation.</p></div>
        </aside>
      </div>`
      : `<div class="statepage"><h2 style="font-size:var(--t-h3)">Your cart is empty</h2>
         <p>Every piece here is one of a kind. Add what you are considering and request a single quote for the lot.</p>
         <a class="btn btn--fill" href="#/browse">Shop the Collection <span class="arw" aria-hidden="true">→</span></a></div>`}
  </div>`;
}

/* ---------------- ACCOUNT ---------------- */
function viewAccount() {
  return `<div class="shell"><div class="statepage">
    <p class="eyebrow" style="justify-content:center">Account</p>
    <h1>You do not need an account to buy</h1>
    <p>There is one seller here, and everything happens by message: you ask, we answer, we agree a price, we ship. Your favorites and cart are saved on this device without a login.</p>
    <p style="margin-block-start:1rem">If you would like to be told when Persian rugs, lighting and sculpture are listed, leave your email in the footer.</p>
    <a class="btn btn--fill" href="#/info/how-it-works">How It Works <span class="arw" aria-hidden="true">→</span></a>
  </div></div>`;
}

/* ---------------- INFO PAGES ---------------- */
/* Panelden yazilan metin varsa o kazanir. Yoksa kodda duran metin kullanilir;
   panel doldurulmadan sayfa bos kalmaz. Eslesme: sayfalar tablosundaki anahtar
   ile buradaki slug. */
const SAYFA_ESLESME = { about:'hakkinda', shipping:'kargo', returns:'iade',
                        privacy:'gizlilik', terms:'sartlar' };
function viewInfo(slug) {
  const p = PAGES[slug];
  if (!p) return notFound('That page could not be found.');
  let [title, eyebrow, blocks] = p;
  const db = (typeof DBSAYFA !== 'undefined') && DBSAYFA[SAYFA_ESLESME[slug] || slug];
  if (db && db.icerik) {
    if (db.baslik) title = db.baslik;
    blocks = db.icerik.split(/\n{2,}/).map(par => {
      const satir = par.split('\n');
      return (satir.length > 1 && satir[0].length < 80 && !/[.!?]$/.test(satir[0]))
        ? [satir[0], satir.slice(1)]
        : ['', satir];
    });
  }
  const body = blocks.map(([h, paras]) =>
    (h ? `<h2>${esc(h)}</h2>` : '') + paras.map((t, i) =>
      `<p class="${!h && i === 0 ? 'lead' : ''}">${esc(t)}</p>`).join('')).join('');
  const others = Object.keys(PAGES).filter(k => k !== slug)
    .map(k => `<a href="#/info/${k}">${esc(PAGES[k][0])}</a>`).join('');
  return `<div class="shell">
    <nav class="crumbs" aria-label="Breadcrumbs"><a href="#/">Home</a><i>/</i><span aria-current="page">${esc(title)}</span></nav>
    <article class="doc" data-io>
      <p class="eyebrow up">${esc(eyebrow)}</p>
      <h1>${esc(title)}</h1>
      ${body}
      <nav class="doc-nav" aria-label="More information">${others}</nav>
    </article>
  </div>`;
}

/* ---------------- SITE MAP ---------------- */
function viewSitemap() {
  const cols = [
    ['Shop', [['All Items', '#/browse'], ['New Arrivals', '#/browse?cat=new'],
      ['Paintings & Prints', '#/browse?cat=tablo'], ['Handmade Objects', '#/browse?cat=obje'],
      ['Documents', '#/browse?cat=belge'], ['Persian Rug', '#/browse?cat=rugs'],
      ['Lighting', '#/browse?cat=lighting'], ['Sculpture', '#/browse?cat=sculpture'],
      ['Creators', '#/creators'],
      ['Collections', '#/collections'], ['The Museum', 'museum/index.html']]],
    ['Buy', [['How It Works', '#/info/how-it-works'], ['The Promise', '#/info/promise'],
      ['Shipping & Delivery', '#/info/shipping'], ['Returns & Cancellation', '#/info/returns'],
      ['Cart', '#/cart'], ['Favorites', '#/favorites']]],
    ['Support', [['Contact Us', '#/info/contact'], ['FAQ', '#/info/faq'], ['Account', '#/account']]],
    ['Company', [['About Us', '#/info/about'], ['User Agreement', '#/info/user-agreement'],
      ['Privacy Policy', '#/info/privacy'], ['Site Map', '#/sitemap']]],
  ];
  const colls = COLLECTIONS.map(c => `<a href="#/collection/${c.slug}">${esc(c.name)}</a>`).join('');
  return `<div class="shell">
    <nav class="crumbs" aria-label="Breadcrumbs"><a href="#/">Home</a><i>/</i><span aria-current="page">Site Map</span></nav>
    <div class="coll-top"><h1>Site Map</h1></div>
    <div class="maplist" style="margin-block:var(--gap-m)">
      ${cols.map(([h, ls]) => `<div><h2>${h}</h2>${ls.map(([t, u]) => `<a href="${u}">${esc(t)}</a>`).join('')}</div>`).join('')}
      <div><h2>Collections</h2>${colls}</div>
    </div>
  </div>`;
}

function notFound(msg) {
  return `<div class="shell"><div class="statepage">
    <p class="eyebrow" style="justify-content:center">404</p>
    <h1>Page not found</h1><p>${esc(msg)}</p>
    <a class="btn btn--fill" href="#/browse">Shop the Collection <span class="arw" aria-hidden="true">→</span></a>
  </div></div>`;
}

/* ---------------- shared: purchase protection block ---------------- */
function protectionBlock() {
  const P = [
    ['Authenticity Guaranteed', 'Signatures, edition numbers, back labels and certificates are photographed and shown with the listing.'],
    ['Money Back Guarantee', 'If a piece is not as described, return it within 14 days of delivery for a full refund.'],
    ['Price Matching', 'Find the same piece offered for less elsewhere and we will match the price.'],
    ['A Seller You Can Reach', 'One named collector, one inbox, typical response time the same day.'],
    ['24-Hour Cancellation', 'An order may be cancelled free of charge within twenty-four hours of confirmation.'],
    ['Protected Global Delivery', 'Crated or boarded as the piece requires, insured for its full agreed value, and tracked.'],
  ];
  return `<section class="sec sec--band" data-io aria-labelledby="h-conf">
  <div class="shell">
    <div class="sec-head"><h2 id="h-conf" class="rv"><span>Shop With Confidence</span></h2>
      <a class="lnk up" href="#/info/promise"><span>Learn More</span> <span class="arw" aria-hidden="true">→</span></a></div>
    <ul class="promise">
      ${P.map(([t, p], i) => `<li class="up" style="--i:${i % 4}"><h3>${t}</h3><p>${p}</p></li>`).join('')}
    </ul>
  </div>
</section>`;
}
"""
