# -*- coding: utf-8 -*-
"""Session state (favorites, cart, recently viewed) and the chrome behaviours
1stDibs has: typeahead, cart drawer, quick view, lightbox, cookie bar, auth."""

STATE_JS = r"""
/* ---------------- session state (in memory, no storage) ---------------- */
const FAV = new Set();
const CART = new Set();
const RECENT = [];
function remember(slug) {
  const i = RECENT.indexOf(slug);
  if (i > -1) RECENT.splice(i, 1);
  RECENT.unshift(slug);
  RECENT.length = Math.min(RECENT.length, 8);
}
function badge(id, n, one, many) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = n;
  el.hidden = !n;
  el.setAttribute('aria-hidden', 'true');
  const host = el.parentElement;
  host.setAttribute('aria-label', n ? `${many}, ${n} ${n === 1 ? one : one + 's'}` : many);
}
function syncCounts() {
  badge('favCount', FAV.size, 'item', 'Favorites');
  badge('cartCount', CART.size, 'item', 'Cart');
}

/* ---------------- favorites ---------------- */
document.addEventListener('click', e => {
  const f = e.target.closest('.fav');
  if (!f) return;
  e.preventDefault();
  const slug = f.dataset.slug || (f.closest('[data-slug]') || {}).dataset?.slug;
  const on = f.dataset.on === '1';
  f.dataset.on = on ? '0' : '1';
  const svg = f.querySelector('svg');
  if (svg) svg.setAttribute('fill', on ? 'none' : 'currentColor');
  f.style.color = on ? '' : 'var(--ink)';
  if (slug) { on ? FAV.delete(slug) : FAV.add(slug); syncCounts(); }
});

/* ---------------- cart ---------------- */
const drawer = document.getElementById('cartDrawer');
const scrim = document.getElementById('scrim');
function drawCart() {
  const body = document.getElementById('cartBody');
  const items = DATA.filter(d => CART.has(d.slug));
  body.innerHTML = items.length
    ? items.map(d => `<div class="minirow">
        ${pic(cover(d), 't', '')}
        <div><b>${esc(d.title)}</b><span>${esc(d.creator || 'Unknown')} &middot; VO-${String(d.no).padStart(2, '0')}</span>
          <span>Price Upon Request</span></div>
        <button type="button" data-uncart="${d.slug}">Remove</button></div>`).join('')
    : `<p style="color:var(--ink-2);font-size:.95rem">Your bag is empty. Add the pieces you are considering and request a single quote for the lot.</p>`;
  document.getElementById('cartFootN').textContent =
    items.length + (items.length === 1 ? ' item' : ' items');
}
function openCart(on) {
  if (on) drawCart();
  drawer.toggleAttribute('data-open', on);
  scrim.toggleAttribute('data-open', on);
  drawer.setAttribute('aria-hidden', String(!on));
  if (on) drawer.querySelector('button').focus();
}
document.getElementById('cartBtn').addEventListener('click', () => openCart(true));

/* --- mobil gezinme cekmecesi --- */
const navDrawer = document.getElementById('navDrawer');
const navBtn = document.getElementById('navBtn');
function openNav(on) {
  navDrawer.toggleAttribute('data-open', on);
  scrim.toggleAttribute('data-open', on);
  navDrawer.setAttribute('aria-hidden', String(!on));
  if (navBtn) navBtn.setAttribute('aria-expanded', String(on));
  if (on) navDrawer.querySelector('a, button').focus();
  else if (navBtn) navBtn.focus();
}
if (navBtn) navBtn.addEventListener('click', () => openNav(true));
navDrawer.addEventListener('click', e => {
  if (e.target.closest('[data-drawer-close]') || e.target.closest('a')) openNav(false);
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && navDrawer.hasAttribute('data-open')) openNav(false);
});

scrim.addEventListener('click', () => { openCart(false); openNav(false); });
drawer.addEventListener('click', e => {
  if (e.target.closest('[data-drawer-close]')) openCart(false);
});
document.addEventListener('click', e => {
  const add = e.target.closest('[data-cart]');
  if (add) {
    const slug = add.dataset.cart;
    if (CART.has(slug)) { CART.delete(slug); add.textContent = 'Add to Cart'; }
    else { CART.add(slug); add.textContent = 'In Your Cart'; openCart(true); }
    syncCounts();
  }
  const rm = e.target.closest('[data-uncart]');
  if (rm) {
    CART.delete(rm.dataset.uncart);
    syncCounts(); drawCart();
    if (location.hash.startsWith('#/cart')) render();
  }
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && drawer.hasAttribute('data-open')) openCart(false);
});

/* ---------------- search typeahead ---------------- */
const sugg = document.getElementById('sugg');
const qEl = document.getElementById('q');
const searchForm = document.getElementById('searchForm');
function suggest(v) {
  const t = v.trim().toLowerCase();
  if (t.length < 2) { sugg.hidden = true; qEl.setAttribute('aria-expanded', 'false'); return; }
  const hay = d => (d.title + ' ' + d.creator + ' ' + d.desc + ' ' + d.catEn).toLowerCase();
  const hits = DATA.filter(d => hay(d).includes(t)).slice(0, 6);
  const names = [...new Set(DATA.map(d => d.creator).filter(c => c && c.toLowerCase().includes(t)))].slice(0, 3);
  if (!hits.length && !names.length) { sugg.hidden = true; qEl.setAttribute('aria-expanded', 'false'); return; }
  sugg.innerHTML =
    (names.length ? `<h4>Creators</h4>` + names.map(n =>
      `<a role="option" href="#/browse?artist=${encodeURIComponent(n)}"><b>${esc(n)}</b></a>`).join('') : '') +
    (hits.length ? `<h4>Items</h4>` + hits.map(d =>
      `<a role="option" href="#/item/${d.slug}">${pic(cover(d), 't', '')}
        <span><b>${esc(d.title)}</b><span>${esc(d.creator || 'Unknown')}</span></span></a>`).join('') : '') +
    `<a class="all" role="option" href="#/browse?q=${encodeURIComponent(v.trim())}">
      <span>See all results for &ldquo;${esc(v.trim())}&rdquo;</span><span aria-hidden="true">&#8594;</span></a>`;
  sugg.hidden = false;
  qEl.setAttribute('aria-expanded', 'true');
}
if (qEl) {
  let st;
  qEl.addEventListener('input', () => {
    searchForm.toggleAttribute('data-has', !!qEl.value);
    clearTimeout(st); st = setTimeout(() => suggest(qEl.value), 160);
  });
  qEl.addEventListener('focus', () => { if (qEl.value.trim().length > 1) suggest(qEl.value); });
  document.getElementById('qClear').addEventListener('click', () => {
    qEl.value = ''; searchForm.removeAttribute('data-has'); sugg.hidden = true; qEl.focus();
  });
  document.addEventListener('click', e => {
    if (!e.target.closest('#searchForm')) { sugg.hidden = true; qEl.setAttribute('aria-expanded', 'false'); }
  });
  qEl.addEventListener('keydown', e => {
    if (e.key === 'Escape') { sugg.hidden = true; qEl.setAttribute('aria-expanded', 'false'); }
    if (e.key === 'ArrowDown' && !sugg.hidden) { e.preventDefault(); const a = sugg.querySelector('a'); if (a) a.focus(); }
  });
  searchForm.addEventListener('submit', e => {
    e.preventDefault();
    const v = qEl.value.trim();
    sugg.hidden = true;
    go('#/browse' + (v ? '?q=' + encodeURIComponent(v) : ''));
  });
}

/* ---------------- quick view ---------------- */
const qvDlg = document.getElementById('qv');
document.addEventListener('click', e => {
  const b = e.target.closest('[data-qv]');
  if (!b) return;
  e.preventDefault();
  const d = DATA.find(x => x.slug === b.dataset.qv);
  if (!d) return;
  document.getElementById('qvBody').innerHTML = `
    <div class="qvbox">
      <figure>${pic(cover(d), 'c', esc(d.title))}</figure>
      <div>
        <p class="eyebrow">${esc(d.catEn)}</p>
        <p class="creatorline" style="margin-block:.6rem .2rem">${esc(d.creator || 'Unknown')}</p>
        <h2 style="font-size:var(--t-h4);line-height:1.2">${esc(d.title)}</h2>
        <p style="font-family:var(--f-mono);margin-block:.8rem">Price Upon Request</p>
        <p style="color:var(--ink-2);font-size:.94rem;line-height:1.65">${esc(d.desc.slice(0, 240))}${d.desc.length > 240 ? '&hellip;' : ''}</p>
        <dl>
          <div><dt>Located in</dt><dd>Virginia, United States</dd></div>
          <div><dt>Category</dt><dd>${esc(d.catEn)}</dd></div>
          <div><dt>Photographs</dt><dd>${d.shots}</dd></div>
          <div><dt>Reference</dt><dd>VO-${String(d.no).padStart(2, '0')}</dd></div>
        </dl>
        <a class="btn btn--fill" href="#/item/${d.slug}" data-qv-go>View Full Details <span class="arw" aria-hidden="true">&#8594;</span></a>
      </div>
    </div>`;
  qvDlg.showModal();
});
qvDlg.addEventListener('click', e => {
  if (e.target.closest('[data-close]') || e.target.closest('[data-qv-go]')) qvDlg.close();
});

/* ---------------- lightbox ---------------- */
const lb = document.getElementById('lb');
let lbImgs = [], lbI = 0;
function lbShow(n) {
  lbI = (n + lbImgs.length) % lbImgs.length;
  lbUnzoom();
  document.getElementById('lbImg').src = lbImgs[lbI];
  document.getElementById('lbCap').textContent = `${lbI + 1} of ${lbImgs.length}`;
}

/* Tam ekranda yaklas ve gezin. Dokunmatikte buyutec calismadigi icin
   detaya bakmanin yolu bu: bir kez dokun, fotografin kendi cozunurlugune
   yaklasir; parmagini surterek gezinirsin. */
function lbUnzoom() {
  const im = document.getElementById('lbImg');
  if (!im) return;
  im.removeAttribute('data-zoom');
  im.removeAttribute('data-grab');
  im.style.transform = '';
  im.style.transformOrigin = '';
}
(function lbZoomKur() {
  const im = document.getElementById('lbImg');
  if (!im) return;
  let sur = false, ox = 0, oy = 0, tx = 0, ty = 0, K = 1;
  const uygula = () => { im.style.transform = `translate(${tx}px,${ty}px) scale(${K})`; };
  const sinirla = () => {
    const r = im.getBoundingClientRect();
    const tasx = Math.max(0, (im.offsetWidth * K - innerWidth) / 2);
    const tasy = Math.max(0, (im.offsetHeight * K - innerHeight) / 2);
    tx = Math.min(tasx, Math.max(-tasx, tx));
    ty = Math.min(tasy, Math.max(-tasy, ty));
    return r;
  };
  im.addEventListener('click', e => {
    e.stopPropagation();
    if (im.hasAttribute('data-zoom')) { lbUnzoom(); K = 1; tx = ty = 0; return; }
    K = Math.min(3.2, Math.max(1.8, (im.naturalWidth || 1400) / Math.max(1, im.offsetWidth)));
    const r = im.getBoundingClientRect();
    // tiklanan nokta ekranin ortasina gelsin
    tx = (r.left + r.width / 2 - e.clientX) * K;
    ty = (r.top + r.height / 2 - e.clientY) * K;
    im.setAttribute('data-zoom', '');
    sinirla(); uygula();
  });
  im.addEventListener('pointerdown', e => {
    if (!im.hasAttribute('data-zoom')) return;
    sur = true; ox = e.clientX - tx; oy = e.clientY - ty;
    im.setAttribute('data-grab', '');
    im.setPointerCapture(e.pointerId);
  });
  im.addEventListener('pointermove', e => {
    if (!sur) return;
    tx = e.clientX - ox; ty = e.clientY - oy;
    sinirla(); uygula();
  });
  const birak = e => {
    if (!sur) return;
    sur = false; im.removeAttribute('data-grab');
    try { im.releasePointerCapture(e.pointerId); } catch (_) {}
  };
  im.addEventListener('pointerup', birak);
  im.addEventListener('pointercancel', birak);
})();
function lbOpen(imgs, i) {
  if (!imgs.length) return;
  lbImgs = imgs; lb.hidden = false; document.body.style.overflow = 'hidden';
  lbShow(i); document.getElementById('lbClose').focus();
}
function lbClose() { lbUnzoom(); lb.hidden = true; document.body.style.overflow = ''; }
lb.addEventListener('click', e => {
  if (e.target.closest('#lbClose') || e.target === lb) return lbClose();
  const n = e.target.closest('[data-lb]');
  if (n) lbShow(lbI + (+n.dataset.lb));
});
document.addEventListener('keydown', e => {
  if (lb.hidden) return;
  if (e.key === 'Escape') lbClose();
  if (e.key === 'ArrowRight') lbShow(lbI + 1);
  if (e.key === 'ArrowLeft') lbShow(lbI - 1);
});

/* ---------------- details dialog (shipping / returns / promise) ---------------- */
const detDlg = document.getElementById('det');
document.addEventListener('click', e => {
  const b = e.target.closest('[data-det]');
  if (!b) return;
  const p = PAGES[b.dataset.det];
  if (!p) return;
  document.getElementById('detBody').innerHTML =
    `<p class="eyebrow">${esc(p[1])}</p><h2 style="font-size:var(--t-h3);margin-block:.6rem 1rem">${esc(p[0])}</h2>` +
    p[2].slice(0, 3).map(([h, ps]) => (h ? `<h3 style="margin-block:1.2rem .4rem;font-size:1rem">${esc(h)}</h3>` : '') +
      ps.map(t => `<p style="color:var(--ink-2);font-size:.94rem;line-height:1.7;margin-block-end:.7rem">${esc(t)}</p>`).join('')).join('') +
    `<p style="margin-block-start:1.4rem"><a class="btn btn--line" href="#/info/${b.dataset.det}" data-det-go>Read the Full Policy <span class="arw" aria-hidden="true">&#8594;</span></a></p>`;
  detDlg.showModal();
});
detDlg.addEventListener('click', e => {
  if (e.target.closest('[data-close]') || e.target.closest('[data-det-go]')) detDlg.close();
});

/* ---------------- auth dialog ---------------- */
const authDlg = document.getElementById('auth');
document.addEventListener('click', e => {
  const b = e.target.closest('[data-auth]');
  if (!b) return;
  const up = b.dataset.auth === 'up';
  document.getElementById('authTitle').textContent = up ? 'Create an account' : 'Log in';
  document.getElementById('authBody').innerHTML = up
    ? `<p>You do not need an account to buy here. There is one seller, and everything happens by message: you ask, we answer, we agree a price, we ship.</p>
       <p>Leave your email in the footer and we will tell you when new pieces are listed, including rugs, carpets and lighting.</p>`
    : `<p>There are no accounts on this site. Your favorites and cart are kept for this visit without a login, and every enquiry is answered by the collector personally.</p>
       <p>If you have an order in progress, reply to the email thread you already have with the seller.</p>`;
  authDlg.showModal();
});
authDlg.addEventListener('click', e => { if (e.target.closest('[data-close]')) authDlg.close(); });

/* ---------------- newsletter ---------------- */
const nf = document.getElementById('newsForm');
if (nf) nf.addEventListener('submit', e => {
  e.preventDefault();
  const v = document.getElementById('nl').value.trim();
  const ok = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v);
  const note = document.getElementById('newsNote');
  document.getElementById('nl').setAttribute('aria-invalid', String(!ok));
  note.textContent = ok
    ? 'Thank you. We will write when new pieces are listed. This is a prototype: nothing is sent yet.'
    : 'Please enter a valid email address.';
});

/* ---------------- cookie bar ---------------- */
const ck = document.getElementById('cookie');
function ckMeasure() {
  document.body.style.setProperty('--ck-h', ck.hidden ? '0px' : (ck.offsetHeight + 12) + 'px');
}
function ckShow(on) { ck.hidden = !on; ckMeasure(); }
new ResizeObserver(ckMeasure).observe(ck);
ckMeasure();
document.getElementById('ckPrefs').addEventListener('click', () => ckShow(true));
ck.addEventListener('click', e => { if (e.target.closest('[data-ck]')) ckShow(false); });

/* ---------------- back to top (observer, never a scroll listener) ---------------- */
const toTop = document.getElementById('toTop');
new IntersectionObserver(es => {
  toTop.hidden = es[0].isIntersecting;
}, { threshold: 0 }).observe(document.getElementById('topSentinel'));
toTop.addEventListener('click', () => {
  window.scrollTo({ top: 0, behavior: RM.matches ? 'auto' : 'smooth' });
  document.querySelector('.brand').focus?.();
});

/* ---------------- mega menu images ---------------- */
function fillMegaImages() {
  document.querySelectorAll('[data-mega-img]').forEach(el => {
    const k = el.dataset.megaImg;
    const pool = DATA.filter(d => d.cat === k && cover(d));
    const d = pool[pool.length - 1] || DATA.find(x => cover(x));
    if (d) el.style.backgroundImage = `url("${cover(d).c}")`;
  });
}
"""
