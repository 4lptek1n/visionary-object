/* ===========================================================================
   Analitik sayfasi + Gelen kutusuna bulten bolumu.
   panel.js'in sonuna eklenir. Sayac cerezsizdir; burada yalnizca sayilir.
   =========================================================================== */

async function analitikSayfasi() {
  kabuk(`<div class="yukleniyor">Yukleniyor</div>`, "analitik");
  const gvd = document.getElementById("icerik");

  const otuzGun = new Date(Date.now() - 30 * 24 * 3600 * 1000).toISOString();
  const { data, error } = await sb.from("ziyaretler")
    .select("yol,kaynak,olusturuldu")
    .gt("olusturuldu", otuzGun)
    .order("olusturuldu", { ascending: false })
    .limit(20000);
  if (error) return void (gvd.innerHTML = hataKutusu(error));

  const v = data || [];
  const simdi = Date.now();
  const gunMs = 24 * 3600 * 1000;
  const bugun = v.filter(x => simdi - new Date(x.olusturuldu).getTime() < gunMs).length;
  const hafta = v.filter(x => simdi - new Date(x.olusturuldu).getTime() < 7 * gunMs).length;

  function say(liste, al) {
    const m = new Map();
    for (const x of liste) {
      const k = al(x);
      if (k) m.set(k, (m.get(k) || 0) + 1);
    }
    return [...m.entries()].sort((a, b) => b[1] - a[1]);
  }
  const sayfalar = say(v, x => x.yol).slice(0, 12);
  const eserler = say(v.filter(x => x.yol.indexOf("#/item/") === 0),
                      x => x.yol.slice(7)).slice(0, 10);
  const kaynaklar = say(v, x => x.kaynak).slice(0, 10);

  // Gunluk cizgi: son 14 gun, en yogun gune gore olceklenmis yatay cubuklar.
  const gunler = [];
  for (let i = 13; i >= 0; i--) {
    const bas = new Date(simdi - i * gunMs);
    const ad = bas.toLocaleDateString("tr-TR", { day: "numeric", month: "short" });
    const n = v.filter(x => {
      const t = simdi - new Date(x.olusturuldu).getTime();
      return t >= (i) * gunMs - (simdi % gunMs) && t < (i + 1) * gunMs - (simdi % gunMs);
    }).length;
    gunler.push([ad, n]);
  }
  const enCok = Math.max(1, ...gunler.map(g => g[1]));

  const YOL_ADI = y => y === "#/" ? "Ana sayfa"
    : y.indexOf("#/item/") === 0 ? "Eser: " + y.slice(7)
    : y.indexOf("#/browse") === 0 ? "Vitrin"
    : y.indexOf("#/info/") === 0 ? "Sayfa: " + y.slice(7)
    : y;

  gvd.innerHTML = `
  <div class="ustbilgi"><div><h1>Analitik</h1>
    <p>Cerezsiz, birinci taraf sayac: yalnizca sayfa yolu ve geldigi site tutulur.
       IP, cerez ve kisisel veri yok. Panele girisli olanlar sayilmaz.</p></div></div>

  <div class="ozet">
    <div><b>${bugun}</b><span>Bugun</span></div>
    <div><b>${hafta}</b><span>Son 7 gun</span></div>
    <div><b>${v.length}</b><span>Son 30 gun</span></div>
  </div>

  <div class="kutu" style="padding:1.25rem;margin-block-end:.75rem">
    <h3 style="margin-block-end:.75rem">Son 14 gun</h3>
    ${gunler.map(([ad, n]) => `
      <div style="display:grid;grid-template-columns:5.5rem 1fr 3rem;gap:.6rem;align-items:center;margin-block-end:.35rem">
        <span class="ipucu">${ad}</span>
        <span style="display:block;block-size:10px;background:var(--pnl-band);border-radius:2px;overflow:hidden">
          <span style="display:block;block-size:100%;inline-size:${Math.round(n / enCok * 100)}%;background:var(--pnl-ink)"></span></span>
        <span class="sayisal" style="font-size:.8125rem;text-align:end">${n}</span>
      </div>`).join("")}
  </div>

  <div class="ikili">
    <div class="kutu" style="padding:1.25rem">
      <h3 style="margin-block-end:.75rem">En cok bakilan eserler</h3>
      ${!eserler.length ? `<div class="bos" style="padding:1.5rem">Henuz veri yok.</div>`
        : eserler.map(([slug, n]) => `
        <div style="display:flex;justify-content:space-between;gap:1rem;padding-block:.35rem;border-block-end:1px solid var(--pnl-line)">
          <a href="https://thetimesfigures.com/#/item/${esc(slug)}" target="_blank" rel="noopener">${esc(slug)}</a>
          <span class="sayisal">${n}</span></div>`).join("")}
    </div>
    <div class="kutu" style="padding:1.25rem">
      <h3 style="margin-block-end:.75rem">Nereden geliyorlar</h3>
      ${!kaynaklar.length ? `<div class="bos" style="padding:1.5rem">Dogrudan girisler disinda kaynak yok.</div>`
        : kaynaklar.map(([k, n]) => `
        <div style="display:flex;justify-content:space-between;gap:1rem;padding-block:.35rem;border-block-end:1px solid var(--pnl-line)">
          <span>${esc(k)}</span><span class="sayisal">${n}</span></div>`).join("")}
    </div>
  </div>

  <div class="kutu" style="padding:1.25rem;margin-block-start:.75rem">
    <h3 style="margin-block-end:.75rem">En cok gezilen sayfalar</h3>
    ${sayfalar.map(([y, n]) => `
      <div style="display:flex;justify-content:space-between;gap:1rem;padding-block:.35rem;border-block-end:1px solid var(--pnl-line)">
        <span>${esc(YOL_ADI(y))}</span><span class="sayisal">${n}</span></div>`).join("")}
  </div>

  <div class="kutu" style="padding:1.25rem;margin-block-start:.75rem">
    <h3>Temizlik</h3>
    <p class="ipucu" style="margin-block-end:.75rem">90 gunden eski kayitlari silmek tabloyu kucuk tutar; raporlar son 30 gune bakar.</p>
    <button class="btn btn--kucuk" id="analitikTemizle">90 gunden eskiyi sil</button>
  </div>`;

  document.getElementById("analitikTemizle").addEventListener("click", async () => {
    const sinir = new Date(Date.now() - 90 * 24 * 3600 * 1000).toISOString();
    const { error } = await sb.from("ziyaretler").delete().lt("olusturuldu", sinir);
    bildir(error ? error.message : "Eski kayitlar silindi.", !!error);
  });
}
