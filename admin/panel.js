/* Visionary Object - yonetim paneli
 * Tek dosya, cerceve yok. Supabase ile dogrudan konusur; araya sunucu girmez.
 * Yetkiyi veritabani verir (RLS), bu dosya degil: burada bir kontrolu atlamak
 * veriye erismeye yetmez.
 */
import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm";

// Supabase bagliysa gercek istemci; degilse onizleme.js'in sahte istemcisi.
const sb = window.__VO_SB || createClient(window.VO.URL, window.VO.ANAHTAR);
const ONIZLEME = !!(sb && sb.ONIZLEME);
const kok = document.getElementById("kok");
const bildirimKutu = document.getElementById("bildirim");

let oturum = null, profil = null;
const durumState = { ilanlar: [], sayfa: 1, adet: 25, arama: "", suzgec: "hepsi", kat: "hepsi", siralama: "no-desc" };

/* ------------------------------------------------------------------ araclar */
const esc = s => String(s ?? "").replace(/[&<>"']/g, c =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function bildir(mesaj, hata = false) {
  const d = document.createElement("div");
  if (hata) d.className = "hata";
  d.textContent = mesaj;
  bildirimKutu.append(d);
  setTimeout(() => d.remove(), hata ? 6000 : 3200);
}

const para = (deger, birim = "USD") =>
  deger == null || deger === "" ? "" :
  new Intl.NumberFormat("en-US", { style: "currency", currency: birim, maximumFractionDigits: 0 })
    .format(Number(deger));

function gorselUrl(yol, boy = 400) {
  if (!yol) return "";
  // Tasima sirasinda gelen kareler sitedeki mevcut webp dosyasini gosterir.
  // Depoya yuklenmedikleri icin Supabase'e sorulmaz, dogrudan siteden alinir.
  if (yol.indexOf("img/") === 0) {
    const boyut = boy <= 200 ? "t" : boy <= 700 ? "c" : "f";
    return (window.VO.SITE || "") + "/" + yol + "-" + boyut + ".webp";
  }
  const t = sb.storage.from("gorseller").getPublicUrl(yol, {
    transform: { width: boy, height: boy, resize: "contain" }
  });
  return t.data.publicUrl;
}

async function sor(soru, onay = "Sil") {
  return new Promise(cevapla => {
    const d = document.createElement("dialog");
    d.innerHTML = `<h2>${esc(soru)}</h2>
      <p style="color:var(--pnl-ink-2);margin:.75rem 0 1.5rem">Bu islem geri alinamaz.</p>
      <div class="eylemler" style="justify-content:flex-end">
        <button class="btn btn--line" value="iptal">Vazgec</button>
        <button class="btn btn--tehlike" value="tamam">${esc(onay)}</button>
      </div>`;
    document.body.append(d);
    d.showModal();
    d.addEventListener("click", e => {
      const b = e.target.closest("button");
      if (!b) return;
      d.close(); d.remove(); cevapla(b.value === "tamam");
    });
    d.addEventListener("cancel", () => { d.remove(); cevapla(false); });
  });
}

/* Veritabani henuz kurulmamissa PostgREST "tablo yok" der. Ham hata yerine
   ne yapilacagini yaziyoruz. */
function hataKutusu(hata) {
  const kurulmamis = hata && (hata.code === "PGRST205" ||
    /schema cache|does not exist|Could not find the table/i.test(hata.message || ""));
  if (!kurulmamis) return `<p class="uyari-serit uyari-serit--hata">${esc(hata.message || hata)}</p>`;
  return `<div class="kutu" style="padding:2rem;max-inline-size:640px">
    <h2>Veritabani henuz kurulmadi</h2>
    <p style="color:var(--pnl-ink-2);margin-block-start:.75rem">
      Supabase projesi bagli ve calisiyor, ama tablolar acilmamis. Supabase panelinde
      <b>SQL Editor</b> bolumune gec ve su iki dosyayi sirayla yapistirip calistir:</p>
    <ol style="color:var(--pnl-ink-2);margin:1rem 0 0 1.2rem;line-height:2">
      <li><code>supabase/KUR.sql</code> - tablolar, erisim kurallari, kampanya sistemi</li>
      <li><code>supabase/VERI.sql</code> - 270 ilan ve 879 gorsel</li>
    </ol>
    <p style="margin-block-start:1.25rem"><button class="btn" onclick="location.reload()">Kurdum, yenile</button></p>
  </div>`;
}

const YETKI = () => profil && (profil.rol === "sahip" || profil.rol === "yonetici");
const SAHIP = () => profil && profil.rol === "sahip";

/* ------------------------------------------------------------------- giris */
function girisEkrani(hataMesaji = "") {
  kok.innerHTML = `
  <div class="giris">
    <form id="giris-form">
      <div>
        <p class="marka">Visionary Object</p>
        <p class="alt">Yonetim paneli${typeof ONIZLEME !== "undefined" && ONIZLEME ? " - onizleme" : ""}</p>
      </div>
      ${hataMesaji ? `<p class="uyari-serit uyari-serit--hata" role="alert">${esc(hataMesaji)}</p>` : ""}
      <div class="alan">
        <label for="eposta">E-posta</label>
        <input id="eposta" type="email" autocomplete="username" required>
      </div>
      <div class="alan">
        <label for="sifre">Sifre</label>
        <input id="sifre" type="password" autocomplete="current-password" required>
      </div>
      <button class="btn" type="submit">Giris yap</button>
      <div style="display:flex;gap:.5rem;flex-wrap:wrap">
        <button class="btn btn--line btn--kucuk" type="button" id="sifre-unuttum">Sifremi unuttum</button>
        <button class="btn btn--line btn--kucuk" type="button" id="hesap-ac">Hesap olustur</button>
      </div>
      ${typeof ONIZLEME !== "undefined" && ONIZLEME ? `<p style="font-size:.75rem;color:var(--pnl-ink-3);line-height:1.5;margin-block-start:.25rem">
        Onizleme kilidi. Denetim tarayicida yapiliyor, yani bu bir perde; gercek kilit
        Supabase baglandiginda gelir. E-posta alanina istedigini yazabilirsin.</p>` : ""}
    </form>
  </div>`;

  document.getElementById("giris-form").addEventListener("submit", async e => {
    e.preventDefault();
    const btn = e.target.querySelector("button[type=submit]");
    btn.disabled = true; btn.textContent = "Giriliyor";
    const { error } = await sb.auth.signInWithPassword({
      email: document.getElementById("eposta").value.trim(),
      password: document.getElementById("sifre").value
    });
    if (error) { girisEkrani("E-posta ya da sifre dogru degil."); return; }
    baslat();
  });

  const hesapDugme = document.getElementById("hesap-ac");
  if (hesapDugme) hesapDugme.addEventListener("click", async () => {
    const e = document.getElementById("eposta").value.trim();
    const p = document.getElementById("sifre").value;
    if (!e || p.length < 8) return bildir("E-posta yaz ve en az sekiz karakterlik bir sifre sec.", true);
    hesapDugme.disabled = true; hesapDugme.textContent = "Aciliyor";
    const { data, error } = await sb.auth.signUp({ email: e, password: p });
    hesapDugme.disabled = false; hesapDugme.textContent = "Hesap olustur";
    if (error) return bildir(error.message, true);
    if (data && data.session) { baslat(); return; }
    bildir("Hesap acildi. E-postana gelen dogrulama baglantisina tikla, sonra giris yap.");
  });

  document.getElementById("sifre-unuttum").addEventListener("click", async () => {
    const e = document.getElementById("eposta").value.trim();
    if (!e) return bildir("Once e-posta adresini yaz.", true);
    const { error } = await sb.auth.resetPasswordForEmail(e, { redirectTo: location.href });
    bildir(error ? error.message : "Sifre yenileme baglantisi gonderildi.", !!error);
  });
}

/* ------------------------------------------------------------------- kabuk */
const MENU = [
  ["ilanlar",     "Ilanlar",      "▤"],
  ["fiyatlar",    "Fiyatlar",     "$"],
  ["kampanyalar", "Kampanyalar",  "%"],
  ["sayfalar",    "Site metinleri", "¶"],
  ["sanatcilar",  "Sanatcilar",   "✎"],
  ["ayarlar",     "Ayarlar",      "⚙"],
  ["kullanicilar","Kullanicilar", "◍"],
  ["gecmis",      "Gecmis",       "↺"],
];

function kabuk(icerik, aktif) {
  kok.innerHTML = `
  <div class="kabuk">
    <aside class="ray">
      <div class="ust">
        <b>Visionary Object</b>
        <span>Yonetim</span>
      </div>
      <nav>
        ${MENU.filter(m => m[0] !== "kullanicilar" || SAHIP())
              .map(([k, ad, ik]) => `<a href="#/${k}" ${k === aktif ? 'aria-current="page"' : ""}>
                 <i aria-hidden="true">${ik}</i>${esc(ad)}</a>`).join("")}
      </nav>
      <div class="dip">
        <p>${esc(profil?.ad || profil?.eposta || "")}</p>
        <p style="text-transform:capitalize">${esc(profil?.rol || "")}</p>
        <button class="btn btn--line btn--kucuk" id="cikis" style="margin-block-start:.6rem">Cikis</button>
      </div>
    </aside>
    <main class="govde">
      <div class="cubuk">
        <div class="ara">
          <label class="sr" for="genel-ara">Ilanlarda ara</label>
          <input id="genel-ara" type="search" placeholder="Baslik, sanatci ya da ilan numarasi" value="${esc(durumState.arama)}">
        </div>
        <div class="eylemler" style="margin-inline-start:auto">
          <a class="btn btn--line btn--kucuk" href="${esc(window.VO.SITE)}" target="_blank" rel="noopener">Siteyi gor</a>
          <button class="btn btn--kucuk" id="yayinla">Yayinla</button>
        </div>
      </div>
      <div class="icerik" id="icerik">${ONIZLEME ? `<p class="uyari-serit uyari-serit--hata" style="border-color:var(--pnl-uyari);color:var(--pnl-uyari);background:#FDF9F0">
        Onizleme modu. Veriler gercek, ekranlar gercek; ama Supabase bagli olmadigi icin
        hicbir degisiklik kaydedilmez. Kurulum bitince bu serit kaybolur.</p>` : ""}${icerik}</div>
    </main>
  </div>`;

  document.getElementById("cikis").addEventListener("click", async () => {
    await sb.auth.signOut(); location.hash = ""; baslat();
  });
  document.getElementById("yayinla").addEventListener("click", yayinla);
  const ara = document.getElementById("genel-ara");
  let zaman;
  ara.addEventListener("input", () => {
    clearTimeout(zaman);
    zaman = setTimeout(() => {
      durumState.arama = ara.value.trim();
      durumState.sayfa = 1;
      if (location.hash.startsWith("#/ilanlar") || location.hash === "" ) ilanlarSayfasi();
      else location.hash = "#/ilanlar";
    }, 260);
  });
}

async function yayinla() {
  if (!YETKI()) return bildir("Yayinlama yetkin yok.", true);
  const btn = document.getElementById("yayinla");
  btn.disabled = true; btn.textContent = "Gonderiliyor";
  const { error } = await sb.from("yayin_istek").insert({
    isteyen: oturum.user.id, mesaj: "Panelden istendi"
  });
  btn.disabled = false; btn.textContent = "Yayinla";
  if (error) return bildir("Yayin istegi gonderilemedi: " + error.message, true);
  bildir("Yayin sıraya alindi. Site birkac dakika icinde guncellenir.");
}

/* ---------------------------------------------------------------- ilanlar */
const KATLAR = [["tablo","Paintings & Prints"],["obje","Handmade Objects"],["belge","Documents"],
                ["rugs","Persian Rug"],["lighting","Lighting"],["sculpture","Sculpture"]];
const DURUMLAR = [["taslak","Taslak"],["yayinda","Yayinda"],["rezerve","Rezerve"],
                  ["satildi","Satildi"],["arsiv","Arsiv"]];

function durumRozet(d) {
  const sinif = d === "yayinda" ? "rozet--yayinda" : d === "taslak" ? "rozet--taslak"
              : (d === "satildi" || d === "rezerve") ? "rozet--satildi" : "";
  const ad = (DURUMLAR.find(x => x[0] === d) || [d, d])[1];
  return `<span class="rozet ${sinif}"><i></i>${esc(ad)}</span>`;
}

async function ilanlarSayfasi() {
  kabuk(`<div class="yukleniyor">Ilanlar yukleniyor</div>`, "ilanlar");
  const gvd = document.getElementById("icerik");

  let q = sb.from("ilanlar")
    .select("id,no,slug,kat,durum,baslik,sanatci,fiyat,para_birimi,fiyat_gizli,olcu_w,olcu_h,guncellendi,kareler(yol,sira)",
            { count: "exact" });

  if (durumState.suzgec !== "hepsi") q = q.eq("durum", durumState.suzgec);
  if (durumState.kat !== "hepsi") q = q.eq("kat", durumState.kat);
  if (durumState.arama) {
    const a = durumState.arama.replace(/[%,()]/g, " ");
    q = /^\d+$/.test(a)
      ? q.eq("no", Number(a))
      : q.or(`baslik.ilike.%${a}%,sanatci.ilike.%${a}%,slug.ilike.%${a}%`);
  }
  const [alan, yon] = durumState.siralama.split("-");
  q = q.order(alan, { ascending: yon === "asc" });
  const bas = (durumState.sayfa - 1) * durumState.adet;
  q = q.range(bas, bas + durumState.adet - 1);

  const { data, error, count } = await q;
  if (error) { gvd.innerHTML = hataKutusu(error); return; }

  const sayfaSayisi = Math.max(1, Math.ceil((count || 0) / durumState.adet));
  const secenek = (liste, secili) => liste.map(([v, ad]) =>
    `<option value="${v}" ${v === secili ? "selected" : ""}>${esc(ad)}</option>`).join("");

  gvd.innerHTML = `
  <div class="ustbilgi">
    <div>
      <h1>Ilanlar</h1>
      <p>${count || 0} kayit. Bir satira tiklayarak ilanin tamamini duzenleyebilirsin.</p>
    </div>
    <div class="eylemler">
      <button class="btn" id="yeni-ilan">Yeni ilan</button>
    </div>
  </div>

  <div class="kutu" style="padding:.85rem 1rem;margin-block-end:1rem;display:flex;gap:1rem;flex-wrap:wrap;align-items:end">
    <div style="min-inline-size:170px">
      <label for="f-durum">Durum</label>
      <select id="f-durum">${secenek([["hepsi","Hepsi"], ...DURUMLAR], durumState.suzgec)}</select>
    </div>
    <div style="min-inline-size:190px">
      <label for="f-kat">Kategori</label>
      <select id="f-kat">${secenek([["hepsi","Hepsi"], ...KATLAR], durumState.kat)}</select>
    </div>
    <div style="min-inline-size:190px">
      <label for="f-sira">Siralama</label>
      <select id="f-sira">${secenek([["no-desc","En yeni ilan no"],["no-asc","En eski ilan no"],
        ["guncellendi-desc","Son degisen"],["baslik-asc","Baslik A-Z"],["fiyat-desc","Fiyat yuksekten"],
        ["fiyat-asc","Fiyat dusukten"]], durumState.siralama)}</select>
    </div>
  </div>

  <div class="kutu" style="overflow-x:auto">
    ${!data.length ? `<div class="bos">Bu suzgece uyan ilan yok.</div>` : `
    <table>
      <thead><tr>
        <th style="inline-size:70px">Gorsel</th><th>Baslik</th><th>Sanatci</th>
        <th>Olcu</th><th>Fiyat</th><th>Durum</th><th style="inline-size:90px"></th>
      </tr></thead>
      <tbody>${data.map(r => {
        const kapak = (r.kareler || []).slice().sort((a, b) => a.sira - b.sira)[0];
        return `<tr data-id="${r.id}" style="cursor:pointer">
          <td><img class="satir-kapak" loading="lazy" alt=""
               src="${kapak ? esc(gorselUrl(kapak.yol, 112)) : ""}"></td>
          <td>
            <b style="font-weight:500">${esc(r.baslik || "Adsiz ilan")}</b>
            <div style="font-size:.75rem;color:var(--pnl-ink-3)">${esc(r.slug)} · VO-${r.no}</div>
          </td>
          <td>${esc(r.sanatci || "-")}</td>
          <td class="sayisal">${r.olcu_w && r.olcu_h ? `${r.olcu_w} × ${r.olcu_h} in` : "-"}</td>
          <td class="sayisal">${r.fiyat ? esc(para(r.fiyat, r.para_birimi)) + (r.fiyat_gizli ? " <span style='color:var(--pnl-ink-3);font-size:.75rem'>(gizli)</span>" : "") : "<span style='color:var(--pnl-uyari)'>girilmedi</span>"}</td>
          <td>${durumRozet(r.durum)}</td>
          <td><button class="btn btn--line btn--kucuk" data-duzenle="${r.id}">Duzenle</button></td>
        </tr>`;
      }).join("")}</tbody>
    </table>`}
  </div>

  <div style="display:flex;gap:.5rem;align-items:center;justify-content:center;margin-block-start:1.25rem">
    <button class="btn btn--line btn--kucuk" id="onceki" ${durumState.sayfa <= 1 ? "disabled" : ""}>Onceki</button>
    <span class="sayisal" style="color:var(--pnl-ink-2)">${durumState.sayfa} / ${sayfaSayisi}</span>
    <button class="btn btn--line btn--kucuk" id="sonraki" ${durumState.sayfa >= sayfaSayisi ? "disabled" : ""}>Sonraki</button>
  </div>`;

  gvd.querySelectorAll("tbody tr").forEach(tr =>
    tr.addEventListener("click", () => { location.hash = "#/ilan/" + tr.dataset.id; }));
  document.getElementById("f-durum").addEventListener("change", e => {
    durumState.suzgec = e.target.value; durumState.sayfa = 1; ilanlarSayfasi(); });
  document.getElementById("f-kat").addEventListener("change", e => {
    durumState.kat = e.target.value; durumState.sayfa = 1; ilanlarSayfasi(); });
  document.getElementById("f-sira").addEventListener("change", e => {
    durumState.siralama = e.target.value; ilanlarSayfasi(); });
  document.getElementById("onceki").addEventListener("click", () => { durumState.sayfa--; ilanlarSayfasi(); });
  document.getElementById("sonraki").addEventListener("click", () => { durumState.sayfa++; ilanlarSayfasi(); });
  document.getElementById("yeni-ilan").addEventListener("click", yeniIlan);
}

async function yeniIlan() {
  if (!YETKI()) return bildir("Yetkin yok.", true);
  const { data: enB } = await sb.from("ilanlar").select("no").order("no", { ascending: false }).limit(1);
  const no = (enB?.[0]?.no || 0) + 1;
  const { data, error } = await sb.from("ilanlar")
    .insert({ no, slug: "ilan-" + no, baslik: "Yeni ilan", durum: "taslak" })
    .select("id").single();
  if (error) return bildir(error.message, true);
  location.hash = "#/ilan/" + data.id;
}

/* ------------------------------------------------------------ ilan duzenle */
const ROLLER = [["tam","Tam gorunum"],["aci","Acili"],["detay","Detay"],["imza","Imza"],
  ["sertifika","Sertifika"],["etiket","Etiket"],["plaka","Kunye plakasi"],["arka","Arka yuz"],["olcu","Olcu"]];

const FACET = {
  subject: [["landscape","Landscape"],["figurative","People"],["architecture","Architecture"],
    ["seascape","Water & Boats"],["still-life","Still Life"],["animal","Animals"],
    ["portrait","Portrait"],["abstract","Abstract"],["nude","Nude"],["document","Historical Documents"]],
  medium: [["oil","Oil Paint"],["watercolour","Watercolor"],["print","Prints & Works on Paper"],
    ["charcoal","Charcoal & Drawing"],["canvas","Canvas"],["paper","Paper"],
    ["panel","Wood Panel"],["textile","Textile & Needlework"],["ink","Ink"]],
  style: [["asian","Asian"],["modern","Modern"],["old-masters","Old Masters"],["contemporary","Contemporary"],
    ["impressionist","Impressionist"],["art-nouveau","Art Nouveau"],["folk","Folk & Naive"],["surrealist","Surrealist"]],
  framing: [["framed","Frame Included"],["unframed","Unframed"]],
  color: [["Gray","Gray"],["Brown","Brown"],["Black","Black"],["Beige","Beige"],["Blue","Blue"],
    ["Purple","Purple"],["Orange","Orange"],["Red","Red"],["Pink","Pink"],["Green","Green"],
    ["Gold","Gold"],["Yellow","Yellow"],["White","White"],["Silver","Silver"]],
};
const DONEMLER = [["","Secilmedi"],["18th-and-earlier","18th Century and Earlier"],
  ["19th","19th Century"],["20th","20th Century"],["21st","21st Century and Contemporary"]];

async function ilanSayfasi(id) {
  kabuk(`<div class="yukleniyor">Ilan yukleniyor</div>`, "ilanlar");
  const { data: il, error } = await sb.from("ilanlar").select("*").eq("id", id).single();
  if (error) { document.getElementById("icerik").innerHTML =
    `<p class="uyari-serit uyari-serit--hata">${esc(error.message)}</p>`; return; }
  const { data: kareler } = await sb.from("kareler").select("*").eq("ilan_id", id).order("sira");
  ilanCiz(il, kareler || []);
}

function alanKutu(ad, etiket, deger, tur = "text", ipucu = "") {
  const g = esc(deger ?? "");
  const govde = tur === "textarea"
    ? `<textarea id="a-${ad}" name="${ad}" rows="6">${g}</textarea>`
    : `<input id="a-${ad}" name="${ad}" type="${tur}" value="${g}"${tur === "number" ? ' step="any"' : ""}>`;
  return `<div class="alan"><label for="a-${ad}">${esc(etiket)}</label>${govde}
    ${ipucu ? `<p class="ipucu">${esc(ipucu)}</p>` : ""}</div>`;
}

function ilanCiz(il, kareler) {
  const gvd = document.getElementById("icerik");
  const facet = il.facet || {};
  const kutular = (grup, secili) => `<div class="etiketler">${FACET[grup].map(([v, ad]) =>
    `<label><input type="checkbox" data-facet="${grup}" value="${v}"
       ${(secili || []).includes(v) ? "checked" : ""}>${esc(ad)}</label>`).join("")}</div>`;

  gvd.innerHTML = `
  <div class="ustbilgi">
    <div>
      <h1>${esc(il.baslik || "Adsiz ilan")}</h1>
      <p>${esc(il.slug)} · VO-${il.no} · son degisiklik ${new Date(il.guncellendi).toLocaleString("tr-TR")}</p>
    </div>
    <div class="eylemler">
      <a class="btn btn--line btn--kucuk" href="#/ilanlar">Listeye don</a>
      <a class="btn btn--line btn--kucuk" target="_blank" rel="noopener"
         href="${esc(window.VO.SITE)}/item/${esc(il.slug)}.html">Sitede gor</a>
      <button class="btn btn--tehlike btn--kucuk" id="ilan-sil">Ilani sil</button>
      <button class="btn" id="kaydet">Kaydet</button>
    </div>
  </div>

  <div class="sekmeler" role="tablist">
    <button role="tab" aria-selected="true"  data-sekme="gorsel">Gorseller</button>
    <button role="tab" aria-selected="false" data-sekme="icerik">Icerik</button>
    <button role="tab" aria-selected="false" data-sekme="fiyat">Fiyat ve durum</button>
    <button role="tab" aria-selected="false" data-sekme="siniflandirma">Siniflandirma</button>
    <button role="tab" aria-selected="false" data-sekme="seo">SEO</button>
  </div>

  <form id="ilan-form">
  <section data-panel="gorsel">
    <p style="color:var(--pnl-ink-2);margin-block-end:1rem">
      Listedeki ilk gorsel kapaktir. Suruklerek sirayi degistirebilirsin.</p>
    <div class="kareler" id="kare-liste"></div>
    <div class="birak" id="birak-alani" style="margin-block-start:1rem">
      <p>Fotograflari buraya surukle ya da
        <label style="display:inline;text-decoration:underline;cursor:pointer;color:var(--pnl-ink)">
          bilgisayardan sec<input type="file" id="dosya-sec" accept="image/*" multiple hidden></label></p>
      <p class="ipucu" style="margin-block-start:.4rem">JPG, PNG, HEIC ya da WEBP. Tek dosya en fazla 50 MB.</p>
    </div>
    <div id="yukleme-durum" style="margin-block-start:.75rem"></div>
  </section>

  <section data-panel="icerik" hidden>
    ${alanKutu("baslik", "Ilan basligi", il.baslik, "text", "Sitede ve arama sonucunda gorunen ad.")}
    ${alanKutu("aciklama", "Aciklama", il.aciklama, "textarea", "Alicinin okudugu metin. Em cizgi kullanma.")}
    <div class="ikili">
      ${alanKutu("sanatci", "Sanatci", il.sanatci)}
      ${alanKutu("eser_adi", "Eserin adi", il.eser_adi)}
    </div>
    <div class="uclu">
      ${alanKutu("donem", "Donem", il.donem, "text", "Ornek: 20th century")}
      ${alanKutu("teknik", "Teknik", il.teknik, "text", "Ornek: oil on canvas")}
      ${alanKutu("baski", "Baski / edisyon", il.baski)}
    </div>
    <div class="uclu">
      ${alanKutu("galeri_adi", "Galeri", il.galeri_adi)}
      ${alanKutu("ref", "Referans no", il.ref)}
      ${alanKutu("kaynak_dosya", "Kaynak dosya", il.kaynak_dosya)}
    </div>
    ${alanKutu("etiket", "Arka etiket metni", il.etiket, "textarea")}
    ${alanKutu("belge", "Sertifika notu", il.belge, "textarea")}
    ${alanKutu("biyografi", "Sanatci biyografisi", il.biyografi, "textarea")}
    ${alanKutu("aciklama_not", "Ic not (sitede gorunmez)", il.aciklama_not, "textarea")}
  </section>

  <section data-panel="fiyat" hidden>
    <div class="uclu">
      ${alanKutu("fiyat", "Fiyat", il.fiyat, "number", "Bos birakirsan sitede Price Upon Request yazar.")}
      ${alanKutu("fiyat_eski", "Eski fiyat", il.fiyat_eski, "number", "Doldurursan sitede indirim gorunur.")}
      <div class="alan">
        <label for="a-para_birimi">Para birimi</label>
        <select id="a-para_birimi" name="para_birimi">
          ${["USD","EUR","GBP","TRY"].map(p => `<option ${il.para_birimi === p ? "selected" : ""}>${p}</option>`).join("")}
        </select>
      </div>
    </div>
    <div class="ikili">
      <div class="alan">
        <label for="a-durum">Durum</label>
        <select id="a-durum" name="durum">${DURUMLAR.map(([v, ad]) =>
          `<option value="${v}" ${il.durum === v ? "selected" : ""}>${esc(ad)}</option>`).join("")}</select>
        <p class="ipucu">Yalnizca "Yayinda" olan ilanlar sitede gorunur.</p>
      </div>
      <div class="alan">
        <label for="a-kat">Kategori</label>
        <select id="a-kat" name="kat">${KATLAR.map(([v, ad]) =>
          `<option value="${v}" ${il.kat === v ? "selected" : ""}>${esc(ad)}</option>`).join("")}</select>
      </div>
    </div>
    <div class="uclu">
      ${alanKutu("olcu_w", "Genislik (inc)", il.olcu_w, "number")}
      ${alanKutu("olcu_h", "Yukseklik (inc)", il.olcu_h, "number")}
      ${alanKutu("olcu_d", "Derinlik (inc)", il.olcu_d, "number")}
    </div>
    ${alanKutu("olcu_nesi", "Olcu neyin", il.olcu_nesi, "text", "Ornek: outside of frame, sheet, canvas")}
    <div class="etiketler" style="margin-block-start:.5rem">
      <label><input type="checkbox" id="a-fiyat_gizli" ${il.fiyat_gizli ? "checked" : ""}>Fiyati sitede gizle</label>
      <label><input type="checkbox" id="a-pazarlik" ${il.pazarlik ? "checked" : ""}>Teklife acik</label>
      <label><input type="checkbox" id="a-one_cikan" ${il.one_cikan ? "checked" : ""}>Ana sayfada one cikar</label>
    </div>
  </section>

  <section data-panel="siniflandirma" hidden>
    <p style="color:var(--pnl-ink-2);margin-block-end:1.25rem">
      Bunlar sitedeki suzgecleri besler. Alici soldaki filtrelerden bunlarla arar.</p>
    <div class="alan"><label>Konu</label>${kutular("subject", facet.subject)}</div>
    <div class="alan"><label>Teknik</label>${kutular("medium", facet.medium)}</div>
    <div class="alan"><label>Uslup</label>${kutular("style", facet.style)}</div>
    <div class="alan"><label>Cerceve</label>${kutular("framing", facet.framing)}</div>
    <div class="alan"><label>Renk</label>${kutular("color", facet.color)}</div>
    <div class="alan" style="max-inline-size:340px">
      <label for="a-period">Yuzyil</label>
      <select id="a-period">${DONEMLER.map(([v, ad]) =>
        `<option value="${v}" ${(facet.period || "") === v ? "selected" : ""}>${esc(ad)}</option>`).join("")}</select>
    </div>
  </section>

  <section data-panel="seo" hidden>
    ${alanKutu("slug", "Adres (slug)", il.slug, "text", "Degistirirsen eski adres kirilir. Zorunlu olmadikca dokunma.")}
    ${alanKutu("seo_baslik", "Arama basligi", il.seo_baslik, "text", "Bos birakirsan ilan basligi kullanilir. 60 karakteri gecmesin.")}
    ${alanKutu("seo_aciklama", "Arama aciklamasi", il.seo_aciklama, "textarea", "155 karakteri gecmesin.")}
    <div class="kutu" style="padding:1rem;max-inline-size:640px">
      <p style="font-size:.75rem;letter-spacing:.1em;text-transform:uppercase;color:var(--pnl-ink-3)">Google onizleme</p>
      <p id="onizleme-baslik" style="color:#1a0dab;font-size:1.15rem;margin-block-start:.4rem"></p>
      <p style="color:var(--pnl-ok);font-size:.8125rem">${esc(window.VO.SITE)}/item/${esc(il.slug)}.html</p>
      <p id="onizleme-aciklama" style="color:var(--pnl-ink-2);font-size:.875rem;margin-block-start:.25rem"></p>
    </div>
  </section>
  </form>`;

  /* sekmeler */
  gvd.querySelectorAll("[data-sekme]").forEach(b => b.addEventListener("click", () => {
    gvd.querySelectorAll("[data-sekme]").forEach(x => x.setAttribute("aria-selected", x === b));
    gvd.querySelectorAll("[data-panel]").forEach(s => s.hidden = s.dataset.panel !== b.dataset.sekme);
  }));

  const onizle = () => {
    const b = gvd.querySelector("#a-seo_baslik").value || gvd.querySelector("#a-baslik").value;
    const a = gvd.querySelector("#a-seo_aciklama").value || (il.aciklama || "").slice(0, 155);
    gvd.querySelector("#onizleme-baslik").textContent = b;
    gvd.querySelector("#onizleme-aciklama").textContent = a;
  };
  ["#a-seo_baslik", "#a-seo_aciklama", "#a-baslik"].forEach(s =>
    gvd.querySelector(s).addEventListener("input", onizle));
  onizle();

  kareleriCiz(il, kareler);
  yuklemeKur(il, kareler);

  document.getElementById("kaydet").addEventListener("click", () => ilanKaydet(il, kareler));
  document.getElementById("ilan-sil").addEventListener("click", async () => {
    if (!await sor("Bu ilan silinsin mi?")) return;
    const { error } = await sb.from("ilanlar").delete().eq("id", il.id);
    if (error) return bildir(error.message, true);
    bildir("Ilan silindi."); location.hash = "#/ilanlar";
  });
}

/* -------------------------------------------------------- kare listesi ve surukleme */
function kareleriCiz(il, kareler) {
  const kap = document.getElementById("kare-liste");
  if (!kareler.length) {
    kap.innerHTML = `<p style="color:var(--pnl-ink-2)">Bu ilanda henuz gorsel yok.</p>`;
    return;
  }
  kap.innerHTML = kareler.map((k, i) => `
    <figure class="kare" draggable="true" data-kid="${k.id}" data-i="${i}" style="margin:0">
      ${i === 0 ? `<span class="kapak-rozet">Kapak</span>` : ""}
      <button type="button" class="sil" data-sil="${k.id}" aria-label="Bu gorseli kaldir">×</button>
      <span class="tut" aria-hidden="true">surukle</span>
      <img loading="lazy" alt="${esc(k.alt_metin || "")}" src="${esc(gorselUrl(k.yol, 400))}">
      <div class="alt-bar">
        <select data-rol="${k.id}" aria-label="Gorselin rolu">
          ${ROLLER.map(([v, ad]) => `<option value="${v}" ${k.rol === v ? "selected" : ""}>${esc(ad)}</option>`).join("")}
        </select>
        <input type="text" data-alt="${k.id}" value="${esc(k.alt_metin || "")}"
               placeholder="Gorsel aciklamasi" style="min-block-size:36px;font-size:.8125rem">
      </div>
    </figure>`).join("");

  let suruklenen = null;
  kap.querySelectorAll(".kare").forEach(el => {
    el.addEventListener("dragstart", e => {
      suruklenen = el; el.classList.add("suruklenen");
      e.dataTransfer.effectAllowed = "move";
    });
    el.addEventListener("dragend", () => { el.classList.remove("suruklenen"); suruklenen = null;
      kap.querySelectorAll(".kare").forEach(x => x.classList.remove("hedef")); });
    el.addEventListener("dragover", e => { e.preventDefault(); if (el !== suruklenen) el.classList.add("hedef"); });
    el.addEventListener("dragleave", () => el.classList.remove("hedef"));
    el.addEventListener("drop", async e => {
      e.preventDefault(); el.classList.remove("hedef");
      if (!suruklenen || suruklenen === el) return;
      const a = Number(suruklenen.dataset.i), b = Number(el.dataset.i);
      const yeni = kareler.slice();
      yeni.splice(b, 0, yeni.splice(a, 1)[0]);
      await siraKaydet(yeni);
      kareler.length = 0; kareler.push(...yeni);
      kareleriCiz(il, kareler);
    });
  });

  kap.querySelectorAll("[data-sil]").forEach(b => b.addEventListener("click", async e => {
    e.stopPropagation();
    if (!await sor("Bu gorsel ilandan kaldirilsin mi?", "Kaldir")) return;
    const kid = Number(b.dataset.sil);
    const k = kareler.find(x => x.id === kid);
    const { error } = await sb.from("kareler").delete().eq("id", kid);
    if (error) return bildir(error.message, true);
    if (k) await sb.storage.from("gorseller").remove([k.yol]);
    const i = kareler.findIndex(x => x.id === kid);
    kareler.splice(i, 1);
    await siraKaydet(kareler);
    kareleriCiz(il, kareler);
    bildir("Gorsel kaldirildi.");
  }));

  kap.querySelectorAll("[data-rol]").forEach(s => s.addEventListener("change", async () => {
    const { error } = await sb.from("kareler").update({ rol: s.value }).eq("id", Number(s.dataset.rol));
    bildir(error ? error.message : "Rol guncellendi.", !!error);
  }));
  kap.querySelectorAll("[data-alt]").forEach(inp => inp.addEventListener("change", async () => {
    const { error } = await sb.from("kareler").update({ alt_metin: inp.value }).eq("id", Number(inp.dataset.alt));
    if (error) bildir(error.message, true);
  }));
}

async function siraKaydet(kareler) {
  for (let i = 0; i < kareler.length; i++) {
    kareler[i].sira = i + 1;
    await sb.from("kareler").update({ sira: i + 1 }).eq("id", kareler[i].id);
  }
}

/* ---------------------------------------------------------------- yukleme */
function yuklemeKur(il, kareler) {
  const alan = document.getElementById("birak-alani");
  const secici = document.getElementById("dosya-sec");
  const durum = document.getElementById("yukleme-durum");

  ["dragenter", "dragover"].forEach(e =>
    alan.addEventListener(e, ev => { ev.preventDefault(); alan.classList.add("uzerinde"); }));
  ["dragleave", "drop"].forEach(e =>
    alan.addEventListener(e, ev => { ev.preventDefault(); alan.classList.remove("uzerinde"); }));
  alan.addEventListener("drop", ev => yukle([...ev.dataTransfer.files]));
  secici.addEventListener("change", () => { yukle([...secici.files]); secici.value = ""; });

  async function yukle(dosyalar) {
    const resimler = dosyalar.filter(f => /^image\//.test(f.type) || /\.(hei[cf]|jpe?g|png|webp|tiff?)$/i.test(f.name));
    if (!resimler.length) return bildir("Gorsel dosyasi bulunamadi.", true);
    let sayac = 0;
    for (const dosya of resimler) {
      sayac++;
      durum.innerHTML = `<p class="ipucu">${sayac} / ${resimler.length} yukleniyor: ${esc(dosya.name)}</p>`;
      const uzanti = (dosya.name.split(".").pop() || "jpg").toLowerCase();
      const yol = `${il.slug}/${Date.now()}-${Math.random().toString(36).slice(2, 8)}.${uzanti}`;
      const { error: yErr } = await sb.storage.from("gorseller")
        .upload(yol, dosya, { cacheControl: "31536000", upsert: false });
      if (yErr) { bildir(`${dosya.name}: ${yErr.message}`, true); continue; }

      const olcu = await olcuOku(dosya);
      const { data, error } = await sb.from("kareler").insert({
        ilan_id: il.id, sira: kareler.length + 1,
        rol: kareler.length === 0 ? "tam" : "detay",
        yol, w: olcu.w, h: olcu.h, kaynak: "orijinal"
      }).select().single();
      if (error) { bildir(error.message, true); continue; }
      kareler.push(data);
    }
    durum.innerHTML = "";
    kareleriCiz(il, kareler);
    bildir(`${sayac} gorsel eklendi.`);
  }
}

function olcuOku(dosya) {
  return new Promise(cevapla => {
    const url = URL.createObjectURL(dosya);
    const im = new Image();
    im.onload = () => { cevapla({ w: im.naturalWidth, h: im.naturalHeight }); URL.revokeObjectURL(url); };
    im.onerror = () => { cevapla({ w: null, h: null }); URL.revokeObjectURL(url); };
    im.src = url;
  });
}

/* --------------------------------------------------------------- kaydetme */
async function ilanKaydet(il) {
  const f = document.getElementById("ilan-form");
  const al = ad => f.querySelector("#a-" + ad);
  const say = ad => { const v = al(ad).value.trim(); return v === "" ? null : Number(v); };

  const facet = { subject: [], medium: [], style: [], framing: [], color: [], period: al("period").value };
  f.querySelectorAll("[data-facet]:checked").forEach(c => facet[c.dataset.facet].push(c.value));

  const yeni = {
    baslik: al("baslik").value.trim(),
    aciklama: al("aciklama").value.trim(),
    sanatci: al("sanatci").value.trim(),
    eser_adi: al("eser_adi").value.trim(),
    donem: al("donem").value.trim(),
    teknik: al("teknik").value.trim(),
    baski: al("baski").value.trim(),
    galeri_adi: al("galeri_adi").value.trim(),
    ref: al("ref").value.trim(),
    kaynak_dosya: al("kaynak_dosya").value.trim(),
    etiket: al("etiket").value.trim(),
    belge: al("belge").value.trim(),
    biyografi: al("biyografi").value.trim(),
    aciklama_not: al("aciklama_not").value.trim(),
    fiyat: say("fiyat"), fiyat_eski: say("fiyat_eski"),
    para_birimi: al("para_birimi").value,
    durum: al("durum").value, kat: al("kat").value,
    olcu_w: say("olcu_w"), olcu_h: say("olcu_h"), olcu_d: say("olcu_d"),
    olcu_nesi: al("olcu_nesi").value.trim(),
    fiyat_gizli: al("fiyat_gizli").checked,
    pazarlik: al("pazarlik").checked,
    one_cikan: al("one_cikan").checked,
    slug: al("slug").value.trim(),
    seo_baslik: al("seo_baslik").value.trim(),
    seo_aciklama: al("seo_aciklama").value.trim(),
    facet,
  };

  const tire = Object.values(yeni).filter(v => typeof v === "string" && /[–—]/.test(v));
  if (tire.length) return bildir("Metinlerde uzun tire var. Sitenin kurali geregi yalnizca kisa tire kullanilir.", true);
  if (!yeni.baslik) return bildir("Baslik bos birakilamaz.", true);
  if (!/^[a-z0-9-]+$/.test(yeni.slug)) return bildir("Adres yalnizca kucuk harf, rakam ve tire icerebilir.", true);

  const btn = document.getElementById("kaydet");
  btn.disabled = true; btn.textContent = "Kaydediliyor";
  const { error } = await sb.from("ilanlar").update(yeni).eq("id", il.id);
  btn.disabled = false; btn.textContent = "Kaydet";
  if (error) return bildir(error.message, true);
  bildir("Kaydedildi. Sitede gorunmesi icin Yayinla.");
  Object.assign(il, yeni);
}

/* --------------------------------------------------------------- fiyatlar */
async function fiyatSayfasi() {
  kabuk(`<div class="yukleniyor">Yukleniyor</div>`, "fiyatlar");
  const { data, error } = await sb.from("ilanlar")
    .select("id,no,slug,baslik,sanatci,fiyat,fiyat_eski,para_birimi,fiyat_gizli,durum")
    .order("no");
  const gvd = document.getElementById("icerik");
  if (error) return gvd.innerHTML = `<p class="uyari-serit uyari-serit--hata">${esc(error.message)}</p>`;

  const eksik = data.filter(d => d.fiyat == null).length;
  gvd.innerHTML = `
  <div class="ustbilgi">
    <div><h1>Fiyatlar</h1>
      <p>Butun ilanlarin fiyatini tek ekrandan girebilirsin. Bir alani doldurup baska yere tikladiginda kaydedilir.</p></div>
  </div>
  <div class="ozet">
    <div><b>${data.length}</b><span>Ilan</span></div>
    <div><b>${data.length - eksik}</b><span>Fiyati girilmis</span></div>
    <div><b>${eksik}</b><span>Fiyat bekleyen</span></div>
  </div>
  <div class="kutu" style="overflow-x:auto">
    <table><thead><tr>
      <th>No</th><th>Baslik</th><th>Sanatci</th><th style="inline-size:140px">Fiyat</th>
      <th style="inline-size:140px">Eski fiyat</th><th style="inline-size:90px">Birim</th>
      <th style="inline-size:80px">Gizli</th><th>Durum</th>
    </tr></thead><tbody>
    ${data.map(d => `<tr>
      <td class="sayisal">${d.no}</td>
      <td><a href="#/ilan/${d.id}" style="text-decoration:none"><b style="font-weight:500">${esc(d.baslik)}</b></a></td>
      <td>${esc(d.sanatci || "-")}</td>
      <td><input type="number" step="any" class="sayisal" data-f="fiyat" data-id="${d.id}"
           value="${d.fiyat ?? ""}" style="min-block-size:38px"></td>
      <td><input type="number" step="any" class="sayisal" data-f="fiyat_eski" data-id="${d.id}"
           value="${d.fiyat_eski ?? ""}" style="min-block-size:38px"></td>
      <td><select data-f="para_birimi" data-id="${d.id}" style="min-block-size:38px">
        ${["USD","EUR","GBP","TRY"].map(p => `<option ${d.para_birimi === p ? "selected" : ""}>${p}</option>`).join("")}
      </select></td>
      <td style="text-align:center"><input type="checkbox" data-f="fiyat_gizli" data-id="${d.id}"
           ${d.fiyat_gizli ? "checked" : ""} aria-label="Fiyati gizle"></td>
      <td>${durumRozet(d.durum)}</td>
    </tr>`).join("")}
    </tbody></table>
  </div>`;

  gvd.querySelectorAll("[data-f]").forEach(el => el.addEventListener("change", async () => {
    const alan = el.dataset.f;
    let deger = el.type === "checkbox" ? el.checked
              : el.type === "number" ? (el.value.trim() === "" ? null : Number(el.value))
              : el.value;
    const { error } = await sb.from("ilanlar").update({ [alan]: deger }).eq("id", Number(el.dataset.id));
    if (error) return bildir(error.message, true);
    el.style.outline = "2px solid var(--pnl-ok)";
    setTimeout(() => { el.style.outline = ""; }, 900);
  }));
}

/* --------------------------------------------------------------- sayfalar */
async function sayfalarSayfasi() {
  kabuk(`<div class="yukleniyor">Yukleniyor</div>`, "sayfalar");
  const { data, error } = await sb.from("sayfalar").select("*").order("anahtar");
  const gvd = document.getElementById("icerik");
  if (error) return gvd.innerHTML = `<p class="uyari-serit uyari-serit--hata">${esc(error.message)}</p>`;

  gvd.innerHTML = `
  <div class="ustbilgi"><div><h1>Site metinleri</h1>
    <p>Ana sayfa, hakkinda, kargo, iade gibi sabit sayfalarin metni. Ilan aciklamalari burada degil, ilanin kendi sayfasinda.</p></div></div>
  ${data.map(s => `
    <details class="kutu" style="margin-block-end:.75rem">
      <summary style="padding:1rem;cursor:pointer;display:flex;justify-content:space-between;gap:1rem">
        <b style="font-weight:500">${esc(s.baslik || s.anahtar)}</b>
        <span style="color:var(--pnl-ink-3);font-size:.8125rem">${esc(s.anahtar)}</span>
      </summary>
      <div style="padding:0 1rem 1rem">
        <div class="alan"><label for="s-b-${s.anahtar}">Baslik</label>
          <input id="s-b-${s.anahtar}" value="${esc(s.baslik)}"></div>
        <div class="alan"><label for="s-i-${s.anahtar}">Metin</label>
          <textarea id="s-i-${s.anahtar}" rows="10">${esc(s.icerik)}</textarea></div>
        <div class="ikili">
          <div class="alan"><label for="s-sb-${s.anahtar}">Arama basligi</label>
            <input id="s-sb-${s.anahtar}" value="${esc(s.seo_baslik || "")}"></div>
          <div class="alan"><label for="s-sa-${s.anahtar}">Arama aciklamasi</label>
            <input id="s-sa-${s.anahtar}" value="${esc(s.seo_aciklama || "")}"></div>
        </div>
        <button class="btn btn--kucuk" data-sayfa="${s.anahtar}">Kaydet</button>
      </div>
    </details>`).join("")}`;

  gvd.querySelectorAll("[data-sayfa]").forEach(b => b.addEventListener("click", async () => {
    const a = b.dataset.sayfa;
    const { error } = await sb.from("sayfalar").update({
      baslik: document.getElementById("s-b-" + a).value,
      icerik: document.getElementById("s-i-" + a).value,
      seo_baslik: document.getElementById("s-sb-" + a).value,
      seo_aciklama: document.getElementById("s-sa-" + a).value,
      guncellendi: new Date().toISOString()
    }).eq("anahtar", a);
    bildir(error ? error.message : "Sayfa kaydedildi.", !!error);
  }));
}

/* ------------------------------------------------------------- sanatcilar */
async function sanatcilarSayfasi() {
  kabuk(`<div class="yukleniyor">Yukleniyor</div>`, "sanatcilar");
  const { data } = await sb.from("sanatcilar").select("*").order("ad");
  const gvd = document.getElementById("icerik");
  gvd.innerHTML = `
  <div class="ustbilgi"><div><h1>Sanatcilar</h1>
    <p>Buraya girilen biyografi, o sanatcinin butun ilanlarinda gorunur.</p></div>
    <div class="eylemler"><button class="btn" id="yeni-sanatci">Yeni sanatci</button></div></div>
  <div class="kutu" style="overflow-x:auto">
    ${!data?.length ? `<div class="bos">Henuz sanatci kaydi yok.</div>` : `
    <table><thead><tr><th>Ad</th><th>Dogum</th><th>Olum</th><th>Ulke</th><th>Biyografi</th><th></th></tr></thead>
    <tbody>${data.map(s => `<tr>
      <td><input value="${esc(s.ad)}" data-s="ad" data-id="${s.id}"></td>
      <td><input value="${esc(s.dogum || "")}" data-s="dogum" data-id="${s.id}" style="inline-size:90px"></td>
      <td><input value="${esc(s.olum || "")}" data-s="olum" data-id="${s.id}" style="inline-size:90px"></td>
      <td><input value="${esc(s.ulke || "")}" data-s="ulke" data-id="${s.id}" style="inline-size:120px"></td>
      <td><textarea data-s="biyografi" data-id="${s.id}" rows="2" style="min-block-size:44px">${esc(s.biyografi || "")}</textarea></td>
      <td><button class="btn btn--tehlike btn--kucuk" data-sil-s="${s.id}">Sil</button></td>
    </tr>`).join("")}</tbody></table>`}
  </div>`;

  gvd.querySelectorAll("[data-s]").forEach(el => el.addEventListener("change", async () => {
    const { error } = await sb.from("sanatcilar")
      .update({ [el.dataset.s]: el.value }).eq("id", Number(el.dataset.id));
    if (error) bildir(error.message, true);
  }));
  gvd.querySelectorAll("[data-sil-s]").forEach(b => b.addEventListener("click", async () => {
    if (!await sor("Sanatci kaydi silinsin mi?")) return;
    await sb.from("sanatcilar").delete().eq("id", Number(b.dataset.silS));
    sanatcilarSayfasi();
  }));
  document.getElementById("yeni-sanatci").addEventListener("click", async () => {
    const { error } = await sb.from("sanatcilar").insert({ ad: "Yeni sanatci " + Date.now() % 10000 });
    if (error) return bildir(error.message, true);
    sanatcilarSayfasi();
  });
}

/* ---------------------------------------------------------------- ayarlar */
async function ayarlarSayfasi() {
  kabuk(`<div class="yukleniyor">Yukleniyor</div>`, "ayarlar");
  const { data } = await sb.from("ayarlar").select("*").order("anahtar");
  const gvd = document.getElementById("icerik");
  gvd.innerHTML = `
  <div class="ustbilgi"><div><h1>Ayarlar</h1>
    <p>Marka adi, iletisim, konum ve fiyat politikasi. Degistirdikten sonra Yayinla demen gerekir.</p></div></div>
  ${(data || []).map(a => `
    <div class="kutu" style="padding:1.25rem;margin-block-end:.75rem">
      <h3 style="text-transform:capitalize">${esc(a.anahtar.replace(/_/g, " "))}</h3>
      <p class="ipucu" style="margin-block-end:.75rem">${esc(a.aciklama || "")}</p>
      ${Object.entries(a.deger).map(([k, v]) => `
        <div class="alan" style="max-inline-size:480px">
          <label for="ay-${a.anahtar}-${k}" style="text-transform:capitalize">${esc(k.replace(/_/g, " "))}</label>
          ${typeof v === "boolean"
            ? `<label class="etiketler" style="margin:0"><input type="checkbox" id="ay-${a.anahtar}-${k}" ${v ? "checked" : ""}> Acik</label>`
            : `<input id="ay-${a.anahtar}-${k}" value="${esc(v)}">`}
        </div>`).join("")}
      <button class="btn btn--kucuk" data-ayar="${a.anahtar}">Kaydet</button>
    </div>`).join("")}`;

  gvd.querySelectorAll("[data-ayar]").forEach(b => b.addEventListener("click", async () => {
    const a = (data || []).find(x => x.anahtar === b.dataset.ayar);
    const yeni = {};
    for (const [k, v] of Object.entries(a.deger)) {
      const el = document.getElementById(`ay-${a.anahtar}-${k}`);
      yeni[k] = typeof v === "boolean" ? el.checked : el.value;
    }
    const { error } = await sb.from("ayarlar")
      .update({ deger: yeni, guncellendi: new Date().toISOString() }).eq("anahtar", a.anahtar);
    bildir(error ? error.message : "Ayar kaydedildi.", !!error);
  }));
}

/* ------------------------------------------------------------ kullanicilar */
async function kullanicilarSayfasi() {
  if (!SAHIP()) { location.hash = "#/ilanlar"; return; }
  kabuk(`<div class="yukleniyor">Yukleniyor</div>`, "kullanicilar");
  const { data } = await sb.from("profiller").select("*").order("olusturuldu");
  const gvd = document.getElementById("icerik");
  gvd.innerHTML = `
  <div class="ustbilgi"><div><h1>Kullanicilar</h1>
    <p>Yeni kullanici davet etmek icin Supabase panelinden Authentication > Users > Invite user.
       Kullanici ilk girisinde burada belirir; rolunu buradan degistirirsin.</p></div></div>
  <div class="kutu" style="overflow-x:auto">
    <table><thead><tr><th>E-posta</th><th>Ad</th><th>Rol</th><th>Son giris</th><th></th></tr></thead>
    <tbody>${(data || []).map(p => `<tr>
      <td>${esc(p.eposta)}</td>
      <td><input value="${esc(p.ad || "")}" data-p="ad" data-id="${p.id}"></td>
      <td><select data-p="rol" data-id="${p.id}" ${p.id === oturum.user.id ? "disabled" : ""}>
        ${[["sahip","Sahip - her sey ve kullanici yonetimi"],
           ["yonetici","Yonetici - butun icerik"],
           ["okur","Okur - sadece bakar"]].map(([v, ad]) =>
          `<option value="${v}" ${p.rol === v ? "selected" : ""}>${esc(ad)}</option>`).join("")}
      </select></td>
      <td style="color:var(--pnl-ink-3);font-size:.8125rem">${p.son_giris ? new Date(p.son_giris).toLocaleString("tr-TR") : "-"}</td>
      <td>${p.id === oturum.user.id ? "" :
        `<button class="btn btn--tehlike btn--kucuk" data-sil-p="${p.id}">Kaldir</button>`}</td>
    </tr>`).join("")}</tbody></table>
  </div>`;

  gvd.querySelectorAll("[data-p]").forEach(el => el.addEventListener("change", async () => {
    const { error } = await sb.from("profiller").update({ [el.dataset.p]: el.value }).eq("id", el.dataset.id);
    bildir(error ? error.message : "Guncellendi.", !!error);
  }));
  gvd.querySelectorAll("[data-sil-p]").forEach(b => b.addEventListener("click", async () => {
    if (!await sor("Bu kullanicinin panele erisimi kaldirilsin mi?", "Kaldir")) return;
    const { error } = await sb.from("profiller").delete().eq("id", b.dataset.silP);
    if (error) return bildir(error.message, true);
    bildir("Erisim kaldirildi. Hesabi tamamen silmek icin Supabase > Authentication.");
    kullanicilarSayfasi();
  }));
}

/* ----------------------------------------------------------------- gecmis */
async function gecmisSayfasi() {
  kabuk(`<div class="yukleniyor">Yukleniyor</div>`, "gecmis");
  const [{ data: log }, { data: yayin }] = await Promise.all([
    sb.from("degisiklik_log").select("*").order("ne_zaman", { ascending: false }).limit(120),
    sb.from("yayin_istek").select("*").order("istendi", { ascending: false }).limit(15),
  ]);
  const gvd = document.getElementById("icerik");
  const ISLEM = { INSERT: "eklendi", UPDATE: "degistirildi", DELETE: "silindi" };
  gvd.innerHTML = `
  <div class="ustbilgi"><div><h1>Gecmis</h1>
    <p>Kim neyi ne zaman degistirdi ve yayin istekleri.</p></div></div>

  <h2 style="margin-block-end:.75rem">Yayin istekleri</h2>
  <div class="kutu" style="overflow-x:auto;margin-block-end:2rem">
    ${!yayin?.length ? `<div class="bos">Henuz yayin istegi yok.</div>` : `
    <table><thead><tr><th>Istendi</th><th>Durum</th><th>Bitti</th><th>Mesaj</th></tr></thead>
    <tbody>${yayin.map(y => `<tr>
      <td>${new Date(y.istendi).toLocaleString("tr-TR")}</td>
      <td>${esc(y.durum)}</td>
      <td>${y.bitti ? new Date(y.bitti).toLocaleString("tr-TR") : "-"}</td>
      <td style="font-size:.8125rem;color:var(--pnl-ink-2)">${esc(y.kayit || y.mesaj || "")}</td>
    </tr>`).join("")}</tbody></table>`}
  </div>

  <h2 style="margin-block-end:.75rem">Degisiklikler</h2>
  <div class="kutu" style="overflow-x:auto">
    ${!log?.length ? `<div class="bos">Kayit yok.</div>` : `
    <table><thead><tr><th>Zaman</th><th>Tablo</th><th>Kayit</th><th>Islem</th></tr></thead>
    <tbody>${log.map(l => `<tr>
      <td>${new Date(l.ne_zaman).toLocaleString("tr-TR")}</td>
      <td>${esc(l.tablo)}</td>
      <td>${esc(l.kayit_id)}</td>
      <td>${esc(ISLEM[l.islem] || l.islem)}</td>
    </tr>`).join("")}</tbody></table>`}
  </div>`;
}

/* ------------------------------------------------------------------ yonlendirme */
function yonlendir() {
  const h = location.hash || "#/ilanlar";
  const ilan = h.match(/^#\/ilan\/(\d+)/);
  if (ilan) return ilanSayfasi(Number(ilan[1]));
  if (h.startsWith("#/fiyatlar")) return fiyatSayfasi();
  if (h.startsWith("#/kampanyalar")) return kampanyaSayfasi();
  if (h.startsWith("#/sayfalar")) return sayfalarSayfasi();
  if (h.startsWith("#/sanatcilar")) return sanatcilarSayfasi();
  if (h.startsWith("#/ayarlar")) return ayarlarSayfasi();
  if (h.startsWith("#/kullanicilar")) return kullanicilarSayfasi();
  if (h.startsWith("#/gecmis")) return gecmisSayfasi();
  return ilanlarSayfasi();
}

window.addEventListener("hashchange", yonlendir);

/* --------------------------------------------------------------- baslangic */
async function baslat() {
  if (ONIZLEME) {
    const { data: o } = await sb.auth.getSession();
    if (!o.session) return girisEkrani();
    profil = { id: "onizleme", ad: "Onizleme", rol: "sahip", eposta: "onizleme" };
    oturum = { user: { id: "onizleme" } };
    yonlendir();
    setTimeout(() => bildir("Onizleme modu: gercek 270 ilan gorunuyor, degisiklikler kaydedilmez.", false), 400);
    return;
  }
  if (!window.VO || window.VO.URL.startsWith("BURAYA")) {
    kok.innerHTML = `<div class="giris"><div class="kutu" style="padding:2rem;max-inline-size:520px">
      <h2>Panel henuz baglanmadi</h2>
      <p style="color:var(--pnl-ink-2);margin-block-start:.75rem">
        <code>admin/config.js</code> dosyasindaki iki degeri Supabase projesinden alip yapistir,
        sonra bu sayfayi yenile. Adim adim anlatim <code>KURULUM.md</code> icinde.</p>
    </div></div>`;
    return;
  }
  const { data } = await sb.auth.getSession();
  oturum = data.session;
  if (!oturum) return girisEkrani();

  const { data: p, error } = await sb.from("profiller").select("*").eq("id", oturum.user.id).single();
  if (error || !p) {
    await sb.auth.signOut();
    return girisEkrani("Bu hesabin panele erisimi yok. Yoneticiden yetki iste.");
  }
  profil = p;
  sb.from("profiller").update({ son_giris: new Date().toISOString() }).eq("id", p.id).then(() => {});
  yonlendir();
}

sb.auth.onAuthStateChange((olay) => {
  if (olay === "SIGNED_OUT") { oturum = null; profil = null; girisEkrani(); }
});

baslat();

/* ------------------------------------------------------------- kampanyalar */
const KAPSAM = [["hepsi","Butun koleksiyon"],["kategori","Secili kategoriler"],
                ["sanatci","Secili sanatcilar"],["secili","Secili ilanlar"]];

function tarihAlan(d) { return d ? String(d).slice(0, 16) : ""; }

async function kampanyaSayfasi() {
  kabuk(`<div class="yukleniyor">Yukleniyor</div>`, "kampanyalar");
  const gvd = document.getElementById("icerik");
  const [{ data, error }, { data: ilan }] = await Promise.all([
    sb.from("kampanyalar").select("*").order("oncelik", { ascending: false }),
    sb.from("ilanlar").select("kat,sanatci,fiyat,fiyat_gizli,durum"),
  ]);
  if (error) return gvd.innerHTML = `<p class="uyari-serit uyari-serit--hata">${esc(error.message)}
    Kampanya tablosu yoksa <code>supabase/04_kampanya.sql</code> dosyasini calistir.</p>`;

  const fiyatli = (ilan || []).filter(x => x.fiyat != null && !x.fiyat_gizli && x.durum !== "satildi").length;
  const sanatcilar = [...new Set((ilan || []).map(x => (x.sanatci || "").trim()).filter(Boolean))].sort();

  gvd.innerHTML = `
  <div class="ustbilgi">
    <div><h1>Kampanyalar</h1>
      <p>Indirim kurallari. Bir ilana birden fazla kampanya uyarsa indirimler ust uste binmez;
         oncelik sirasi yuksek olan uygulanir. Fiyati girilmemis ya da satilmis ilanlar indirime girmez.</p></div>
    <div class="eylemler"><button class="btn" id="yeni-kampanya">Yeni kampanya</button></div>
  </div>
  <div class="ozet">
    <div><b>${(data || []).filter(k => k.aktif).length}</b><span>Acik kampanya</span></div>
    <div><b>${fiyatli}</b><span>Indirime girebilecek ilan</span></div>
    <div><b>${(ilan || []).length - fiyatli}</b><span>Fiyati yok ya da satildi</span></div>
  </div>
  ${!(data || []).length ? `<div class="kutu bos">Henuz kampanya yok.</div>` :
    data.map(k => kampanyaKart(k, sanatcilar)).join("")}`;

  gvd.querySelectorAll("[data-kaydet-k]").forEach(b => b.addEventListener("click", async () => {
    const id = Number(b.dataset.kaydetK);
    const kok = gvd.querySelector(`[data-kampanya="${id}"]`);
    const al = ad => kok.querySelector(`[name="${ad}"]`);
    const secili = [...kok.querySelectorAll("[data-kapsam-deger]:checked")].map(x => x.value);
    const elle = al("kapsam_elle").value.split(",").map(x => x.trim()).filter(Boolean);
    const yama = {
      ad: al("ad").value.trim(),
      tur: al("tur").value, deger: Number(al("deger").value),
      kapsam: al("kapsam").value,
      kapsam_deger: al("kapsam").value === "hepsi" ? [] : (secili.length ? secili : elle),
      baslangic: al("baslangic").value ? new Date(al("baslangic").value).toISOString() : null,
      bitis: al("bitis").value ? new Date(al("bitis").value).toISOString() : null,
      aktif: al("aktif").checked,
      rozet: al("rozet").value.trim(),
      serit_metin: al("serit_metin").value.trim(),
      serit_etiket: al("serit_etiket").value.trim(),
      serit_aktif: al("serit_aktif").checked,
      oncelik: Number(al("oncelik").value) || 0,
      en_dusuk: al("en_dusuk").value.trim() === "" ? null : Number(al("en_dusuk").value),
    };
    if (!yama.ad) return bildir("Kampanyaya bir ad ver.", true);
    if (!(yama.deger > 0)) return bildir("Indirim degeri sifirdan buyuk olmali.", true);
    if (/[–—]/.test(yama.serit_metin + yama.rozet))
      return bildir("Uzun tire kullanilamaz.", true);
    const { error: e2 } = await sb.from("kampanyalar").update(yama).eq("id", id);
    bildir(e2 ? e2.message : "Kampanya kaydedildi. Sitede gorunmesi icin Yayinla.", !!e2);
  }));

  gvd.querySelectorAll("[data-sil-k]").forEach(b => b.addEventListener("click", async () => {
    if (!await sor("Kampanya silinsin mi?")) return;
    await sb.from("kampanyalar").delete().eq("id", Number(b.dataset.silK));
    kampanyaSayfasi();
  }));

  gvd.querySelectorAll("[name=kapsam]").forEach(sel => sel.addEventListener("change", () => {
    const kok = sel.closest("[data-kampanya]");
    kok.querySelectorAll("[data-kapsam-kutu]").forEach(x =>
      x.hidden = x.dataset.kapsamKutu !== sel.value);
  }));

  document.getElementById("yeni-kampanya").addEventListener("click", async () => {
    const { error: e3 } = await sb.from("kampanyalar").insert({
      ad: "Yeni kampanya", tur: "yuzde", deger: 10, kapsam: "hepsi", aktif: false });
    if (e3) return bildir(e3.message, true);
    kampanyaSayfasi();
  });
}

function kampanyaKart(k, sanatcilar) {
  const kd = k.kapsam_deger || [];
  const kat = KATLAR.map(([v, ad]) =>
    `<label><input type="checkbox" data-kapsam-deger value="${v}" ${kd.includes(v) ? "checked" : ""}>${esc(ad)}</label>`).join("");
  const snt = sanatcilar.slice(0, 40).map(a =>
    `<label><input type="checkbox" data-kapsam-deger value="${esc(a)}" ${kd.includes(a) ? "checked" : ""}>${esc(a)}</label>`).join("");
  return `
  <div class="kutu" data-kampanya="${k.id}" style="padding:1.25rem;margin-block-end:1rem">
    <div style="display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap;align-items:center;margin-block-end:1rem">
      <h3>${esc(k.ad)}</h3>
      <span class="rozet ${k.aktif ? "rozet--yayinda" : "rozet--taslak"}"><i></i>${k.aktif ? "Acik" : "Kapali"}</span>
    </div>
    <div class="uclu">
      <div class="alan"><label>Kampanya adi</label><input name="ad" value="${esc(k.ad)}"></div>
      <div class="alan"><label>Indirim turu</label>
        <select name="tur">
          <option value="yuzde" ${k.tur === "yuzde" ? "selected" : ""}>Yuzde</option>
          <option value="tutar" ${k.tur === "tutar" ? "selected" : ""}>Sabit tutar</option>
        </select></div>
      <div class="alan"><label>Deger</label>
        <input name="deger" type="number" step="any" value="${k.deger}">
        <p class="ipucu">Yuzde secildiyse 15 yazarsan yuzde on bes iner.</p></div>
    </div>
    <div class="alan">
      <label>Kimlere uygulanacak</label>
      <select name="kapsam" style="max-inline-size:340px">
        ${KAPSAM.map(([v, ad]) => `<option value="${v}" ${k.kapsam === v ? "selected" : ""}>${esc(ad)}</option>`).join("")}
      </select>
      <div data-kapsam-kutu="kategori" ${k.kapsam === "kategori" ? "" : "hidden"} style="margin-block-start:.6rem">
        <div class="etiketler">${kat}</div></div>
      <div data-kapsam-kutu="sanatci" ${k.kapsam === "sanatci" ? "" : "hidden"} style="margin-block-start:.6rem">
        <div class="etiketler">${snt || "<span class='ipucu'>Kayitli sanatci yok.</span>"}</div></div>
      <div data-kapsam-kutu="secili" ${k.kapsam === "secili" ? "" : "hidden"} style="margin-block-start:.6rem"></div>
      <div class="alan" style="margin-block-start:.6rem">
        <label>Elle liste</label>
        <input name="kapsam_elle" value="${esc(kd.join(', '))}"
               placeholder="ornek: ilan-59, ilan-114">
        <p class="ipucu">Yukaridan secim yaparsan bu alan yok sayilir.</p>
      </div>
    </div>
    <div class="uclu">
      <div class="alan"><label>Baslangic</label>
        <input name="baslangic" type="datetime-local" value="${tarihAlan(k.baslangic)}"></div>
      <div class="alan"><label>Bitis</label>
        <input name="bitis" type="datetime-local" value="${tarihAlan(k.bitis)}">
        <p class="ipucu">Bos birakirsan suresiz.</p></div>
      <div class="alan"><label>Oncelik</label>
        <input name="oncelik" type="number" value="${k.oncelik || 0}">
        <p class="ipucu">Iki kampanya ayni ilana uyarsa buyuk olan kazanir.</p></div>
    </div>
    <div class="ikili">
      <div class="alan"><label>Urun uzerindeki etiket</label>
        <input name="rozet" value="${esc(k.rozet || "")}" placeholder="Summer selection"></div>
      <div class="alan"><label>Indirim sonrasi en dusuk fiyat</label>
        <input name="en_dusuk" type="number" step="any" value="${k.en_dusuk ?? ""}">
        <p class="ipucu">Bos birakilabilir.</p></div>
    </div>
    <div class="ikili">
      <div class="alan"><label>Sitenin ust seridi</label>
        <input name="serit_metin" value="${esc(k.serit_metin || "")}"
               placeholder="Fifteen percent off the whole collection until the end of the month"></div>
      <div class="alan"><label>Seritteki kucuk etiket</label>
        <input name="serit_etiket" value="${esc(k.serit_etiket || "")}" placeholder="Summer"></div>
    </div>
    <div class="etiketler" style="margin-block-end:1rem">
      <label><input type="checkbox" name="aktif" ${k.aktif ? "checked" : ""}>Kampanya acik</label>
      <label><input type="checkbox" name="serit_aktif" ${k.serit_aktif ? "checked" : ""}>Ust seridi goster</label>
    </div>
    <div class="eylemler">
      <button class="btn btn--kucuk" data-kaydet-k="${k.id}">Kaydet</button>
      <button class="btn btn--tehlike btn--kucuk" data-sil-k="${k.id}">Sil</button>
    </div>
  </div>`;
}
