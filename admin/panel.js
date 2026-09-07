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

async function sor(soru, onay = "Delete") {
  return new Promise(cevapla => {
    const d = document.createElement("dialog");
    d.innerHTML = `<h2>${esc(soru)}</h2>
      <p style="color:var(--pnl-ink-2);margin:.75rem 0 1.5rem">This cannot be undone.</p>
      <div class="eylemler" style="justify-content:flex-end">
        <button class="btn btn--line" value="iptal">Cancel</button>
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
    <h2>Database not set up yet</h2>
    <p style="color:var(--pnl-ink-2);margin-block-start:.75rem">
      Supabase projesi bagli ve calisiyor, ama tablolar acilmamis. Supabase panelinde
      <b>SQL Editor</b> section, paste these two files in order, then run:</p>
    <ol style="color:var(--pnl-ink-2);margin:1rem 0 0 1.2rem;line-height:2">
      <li><code>supabase/KUR.sql</code> - tables, access rules, promotion system</li>
      <li><code>supabase/VERI.sql</code> - 270 listings and 879 images</li>
    </ol>
    <p style="margin-block-start:1.25rem"><button class="btn" onclick="location.reload()">Done, reload</button></p>
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
        <p class="alt">Admin panel${typeof ONIZLEME !== "undefined" && ONIZLEME ? " - onizleme" : ""}</p>
      </div>
      ${hataMesaji ? `<p class="uyari-serit uyari-serit--hata" role="alert">${esc(hataMesaji)}</p>` : ""}
      <div class="alan">
        <label for="eposta">Email</label>
        <input id="eposta" type="email" autocomplete="username" required>
      </div>
      <div class="alan">
        <label for="sifre">Password</label>
        <input id="sifre" type="password" autocomplete="current-password" required>
      </div>
      <button class="btn" type="submit">Log in</button>
      <div style="display:flex;gap:.5rem;flex-wrap:wrap">
        <button class="btn btn--line btn--kucuk" type="button" id="sifre-unuttum">Forgot password</button>
        <button class="btn btn--line btn--kucuk" type="button" id="hesap-ac">Create account</button>
      </div>
      ${typeof ONIZLEME !== "undefined" && ONIZLEME ? `<p style="font-size:.75rem;color:var(--pnl-ink-3);line-height:1.5;margin-block-start:.25rem">
        Onizleme kilidi. Denetim tarayicida yapiliyor, yani bu bir perde; gercek kilit
        It arrives once Supabase is connected. You can type anything in the email field.</p>` : ""}
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
    if (error) { girisEkrani("Email or password is incorrect."); return; }
    baslat();
  });

  const hesapDugme = document.getElementById("hesap-ac");
  if (hesapDugme) hesapDugme.addEventListener("click", async () => {
    const e = document.getElementById("eposta").value.trim();
    const p = document.getElementById("sifre").value;
    if (!e || p.length < 8) return bildir("Enter an email and choose a password of at least eight characters.", true);
    hesapDugme.disabled = true; hesapDugme.textContent = "Creating";
    const { data, error } = await sb.auth.signUp({ email: e, password: p });
    hesapDugme.disabled = false; hesapDugme.textContent = "Create account";
    if (error) return bildir(error.message, true);
    if (data && data.session) { baslat(); return; }
    bildir("Account created. Click the verification link in your email, then log in.");
  });

  document.getElementById("sifre-unuttum").addEventListener("click", async () => {
    const e = document.getElementById("eposta").value.trim();
    if (!e) return bildir("Enter your email address first.", true);
    const { error } = await sb.auth.resetPasswordForEmail(e, { redirectTo: location.href });
    bildir(error ? error.message : "Password reset link sent.", !!error);
  });
}

/* ------------------------------------------------------------------- kabuk */
const MENU = [
  ["ilanlar",     "Listings",     "▤"],
  ["fiyatlar",    "Prices",       "$"],
  ["kampanyalar", "Promotions",   "%"],
  ["siparisler",  "Orders",       "▦"],
  ["talepler",    "Inbox",        "✉"],
  ["odeme",       "Payment",      "▣"],
  ["sayfalar",    "Site texts",   "¶"],
  ["sanatcilar",  "Artists",   "✎"],
  ["ayarlar",     "Settings",     "⚙"],
  ["analitik",    "Analytics",    "◔"],
  ["kullanicilar","Users",        "◍"],
  ["gecmis",      "History",      "↺"],
];

function kabuk(icerik, aktif) {
  kok.innerHTML = `
  <div class="kabuk">
    <aside class="ray">
      <div class="ust">
        <b>Visionary Object</b>
        <span>Admin</span>
      </div>
      <nav>
        ${MENU.filter(m => m[0] !== "kullanicilar" || SAHIP())
              .map(([k, ad, ik]) => `<a href="#/${k}" ${k === aktif ? 'aria-current="page"' : ""}>
                 <i aria-hidden="true">${ik}</i>${esc(ad)}</a>`).join("")}
      </nav>
      <div class="dip">
        <p>${esc(profil?.ad || profil?.eposta || "")}</p>
        <p style="text-transform:capitalize">${esc(profil?.rol || "")}</p>
        <button class="btn btn--line btn--kucuk" id="cikis" style="margin-block-start:.6rem">Log out</button>
      </div>
    </aside>
    <main class="govde">
      <div class="cubuk">
        <div class="ara">
          <label class="sr" for="genel-ara">Search listings</label>
          <input id="genel-ara" type="search" placeholder="Title, artist or listing number" value="${esc(durumState.arama)}">
        </div>
        <div class="eylemler" style="margin-inline-start:auto">
          <a class="btn btn--line btn--kucuk" href="${esc(window.VO.SITE)}" target="_blank" rel="noopener">View site</a>
          <button class="btn btn--kucuk" id="yayinla">Publish</button>
        </div>
      </div>
      <div class="icerik" id="icerik">${ONIZLEME ? `<p class="uyari-serit uyari-serit--hata" style="border-color:var(--pnl-uyari);color:var(--pnl-uyari);background:#FDF9F0">
        Preview mode. Real data, real screens; but since Supabase is not connected
        no changes are saved. This banner disappears once setup is done.</p>` : ""}${icerik}</div>
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
  if (!YETKI()) return bildir("You don't have publish permission.", true);
  const btn = document.getElementById("yayinla");
  btn.disabled = true; btn.textContent = "Publishing\u2026";
  const { error } = await sb.from("yayin_istek").insert({
    isteyen: oturum.user.id, mesaj: "Panelden istendi"
  });
  if (error) {
    btn.disabled = false; btn.textContent = "Publish";
    return bildir("Yayin istegi gonderilemedi: " + error.message, true);
  }
  // Istegi hemen tetiklemeyi dene. GitHub'in zamanlanmis calismasi garantili
  // degil; tetik calisirsa dakikalar, calismazsa yarim saate kadar surebilir.
  let hemen = false;
  try {
    const { data: o } = await sb.auth.getSession();
    const c = await fetch(window.VO.URL + "/functions/v1/yayin-tetikle", {
      method: "POST",
      headers: { "Content-Type": "application/json", apikey: window.VO.ANAHTAR,
                 Authorization: "Bearer " + (o.session ? o.session.access_token : window.VO.ANAHTAR) },
      body: "{}",
    });
    const d = await c.json().catch(() => ({}));
    hemen = d && d.durum === "tetiklendi";
  } catch (e) { /* tetik olmadiysa zamanlanmis akis devralir */ }
  btn.disabled = false; btn.textContent = "Publish";
  bildir(hemen
    ? "Publishing started. The site updates in a few minutes."
    : "Publish queued. Live within half an hour; for instant publish use yayinla.bat on the computer.");
}

/* ---------------------------------------------------------------- ilanlar */
const KATLAR = [["tablo","Paintings & Prints"],["obje","Handmade Objects"],["belge","Documents"],
                ["rugs","Persian Rug"],["lighting","Lighting"],["sculpture","Sculpture"]];
const DURUMLAR = [["taslak","Draft"],["yayinda","Published"],["rezerve","Reserved"],
                  ["satildi","Sold"],["arsiv","Archived"]];

function durumRozet(d) {
  const sinif = d === "yayinda" ? "rozet--yayinda" : d === "taslak" ? "rozet--taslak"
              : (d === "satildi" || d === "rezerve") ? "rozet--satildi" : "";
  const ad = (DURUMLAR.find(x => x[0] === d) || [d, d])[1];
  return `<span class="rozet ${sinif}"><i></i>${esc(ad)}</span>`;
}

async function ilanlarSayfasi() {
  kabuk(`<div class="yukleniyor">Loading listings</div>`, "ilanlar");
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
      <h1>Listings</h1>
      <p>${count || 0} records. Click a row to edit the full listing.</p>
    </div>
    <div class="eylemler">
      <button class="btn" id="yeni-ilan">New listing</button>
    </div>
  </div>

  <div class="kutu" style="padding:.85rem 1rem;margin-block-end:1rem;display:flex;gap:1rem;flex-wrap:wrap;align-items:end">
    <div style="min-inline-size:170px">
      <label for="f-durum">Status</label>
      <select id="f-durum">${secenek([["hepsi","All"], ...DURUMLAR], durumState.suzgec)}</select>
    </div>
    <div style="min-inline-size:190px">
      <label for="f-kat">Category</label>
      <select id="f-kat">${secenek([["hepsi","All"], ...KATLAR], durumState.kat)}</select>
    </div>
    <div style="min-inline-size:190px">
      <label for="f-sira">Sort</label>
      <select id="f-sira">${secenek([["no-desc","Newest first"],["no-asc","Oldest first"],
        ["guncellendi-desc","Recently changed"],["baslik-asc","Title A-Z"],["fiyat-desc","Price: high to low"],
        ["fiyat-asc","Price: low to high"]], durumState.siralama)}</select>
    </div>
  </div>

  <div class="kutu" style="overflow-x:auto">
    ${!data.length ? `<div class="bos">Bu suzgece uyan ilan yok.</div>` : `
    <table>
      <thead><tr>
        <th style="inline-size:70px">Image</th><th>Title</th><th>Artist</th>
        <th>Size</th><th>Price</th><th>Status</th><th style="inline-size:90px"></th>
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
          <td class="sayisal">${r.fiyat ? esc(para(r.fiyat, r.para_birimi)) + (r.fiyat_gizli ? " <span style='color:var(--pnl-ink-3);font-size:.75rem'>(hidden)</span>" : "") : "<span style='color:var(--pnl-uyari)'>not entered</span>"}</td>
          <td>${durumRozet(r.durum)}</td>
          <td><button class="btn btn--line btn--kucuk" data-duzenle="${r.id}">Edit</button></td>
        </tr>`;
      }).join("")}</tbody>
    </table>`}
  </div>

  <div style="display:flex;gap:.5rem;align-items:center;justify-content:center;margin-block-start:1.25rem">
    <button class="btn btn--line btn--kucuk" id="onceki" ${durumState.sayfa <= 1 ? "disabled" : ""}>Previous</button>
    <span class="sayisal" style="color:var(--pnl-ink-2)">${durumState.sayfa} / ${sayfaSayisi}</span>
    <button class="btn btn--line btn--kucuk" id="sonraki" ${durumState.sayfa >= sayfaSayisi ? "disabled" : ""}>Next</button>
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
    .insert({ no, slug: "ilan-" + no, baslik: "New listing", durum: "taslak" })
    .select("id").single();
  if (error) return bildir(error.message, true);
  location.hash = "#/ilan/" + data.id;
}

/* ------------------------------------------------------------ ilan duzenle */
const ROLLER = [["tam","Full view"],["aci","Angled"],["detay","Detail"],["imza","Signature"],
  ["sertifika","Certificate"],["etiket","Label"],["plaka","Maker's plaque"],["arka","Back"],["olcu","Dimensions"]];

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
const DONEMLER = [["","Not selected"],["18th-and-earlier","18th Century and Earlier"],
  ["19th","19th Century"],["20th","20th Century"],["21st","21st Century and Contemporary"]];

async function ilanSayfasi(id) {
  kabuk(`<div class="yukleniyor">Loading listing</div>`, "ilanlar");
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
      <p>${esc(il.slug)} · VO-${il.no} · son degisiklik ${new Date(il.guncellendi).toLocaleString("en-US")}</p>
    </div>
    <div class="eylemler">
      <a class="btn btn--line btn--kucuk" href="#/ilanlar">Listeye don</a>
      <a class="btn btn--line btn--kucuk" target="_blank" rel="noopener"
         href="${esc(window.VO.SITE)}/item/${esc(il.slug)}.html">Sitede gor</a>
      <button class="btn btn--tehlike btn--kucuk" id="ilan-sil">Ilani sil</button>
      <button class="btn" id="kaydet">Save</button>
    </div>
  </div>

  <div class="sekmeler" role="tablist">
    <button role="tab" aria-selected="true"  data-sekme="gorsel">Images</button>
    <button role="tab" aria-selected="false" data-sekme="icerik">Content</button>
    <button role="tab" aria-selected="false" data-sekme="fiyat">Price & status</button>
    <button role="tab" aria-selected="false" data-sekme="siniflandirma">Classification</button>
    <button role="tab" aria-selected="false" data-sekme="seo">SEO</button>
  </div>

  <form id="ilan-form">
  <section data-panel="gorsel">
    <p style="color:var(--pnl-ink-2);margin-block-end:1rem">
      The first image is the cover. Drag to reorder.</p>
    <div class="kareler" id="kare-liste"></div>
    <div class="birak" id="birak-alani" style="margin-block-start:1rem">
      <p>Drag photos here or
        <label style="display:inline;text-decoration:underline;cursor:pointer;color:var(--pnl-ink)">
          choose from your computer<input type="file" id="dosya-sec" accept="image/*" multiple hidden></label></p>
      <p class="ipucu" style="margin-block-start:.4rem">JPG, PNG, HEIC or WEBP. Max 50 MB per file.</p>
    </div>
    <div id="yukleme-durum" style="margin-block-start:.75rem"></div>
  </section>

  <section data-panel="icerik" hidden>
    ${alanKutu("baslik", "Listing title", il.baslik, "text", "The name shown on the site and in search results.")}
    ${alanKutu("aciklama", "Description", il.aciklama, "textarea", "The text buyers read. Do not use em dashes.")}
    <div class="ikili">
      ${alanKutu("sanatci", "Artist", il.sanatci)}
      ${alanKutu("eser_adi", "Work title", il.eser_adi)}
    </div>
    <div class="uclu">
      ${alanKutu("donem", "Period", il.donem, "text", "Example: 20th century")}
      ${alanKutu("teknik", "Technique", il.teknik, "text", "Example: oil on canvas")}
      ${alanKutu("baski", "Edition", il.baski)}
    </div>
    <div class="uclu">
      ${alanKutu("galeri_adi", "Gallery", il.galeri_adi)}
      ${alanKutu("ref", "Reference no", il.ref)}
      ${alanKutu("kaynak_dosya", "Source file", il.kaynak_dosya)}
    </div>
    ${alanKutu("etiket", "Back label text", il.etiket, "textarea")}
    ${alanKutu("belge", "Certificate note", il.belge, "textarea")}
    ${alanKutu("biyografi", "Artist biography", il.biyografi, "textarea")}
    ${alanKutu("aciklama_not", "Internal note (hidden on site)", il.aciklama_not, "textarea")}
  </section>

  <section data-panel="fiyat" hidden>
    <div class="uclu">
      ${alanKutu("fiyat", "Price", il.fiyat, "number", "Blank shows Price Upon Request on the site.")}
      ${alanKutu("fiyat_eski", "Old price", il.fiyat_eski, "number", "Filled shows a discount on the site.")}
      <div class="alan">
        <label for="a-para_birimi">Currency</label>
        <select id="a-para_birimi" name="para_birimi">
          ${["USD","EUR","GBP","TRY"].map(p => `<option ${il.para_birimi === p ? "selected" : ""}>${p}</option>`).join("")}
        </select>
      </div>
    </div>
    <div class="ikili">
      <div class="alan">
        <label for="a-durum">Status</label>
        <select id="a-durum" name="durum">${DURUMLAR.map(([v, ad]) =>
          `<option value="${v}" ${il.durum === v ? "selected" : ""}>${esc(ad)}</option>`).join("")}</select>
        <p class="ipucu">Only "Published" listings appear on the site.</p>
      </div>
      <div class="alan">
        <label for="a-kat">Category</label>
        <select id="a-kat" name="kat">${KATLAR.map(([v, ad]) =>
          `<option value="${v}" ${il.kat === v ? "selected" : ""}>${esc(ad)}</option>`).join("")}</select>
      </div>
    </div>
    <div class="uclu">
      ${alanKutu("olcu_w", "Width (in)", il.olcu_w, "number")}
      ${alanKutu("olcu_h", "Height (in)", il.olcu_h, "number")}
      ${alanKutu("olcu_d", "Depth (in)", il.olcu_d, "number")}
    </div>
    ${alanKutu("olcu_nesi", "Measurement basis", il.olcu_nesi, "text", "Example: outside of frame, sheet, canvas")}
    <div class="etiketler" style="margin-block-start:.5rem">
      <label><input type="checkbox" id="a-fiyat_gizli" ${il.fiyat_gizli ? "checked" : ""}>Hide price on site</label>
      <label><input type="checkbox" id="a-pazarlik" ${il.pazarlik ? "checked" : ""}>Open to offers</label>
      <label><input type="checkbox" id="a-satin_alinabilir" ${il.satin_alinabilir ? "checked" : ""}>Tek tikla satin alinabilir</label>
      <label><input type="checkbox" id="a-one_cikan" ${il.one_cikan ? "checked" : ""}>Feature on homepage</label>
    </div>
  </section>

  <section data-panel="siniflandirma" hidden>
    <p style="color:var(--pnl-ink-2);margin-block-end:1.25rem">
      These feed the site filters. Buyers search with these in the left filters.</p>
    <div class="alan"><label>Subject</label>${kutular("subject", facet.subject)}</div>
    <div class="alan"><label>Medium</label>${kutular("medium", facet.medium)}</div>
    <div class="alan"><label>Style</label>${kutular("style", facet.style)}</div>
    <div class="alan"><label>Frame</label>${kutular("framing", facet.framing)}</div>
    <div class="alan"><label>Color</label>${kutular("color", facet.color)}</div>
    <div class="alan" style="max-inline-size:340px">
      <label for="a-period">Century</label>
      <select id="a-period">${DONEMLER.map(([v, ad]) =>
        `<option value="${v}" ${(facet.period || "") === v ? "selected" : ""}>${esc(ad)}</option>`).join("")}</select>
    </div>
  </section>

  <section data-panel="seo" hidden>
    ${alanKutu("slug", "Address (slug)", il.slug, "text", "Changing it breaks the old address. Do not touch unless necessary.")}
    ${alanKutu("seo_baslik", "Search title", il.seo_baslik, "text", "Blank uses the listing title. Keep under 60 characters.")}
    ${alanKutu("seo_aciklama", "Search description", il.seo_aciklama, "textarea", "Keep under 155 characters.")}
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
    if (!await sor("Delete this listing?")) return;
    const { error } = await sb.from("ilanlar").delete().eq("id", il.id);
    if (error) return bildir(error.message, true);
    bildir("Listing deleted."); location.hash = "#/ilanlar";
  });
}

/* -------------------------------------------------------- kare listesi ve surukleme */
function kareleriCiz(il, kareler) {
  const kap = document.getElementById("kare-liste");
  if (!kareler.length) {
    kap.innerHTML = `<p style="color:var(--pnl-ink-2)">No images on this listing yet.</p>`;
    return;
  }
  kap.innerHTML = kareler.map((k, i) => `
    <figure class="kare" draggable="true" data-kid="${k.id}" data-i="${i}" style="margin:0">
      ${i === 0 ? `<span class="kapak-rozet">Cover</span>` : ""}
      <button type="button" class="sil" data-sil="${k.id}" aria-label="Remove this image">×</button>
      <span class="tut" aria-hidden="true">drag</span>
      <img loading="lazy" alt="${esc(k.alt_metin || "")}" src="${esc(gorselUrl(k.yol, 400))}">
      <div class="alt-bar">
        <select data-rol="${k.id}" aria-label="Image role">
          ${ROLLER.map(([v, ad]) => `<option value="${v}" ${k.rol === v ? "selected" : ""}>${esc(ad)}</option>`).join("")}
        </select>
        <input type="text" data-alt="${k.id}" value="${esc(k.alt_metin || "")}"
               placeholder="Image description" style="min-block-size:36px;font-size:.8125rem">
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
    if (!await sor("Remove this image from the listing?", "Remove")) return;
    const kid = Number(b.dataset.sil);
    const k = kareler.find(x => x.id === kid);
    const { error } = await sb.from("kareler").delete().eq("id", kid);
    if (error) return bildir(error.message, true);
    if (k) await sb.storage.from("gorseller").remove([k.yol]);
    const i = kareler.findIndex(x => x.id === kid);
    kareler.splice(i, 1);
    await siraKaydet(kareler);
    kareleriCiz(il, kareler);
    bildir("Image removed.");
  }));

  kap.querySelectorAll("[data-rol]").forEach(s => s.addEventListener("change", async () => {
    const { error } = await sb.from("kareler").update({ rol: s.value }).eq("id", Number(s.dataset.rol));
    bildir(error ? error.message : "Role updated.", !!error);
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
    if (!resimler.length) return bildir("Image file not found.", true);
    let sayac = 0;
    for (const dosya of resimler) {
      sayac++;
      durum.innerHTML = `<p class="ipucu">${sayac} / ${resimler.length} uploading: ${esc(dosya.name)}</p>`;
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
    bildir(`${sayac} images added.`);
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
    // Tek tikla satis. Odeme genel ayari kapaliysa bu isaret sitede is gormez.
    satin_alinabilir: al("satin_alinabilir").checked,
    one_cikan: al("one_cikan").checked,
    slug: al("slug").value.trim(),
    seo_baslik: al("seo_baslik").value.trim(),
    seo_aciklama: al("seo_aciklama").value.trim(),
    facet,
  };

  const tire = Object.values(yeni).filter(v => typeof v === "string" && /[–—]/.test(v));
  if (tire.length) return bildir("Long dashes found. Site rule: use short hyphens only.", true);
  if (!yeni.baslik) return bildir("Title cannot be blank.", true);
  if (!/^[a-z0-9-]+$/.test(yeni.slug)) return bildir("Address may only contain lowercase letters, digits and hyphens.", true);

  const btn = document.getElementById("kaydet");
  btn.disabled = true; btn.textContent = "Kaydediliyor";
  const { error } = await sb.from("ilanlar").update(yeni).eq("id", il.id);
  btn.disabled = false; btn.textContent = "Save";
  if (error) return bildir(error.message, true);
  bildir("Saved. Publish to show on the site.");
  Object.assign(il, yeni);
}

/* --------------------------------------------------------------- fiyatlar */
async function fiyatSayfasi() {
  kabuk(`<div class="yukleniyor">Loading</div>`, "fiyatlar");
  const { data, error } = await sb.from("ilanlar")
    .select("id,no,slug,baslik,sanatci,fiyat,fiyat_eski,para_birimi,fiyat_gizli,durum")
    .order("no");
  const gvd = document.getElementById("icerik");
  if (error) return gvd.innerHTML = `<p class="uyari-serit uyari-serit--hata">${esc(error.message)}</p>`;

  const eksik = data.filter(d => d.fiyat == null).length;
  gvd.innerHTML = `
  <div class="ustbilgi">
    <div><h1>Prices</h1>
      <p>Enter all listings' prices from one screen. Filling a field and clicking elsewhere saves it.</p></div>
  </div>
  <div class="ozet">
    <div><b>${data.length}</b><span>Listings</span></div>
    <div><b>${data.length - eksik}</b><span>With price</span></div>
    <div><b>${eksik}</b><span>Awaiting price</span></div>
  </div>
  <div class="kutu" style="overflow-x:auto">
    <table><thead><tr>
      <th>No</th><th>Title</th><th>Artist</th><th style="inline-size:140px">Price</th>
      <th style="inline-size:140px">Old price</th><th style="inline-size:90px">Currency</th>
      <th style="inline-size:80px">Hidden</th><th>Status</th>
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
           ${d.fiyat_gizli ? "checked" : ""} aria-label="Hide price"></td>
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
  kabuk(`<div class="yukleniyor">Loading</div>`, "sayfalar");
  const { data, error } = await sb.from("sayfalar").select("*").order("anahtar");
  const gvd = document.getElementById("icerik");
  if (error) return gvd.innerHTML = `<p class="uyari-serit uyari-serit--hata">${esc(error.message)}</p>`;

  gvd.innerHTML = `
  <div class="ustbilgi"><div><h1>Site texts</h1>
    <p>Text of fixed pages like home, about, shipping, returns. Listing descriptions live on each listing's own page.</p>
    <p class="ipucu" style="margin-block-start:.4rem">If you leave the text BLANK, the site shows professionally pre-written text.
       Anything you write here REPLACES the pre-written text on that page; so either write the full text or leave it blank.</p></div></div>
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
        <button class="btn btn--kucuk" data-sayfa="${s.anahtar}">Save</button>
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
    bildir(error ? error.message : "Page saved.", !!error);
  }));
}

/* ------------------------------------------------------------- sanatcilar */
async function sanatcilarSayfasi() {
  kabuk(`<div class="yukleniyor">Loading</div>`, "sanatcilar");
  const { data } = await sb.from("sanatcilar").select("*").order("ad");
  const gvd = document.getElementById("icerik");
  gvd.innerHTML = `
  <div class="ustbilgi"><div><h1>Artists</h1>
    <p>The biography entered here appears on all of that artist's listings.</p></div>
    <div class="eylemler"><button class="btn" id="yeni-sanatci">New artist</button></div></div>
  <div class="kutu" style="overflow-x:auto">
    ${!data?.length ? `<div class="bos">Henuz sanatci kaydi yok.</div>` : `
    <table><thead><tr><th>Name</th><th>Born</th><th>Died</th><th>Country</th><th>Biography</th><th></th></tr></thead>
    <tbody>${data.map(s => `<tr>
      <td><input value="${esc(s.ad)}" data-s="ad" data-id="${s.id}"></td>
      <td><input value="${esc(s.dogum || "")}" data-s="dogum" data-id="${s.id}" style="inline-size:90px"></td>
      <td><input value="${esc(s.olum || "")}" data-s="olum" data-id="${s.id}" style="inline-size:90px"></td>
      <td><input value="${esc(s.ulke || "")}" data-s="ulke" data-id="${s.id}" style="inline-size:120px"></td>
      <td><textarea data-s="biyografi" data-id="${s.id}" rows="2" style="min-block-size:44px">${esc(s.biyografi || "")}</textarea></td>
      <td><button class="btn btn--tehlike btn--kucuk" data-sil-s="${s.id}">Delete</button></td>
    </tr>`).join("")}</tbody></table>`}
  </div>`;

  gvd.querySelectorAll("[data-s]").forEach(el => el.addEventListener("change", async () => {
    const { error } = await sb.from("sanatcilar")
      .update({ [el.dataset.s]: el.value }).eq("id", Number(el.dataset.id));
    if (error) bildir(error.message, true);
  }));
  gvd.querySelectorAll("[data-sil-s]").forEach(b => b.addEventListener("click", async () => {
    if (!await sor("Delete this artist record?")) return;
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
  kabuk(`<div class="yukleniyor">Loading</div>`, "ayarlar");
  const { data } = await sb.from("ayarlar").select("*").order("anahtar");
  const gvd = document.getElementById("icerik");
  gvd.innerHTML = `
  <div class="ustbilgi"><div><h1>Settings</h1>
    <p>Brand name, contact, location and pricing policy. After changing, press Publish.</p></div></div>
  ${(data || []).map(a => `
    <div class="kutu" style="padding:1.25rem;margin-block-end:.75rem">
      <h3 style="text-transform:capitalize">${esc(a.anahtar.replace(/_/g, " "))}</h3>
      <p class="ipucu" style="margin-block-end:.75rem">${esc(a.aciklama || "")}</p>
      ${(a.deger !== null && typeof a.deger === "object" ? Object.entries(a.deger)
         : [["deger", a.deger]]).map(([k, v]) => `
        <div class="alan" style="max-inline-size:480px">
          <label for="ay-${a.anahtar}-${k}" style="text-transform:capitalize">${esc(k.replace(/_/g, " "))}</label>
          ${typeof v === "boolean"
            ? `<label class="etiketler" style="margin:0"><input type="checkbox" id="ay-${a.anahtar}-${k}" ${v ? "checked" : ""}> On</label>`
            : `<input id="ay-${a.anahtar}-${k}" value="${esc(v)}">`}
        </div>`).join("")}
      <button class="btn btn--kucuk" data-ayar="${a.anahtar}">Save</button>
    </div>`).join("")}`;

  gvd.querySelectorAll("[data-ayar]").forEach(b => b.addEventListener("click", async () => {
    const a = (data || []).find(x => x.anahtar === b.dataset.ayar);
    // Ayarlar ya bir nesnedir (marka bilgileri gibi) ya da tek bir degerdir
    // (odeme_acik gibi). Ikisini de ayni ekrandan kaydedebilmek icin ayiriyoruz.
    let yeni;
    if (a.deger !== null && typeof a.deger === "object") {
      yeni = {};
      for (const [k, v] of Object.entries(a.deger)) {
        const el = document.getElementById(`ay-${a.anahtar}-${k}`);
        yeni[k] = typeof v === "boolean" ? el.checked : el.value;
      }
    } else {
      const el = document.getElementById(`ay-${a.anahtar}-deger`);
      yeni = typeof a.deger === "boolean" ? el.checked : el.value;
    }
    const { error } = await sb.from("ayarlar")
      .update({ deger: yeni, guncellendi: new Date().toISOString() }).eq("anahtar", a.anahtar);
    bildir(error ? error.message : "Settings saved.", !!error);
  }));
}

/* ------------------------------------------------------------ kullanicilar */
async function kullanicilarSayfasi() {
  if (!SAHIP()) { location.hash = "#/ilanlar"; return; }
  kabuk(`<div class="yukleniyor">Loading</div>`, "kullanicilar");
  const { data } = await sb.from("profiller").select("*").order("olusturuldu");
  const gvd = document.getElementById("icerik");
  gvd.innerHTML = `
  <div class="ustbilgi"><div><h1>Users</h1>
    <p>To invite a new user, use Authentication > Users > Invite user in the Supabase panel.
       A user appears here after first login; change their role here.</p></div></div>
  <div class="kutu" style="overflow-x:auto">
    <table><thead><tr><th>Email</th><th>Name</th><th>Role</th><th>Last login</th><th></th></tr></thead>
    <tbody>${(data || []).map(p => `<tr>
      <td>${esc(p.eposta)}</td>
      <td><input value="${esc(p.ad || "")}" data-p="ad" data-id="${p.id}"></td>
      <td><select data-p="rol" data-id="${p.id}" ${p.id === oturum.user.id ? "disabled" : ""}>
        ${[["sahip","Owner - everything and user management"],
           ["yonetici","Yonetici - butun icerik"],
           ["okur","Reader - view only"]].map(([v, ad]) =>
          `<option value="${v}" ${p.rol === v ? "selected" : ""}>${esc(ad)}</option>`).join("")}
      </select></td>
      <td style="color:var(--pnl-ink-3);font-size:.8125rem">${p.son_giris ? new Date(p.son_giris).toLocaleString("en-US") : "-"}</td>
      <td>${p.id === oturum.user.id ? "" :
        `<button class="btn btn--tehlike btn--kucuk" data-sil-p="${p.id}">Remove</button>`}</td>
    </tr>`).join("")}</tbody></table>
  </div>`;

  gvd.querySelectorAll("[data-p]").forEach(el => el.addEventListener("change", async () => {
    const { error } = await sb.from("profiller").update({ [el.dataset.p]: el.value }).eq("id", el.dataset.id);
    bildir(error ? error.message : "Guncellendi.", !!error);
  }));
  gvd.querySelectorAll("[data-sil-p]").forEach(b => b.addEventListener("click", async () => {
    if (!await sor("Remove this user's panel access?", "Remove")) return;
    const { error } = await sb.from("profiller").delete().eq("id", b.dataset.silP);
    if (error) return bildir(error.message, true);
    bildir("Access removed. To delete the account entirely: Supabase > Authentication.");
    kullanicilarSayfasi();
  }));
}

/* ----------------------------------------------------------------- gecmis */
async function gecmisSayfasi() {
  kabuk(`<div class="yukleniyor">Loading</div>`, "gecmis");
  const [{ data: log }, { data: yayin }] = await Promise.all([
    sb.from("degisiklik_log").select("*").order("ne_zaman", { ascending: false }).limit(120),
    sb.from("yayin_istek").select("*").order("istendi", { ascending: false }).limit(15),
  ]);
  const gvd = document.getElementById("icerik");
  const ISLEM = { INSERT: "added", UPDATE: "changed", DELETE: "deleted" };
  gvd.innerHTML = `
  <div class="ustbilgi"><div><h1>History</h1>
    <p>Who changed what and when, plus publish requests.</p></div></div>

  <h2 style="margin-block-end:.75rem">Publish requests</h2>
  <div class="kutu" style="overflow-x:auto;margin-block-end:2rem">
    ${!yayin?.length ? `<div class="bos">Henuz yayin istegi yok.</div>` : `
    <table><thead><tr><th>Requested</th><th>Status</th><th>Finished</th><th>Message</th></tr></thead>
    <tbody>${yayin.map(y => `<tr>
      <td>${new Date(y.istendi).toLocaleString("en-US")}</td>
      <td>${esc(y.durum)}</td>
      <td>${y.bitti ? new Date(y.bitti).toLocaleString("en-US") : "-"}</td>
      <td style="font-size:.8125rem;color:var(--pnl-ink-2)">${esc(y.kayit || y.mesaj || "")}</td>
    </tr>`).join("")}</tbody></table>`}
  </div>

  <h2 style="margin-block-end:.75rem">Degisiklikler</h2>
  <div class="kutu" style="overflow-x:auto">
    ${!log?.length ? `<div class="bos">No records.</div>` : `
    <table><thead><tr><th>Time</th><th>Table</th><th>Record</th><th>Action</th></tr></thead>
    <tbody>${log.map(l => `<tr>
      <td>${new Date(l.ne_zaman).toLocaleString("en-US")}</td>
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
  if (h.startsWith("#/siparisler")) return siparisSayfasi();
  if (h.startsWith("#/talepler")) return talepSayfasi();
  if (h.startsWith("#/odeme")) return odemeSayfasi();
  if (h.startsWith("#/analitik")) return analitikSayfasi();
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
    setTimeout(() => bildir("Preview mode: showing the real 270 listings, changes are not saved.", false), 400);
    return;
  }
  if (!window.VO || window.VO.URL.startsWith("BURAYA")) {
    kok.innerHTML = `<div class="giris"><div class="kutu" style="padding:2rem;max-inline-size:520px">
      <h2>Panel not connected yet</h2>
      <p style="color:var(--pnl-ink-2);margin-block-start:.75rem">
        <code>admin/config.js</code> take the two values from your Supabase project and paste them,
        then reload this page. Step-by-step instructions are in <code>KURULUM.md</code>.</p>
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
const KAPSAM = [["hepsi","Entire collection"],["kategori","Selected categories"],
                ["sanatci","Selected artists"],["secili","Selected listings"]];

function tarihAlan(d) { return d ? String(d).slice(0, 16) : ""; }

async function kampanyaSayfasi() {
  kabuk(`<div class="yukleniyor">Loading</div>`, "kampanyalar");
  const gvd = document.getElementById("icerik");
  const [{ data, error }, { data: ilan }] = await Promise.all([
    sb.from("kampanyalar").select("*").order("oncelik", { ascending: false }),
    sb.from("ilanlar").select("kat,sanatci,fiyat,fiyat_gizli,durum"),
  ]);
  if (error) return gvd.innerHTML = `<p class="uyari-serit uyari-serit--hata">${esc(error.message)}
    If the promotions table is missing, run <code>supabase/04_kampanya.sql</code>.</p>`;

  const fiyatli = (ilan || []).filter(x => x.fiyat != null && !x.fiyat_gizli && x.durum !== "satildi").length;
  const sanatcilar = [...new Set((ilan || []).map(x => (x.sanatci || "").trim()).filter(Boolean))].sort();

  gvd.innerHTML = `
  <div class="ustbilgi">
    <div><h1>Promotions</h1>
      <p>Discount rules. If multiple promotions match a listing, discounts do not stack;
         the highest-priority one applies. Listings without a price or sold are excluded.</p></div>
    <div class="eylemler"><button class="btn" id="yeni-kampanya">New promotion</button></div>
  </div>
  <div class="ozet">
    <div><b>${(data || []).filter(k => k.aktif).length}</b><span>Open promotions</span></div>
    <div><b>${fiyatli}</b><span>Listings eligible for discount</span></div>
    <div><b>${(ilan || []).length - fiyatli}</b><span>No price or sold</span></div>
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
    if (!yama.ad) return bildir("Give the promotion a name.", true);
    if (!(yama.deger > 0)) return bildir("Discount value must be above zero.", true);
    if (/[–—]/.test(yama.serit_metin + yama.rozet))
      return bildir("Uzun tire kullanilamaz.", true);
    const { error: e2 } = await sb.from("kampanyalar").update(yama).eq("id", id);
    bildir(e2 ? e2.message : "Promotion saved. Publish to show on the site.", !!e2);
  }));

  gvd.querySelectorAll("[data-sil-k]").forEach(b => b.addEventListener("click", async () => {
    if (!await sor("Delete this promotion?")) return;
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
      <span class="rozet ${k.aktif ? "rozet--yayinda" : "rozet--taslak"}"><i></i>${k.aktif ? "On" : "Off"}</span>
    </div>
    <div class="uclu">
      <div class="alan"><label>Promotion name</label><input name="ad" value="${esc(k.ad)}"></div>
      <div class="alan"><label>Discount type</label>
        <select name="tur">
          <option value="yuzde" ${k.tur === "yuzde" ? "selected" : ""}>Percent</option>
          <option value="tutar" ${k.tur === "tutar" ? "selected" : ""}>Fixed amount</option>
        </select></div>
      <div class="alan"><label>Value</label>
        <input name="deger" type="number" step="any" value="${k.deger}">
        <p class="ipucu">If percent is selected, entering 15 takes fifteen percent off.</p></div>
    </div>
    <div class="alan">
      <label>Applies to</label>
      <select name="kapsam" style="max-inline-size:340px">
        ${KAPSAM.map(([v, ad]) => `<option value="${v}" ${k.kapsam === v ? "selected" : ""}>${esc(ad)}</option>`).join("")}
      </select>
      <div data-kapsam-kutu="kategori" ${k.kapsam === "kategori" ? "" : "hidden"} style="margin-block-start:.6rem">
        <div class="etiketler">${kat}</div></div>
      <div data-kapsam-kutu="sanatci" ${k.kapsam === "sanatci" ? "" : "hidden"} style="margin-block-start:.6rem">
        <div class="etiketler">${snt || "<span class='ipucu'>No saved artists.</span>"}</div></div>
      <div data-kapsam-kutu="secili" ${k.kapsam === "secili" ? "" : "hidden"} style="margin-block-start:.6rem"></div>
      <div class="alan" style="margin-block-start:.6rem">
        <label>Manual list</label>
        <input name="kapsam_elle" value="${esc(kd.join(', '))}"
               placeholder="e.g. ilan-59, ilan-114">
        <p class="ipucu">If you select above, this field is ignored.</p>
      </div>
    </div>
    <div class="uclu">
      <div class="alan"><label>Start</label>
        <input name="baslangic" type="datetime-local" value="${tarihAlan(k.baslangic)}"></div>
      <div class="alan"><label>End</label>
        <input name="bitis" type="datetime-local" value="${tarihAlan(k.bitis)}">
        <p class="ipucu">Blank means no end date.</p></div>
      <div class="alan"><label>Oncelik</label>
        <input name="oncelik" type="number" value="${k.oncelik || 0}">
        <p class="ipucu">If two promotions match a listing, the larger one wins.</p></div>
    </div>
    <div class="ikili">
      <div class="alan"><label>Badge on the product</label>
        <input name="rozet" value="${esc(k.rozet || "")}" placeholder="Summer selection"></div>
      <div class="alan"><label>Lowest price after discount</label>
        <input name="en_dusuk" type="number" step="any" value="${k.en_dusuk ?? ""}">
        <p class="ipucu">May be left blank.</p></div>
    </div>
    <div class="ikili">
      <div class="alan"><label>Sitenin ust seridi</label>
        <input name="serit_metin" value="${esc(k.serit_metin || "")}"
               placeholder="Fifteen percent off the whole collection until the end of the month"></div>
      <div class="alan"><label>Small ribbon badge</label>
        <input name="serit_etiket" value="${esc(k.serit_etiket || "")}" placeholder="Summer"></div>
    </div>
    <div class="etiketler" style="margin-block-end:1rem">
      <label><input type="checkbox" name="aktif" ${k.aktif ? "checked" : ""}>Promotion on</label>
      <label><input type="checkbox" name="serit_aktif" ${k.serit_aktif ? "checked" : ""}>Ust seridi goster</label>
    </div>
    <div class="eylemler">
      <button class="btn btn--kucuk" data-kaydet-k="${k.id}">Save</button>
      <button class="btn btn--tehlike btn--kucuk" data-sil-k="${k.id}">Delete</button>
    </div>
  </div>`;
}

/* ===========================================================================
   Odeme, Siparisler ve Gelen kutusu sayfalari.

   panel.js'in sonuna eklenir (build sirasinda degil, dogrudan dosyada).
   Buradaki hicbir sey gizli anahtar tasimaz; Stripe'in gizli anahtari
   yalnizca Supabase Edge Function'in gizli degiskeninde durur.
   =========================================================================== */

const SIPARIS_DURUM = {
  basladi: "Started", odendi: "Paid", iptal: "Cancelled",
  iade: "Refunded", basarisiz: "Failed",
};
const TALEP_DURUM = {
  yeni: "New", okundu: "Read", yanitlandi: "Replied",
  kapandi: "Closed", spam: "Spam",
};

function paraGoster(v, birim) {
  const n = Number(v || 0);
  try {
    return new Intl.NumberFormat("en-US", { style: "currency",
      currency: birim || "USD", maximumFractionDigits: 0 }).format(n);
  } catch (e) { return n.toLocaleString("en-US") + " " + (birim || "USD"); }
}

function zaman(t) { return t ? new Date(t).toLocaleString("en-US") : "-"; }

/* --------------------------------------------------------------- siparisler */
async function siparisSayfasi() {
  kabuk(`<div class="yukleniyor">Loading</div>`, "siparisler");
  const { data, error } = await sb.from("siparisler")
    .select("*").order("olusturuldu", { ascending: false }).limit(200);
  const gvd = document.getElementById("icerik");
  if (error) return void (gvd.innerHTML = hataKutusu(error));

  const s = data || [];
  const odenen = s.filter(x => x.durum === "odendi");
  const toplam = odenen.reduce((t, x) => t + Number(x.tutar || 0) + Number(x.kargo || 0), 0);

  gvd.innerHTML = `
  <div class="ustbilgi"><div><h1>Orders</h1>
    <p>Sales via Stripe. When payment completes, the item is automatically
       marked sold and the site is republished.</p></div></div>

  <div class="kutu" style="padding:1.25rem;margin-block-end:.75rem;display:flex;gap:2.5rem;flex-wrap:wrap">
    <div><div class="ipucu">Paid orders</div><strong style="font-size:1.5rem">${odenen.length}</strong></div>
    <div><div class="ipucu">Total collected</div><strong style="font-size:1.5rem">${paraGoster(toplam, odenen[0]?.para_birimi)}</strong></div>
    <div><div class="ipucu">Incomplete</div><strong style="font-size:1.5rem">${s.filter(x => x.durum === "basladi").length}</strong></div>
  </div>

  <div class="kutu" style="overflow-x:auto">
    ${!s.length ? `<div class="bos">No orders yet. They will appear here once the Stripe key is entered and payment is on.
      </div>` : `
    <table><thead><tr>
      <th>Date</th><th>Item</th><th>Customer</th><th>Amount</th><th>Status</th><th></th>
    </tr></thead><tbody>${s.map(x => `<tr>
      <td style="white-space:nowrap">${zaman(x.olusturuldu)}${x.test_mi ? ` <span class="ipucu">test</span>` : ""}</td>
      <td>${x.ilan_slug ? `<a href="#/ilan/${x.ilan_id}">${esc(x.ilan_baslik || x.ilan_slug)}</a>` : "-"}</td>
      <td>${esc(x.ad || "-")}<br><span class="ipucu">${esc(x.eposta || "")}</span></td>
      <td style="white-space:nowrap">${paraGoster(Number(x.tutar) + Number(x.kargo || 0), x.para_birimi)}</td>
      <td>${esc(SIPARIS_DURUM[x.durum] || x.durum)}</td>
      <td><button class="btn btn--kucuk" data-siparis="${x.id}">Details</button></td>
    </tr>`).join("")}</tbody></table>`}
  </div>
  <div id="siparisDetay" style="margin-block-start:.75rem"></div>`;

  gvd.querySelectorAll("[data-siparis]").forEach(b => b.addEventListener("click", () => {
    const x = s.find(v => String(v.id) === b.dataset.siparis);
    const a = x.adres || {};
    document.getElementById("siparisDetay").innerHTML = `
    <div class="kutu" style="padding:1.25rem">
      <h3>Order #${x.id}</h3>
      <p class="ipucu">Stripe session: ${esc(x.oturum || "-")}</p>
      <div class="alan" style="max-inline-size:520px">
        <label>Address</label>
        <div>${[a.line1, a.line2, a.postal_code, a.city, a.state, a.country]
              .filter(Boolean).map(esc).join(", ") || "-"}</div>
      </div>
      <div class="alan" style="max-inline-size:520px">
        <label>Phone</label><div>${esc(x.telefon || "-")}</div>
      </div>
      <div class="alan" style="max-inline-size:320px">
        <label for="sd-${x.id}">Status</label>
        <select id="sd-${x.id}">${Object.entries(SIPARIS_DURUM).map(([k, v]) =>
          `<option value="${k}" ${x.durum === k ? "selected" : ""}>${v}</option>`).join("")}</select>
      </div>
      <button class="btn btn--kucuk" id="sk-${x.id}">Save</button>
    </div>`;
    document.getElementById("sk-" + x.id).addEventListener("click", async () => {
      const yeni = document.getElementById("sd-" + x.id).value;
      const { error } = await sb.from("siparisler")
        .update({ durum: yeni, guncellendi: new Date().toISOString() }).eq("id", x.id);
      bildir(error ? error.message : "Order updated.", !!error);
      if (!error) siparisSayfasi();
    });
  }));
}

/* ------------------------------------------------------------ gelen kutusu */
async function talepSayfasi() {
  kabuk(`<div class="yukleniyor">Loading</div>`, "talepler");
  const [{ data, error }, { data: uyeler }] = await Promise.all([
    sb.from("talepler").select("*").order("olusturuldu", { ascending: false }).limit(300),
    sb.from("bulten").select("eposta,olusturuldu,aktif").order("olusturuldu", { ascending: false }).limit(1000),
  ]);
  const gvd = document.getElementById("icerik");
  if (error) return void (gvd.innerHTML = hataKutusu(error));

  const t = data || [];
  const yeni = t.filter(x => x.durum === "yeni").length;
  const bulten = uyeler || [];

  gvd.innerHTML = `
  <div class="ustbilgi"><div><h1>Gelen kutusu</h1>
    <p>Messages from the site's "Contact Seller" form.
       ${yeni ? `<strong>${yeni} new</strong>` : "No new messages."}</p></div></div>

  <div class="kutu" style="padding:1.25rem;margin-block-end:.75rem">
    <div style="display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap;align-items:center">
      <h3 style="margin:0">Newsletter signups <span class="ipucu" style="font-weight:400">${bulten.length} emails</span></h3>
      ${bulten.length ? `<button class="btn btn--kucuk" id="bultenKopyala">Copy addresses</button>` : ""}
    </div>
    ${bulten.length ? `<p class="ipucu" style="margin-block-start:.5rem">${bulten.slice(0, 8).map(b => esc(b.eposta)).join(", ")}${bulten.length > 8 ? " ..." : ""}</p>`
      : `<p class="ipucu" style="margin-block-start:.5rem">Everyone who leaves an email in the footer form collects here.</p>`}
  </div>

  ${!t.length ? `<div class="kutu"><div class="bos">No messages yet.</div></div>` : t.map(x => `
    <div class="kutu" style="padding:1.25rem;margin-block-end:.75rem">
      <div style="display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap">
        <div>
          <h3 style="margin:0">${esc(x.ad || "Anonymous")}
            <span class="ipucu" style="font-weight:400">&lt;${esc(x.eposta)}&gt;</span></h3>
          <p class="ipucu" style="margin-block:.25rem 0">${zaman(x.olusturuldu)}
            ${x.ilan_slug ? ` &middot; ${esc(x.ilan_slug)}` : ""}
            ${x.telefon ? ` &middot; ${esc(x.telefon)}` : ""}
            ${x.teklif ? ` &middot; teklif ${paraGoster(x.teklif, x.para_birimi)}` : ""}</p>
        </div>
        <div style="display:flex;gap:.5rem;align-items:flex-start">
          <select id="td-${x.id}" style="inline-size:auto">${Object.entries(TALEP_DURUM).map(([k, v]) =>
            `<option value="${k}" ${x.durum === k ? "selected" : ""}>${v}</option>`).join("")}</select>
          <button class="btn btn--kucuk" data-talep="${x.id}">Save</button>
          <a class="btn btn--kucuk" href="mailto:${encodeURIComponent(x.eposta)}?subject=${
            encodeURIComponent("Re: " + (x.ilan_slug || "your message"))}">Reply</a>
        </div>
      </div>
      <p style="margin-block-start:.9rem;white-space:pre-wrap">${esc(x.mesaj)}</p>
    </div>`).join("")}`;

  gvd.querySelectorAll("[data-talep]").forEach(b => b.addEventListener("click", async () => {
    const id = b.dataset.talep;
    const { error } = await sb.from("talepler")
      .update({ durum: document.getElementById("td-" + id).value,
                guncellendi: new Date().toISOString() }).eq("id", id);
    bildir(error ? error.message : "Saved.", !!error);
  }));

  const bk = document.getElementById("bultenKopyala");
  if (bk) bk.addEventListener("click", () => {
    navigator.clipboard.writeText(bulten.map(b => b.eposta).join(", "))
      .then(() => bildir("Addresses copied to clipboard."))
      .catch(() => bildir("Copy failed; the browser refused permission.", true));
  });
}

/* ---------------------------------------------------------------- odeme */
const ODEME_ANAHTARLARI = ["odeme_acik", "odeme_mod", "odeme_para_birimi",
                           "kargo_ucreti", "kargo_metni", "odeme_iade_gun",
                           "talep_eposta"];

async function odemeSayfasi() {
  kabuk(`<div class="yukleniyor">Loading</div>`, "odeme");
  const gvd = document.getElementById("icerik");

  const [{ data: ayar, error }, { count: acikAdet }] = await Promise.all([
    sb.from("ayarlar").select("*").in("anahtar", ODEME_ANAHTARLARI),
    sb.from("ilanlar").select("id", { count: "exact", head: true })
      .eq("satin_alinabilir", true),
  ]);
  if (error) return void (gvd.innerHTML = hataKutusu(error));

  const a = {};
  for (const s of ayar || []) a[s.anahtar] = typeof s.deger === "string" ? s.deger : String(s.deger ?? "");

  gvd.innerHTML = `
  <div class="ustbilgi"><div><h1>Payment</h1>
    <p>One-click purchase runs via Stripe. The secret key is not here,
       it lives in Supabase's secret settings; this screen neither sees nor stores it.</p></div></div>

  <div class="kutu" style="padding:1.25rem;margin-block-end:.75rem">
    <h3>Connection status</h3>
    <p class="ipucu">The button below asks the payment function in Supabase
       whether a key was entered. The key itself never reaches
       the browser.</p>
    <div id="odemeDurum" style="margin-block:.75rem 0"></div>
    <button class="btn btn--kucuk" id="odemeKontrol">Check connection</button>
  </div>

  <div class="kutu" style="padding:1.25rem;margin-block-end:.75rem">
    <h3>Settings</h3>
    <div class="alan" style="max-inline-size:480px">
      <label class="etiketler" style="margin:0">
        <input type="checkbox" id="od-acik" ${a.odeme_acik === "evet" ? "checked" : ""}>
        One-click purchase on</label>
      <p class="ipucu">When off, only "Contact Seller" shows on the site.</p>
    </div>
    <div class="alan" style="max-inline-size:320px">
      <label for="od-mod">Mode</label>
      <select id="od-mod">
        <option value="test" ${a.odeme_mod === "test" ? "selected" : ""}>Test</option>
        <option value="canli" ${a.odeme_mod === "canli" ? "selected" : ""}>Live</option>
      </select>
      <p class="ipucu">Select whichever key you entered in Supabase: sk_test... or sk_live...</p>
    </div>
    <div class="alan" style="max-inline-size:320px">
      <label for="od-birim">Currency</label>
      <input id="od-birim" value="${esc(a.odeme_para_birimi || "USD")}" maxlength="3">
    </div>
    <div class="alan" style="max-inline-size:320px">
      <label for="od-kargo">Fixed shipping fee</label>
      <input id="od-kargo" type="number" step="0.01" min="0" value="${esc(a.kargo_ucreti || "0")}">
      <p class="ipucu">If 0, no shipping line appears at checkout.</p>
    </div>
    <div class="alan" style="max-inline-size:480px">
      <label for="od-kargometin">Shipping text on the product page</label>
      <input id="od-kargometin" value="${esc(a.kargo_metni || "")}">
    </div>
    <div class="alan" style="max-inline-size:320px">
      <label for="od-iade">Return window (days)</label>
      <input id="od-iade" type="number" min="0" value="${esc(a.odeme_iade_gun || "14")}">
    </div>
    <div class="alan" style="max-inline-size:480px">
      <label for="od-talep">Request notification email</label>
      <input id="od-talep" type="email" value="${esc(a.talep_eposta || "")}"
             placeholder="ornek@visionaryobjects.com">
      <p class="ipucu">Notifies here when a new message lands in the inbox.
         Blank still delivers to the panel, just without email.</p>
    </div>
    <button class="btn" id="odemeKaydet">Save</button>
  </div>

  <div class="kutu" style="padding:1.25rem">
    <h3>Which items sell in one click</h3>
    <p class="ipucu">Currently <strong>${acikAdet || 0}</strong> items have one-click sale on.
       Each item enables it from its own page under the "Price & status" tab. To be sellable,
       an item needs a price, must not be hidden, and its status must be Published.</p>
    <button class="btn btn--kucuk" id="hepsiniAc">Enable on all priced items</button>
    <button class="btn btn--kucuk" id="hepsiniKapat">Disable everywhere</button>
  </div>`;

  document.getElementById("odemeKontrol").addEventListener("click", async () => {
    const kutu = document.getElementById("odemeDurum");
    kutu.textContent = "Checking...";
    try {
      const c = await fetch(window.VO.URL + "/functions/v1/odeme-baslat", {
        method: "POST",
        headers: { "Content-Type": "application/json", apikey: window.VO.ANAHTAR,
                   Authorization: "Bearer " + window.VO.ANAHTAR },
        body: JSON.stringify({ slug: "__kontrol__" }),
      });
      const d = await c.json().catch(() => ({}));
      if (c.status === 503 && d.hata === "odeme_kapali") {
        kutu.innerHTML = /anahtari henuz/.test(d.mesaj || "")
          ? `<strong>Stripe key not entered yet.</strong>
             <span class="ipucu">Supabase &gt; Edge Functions &gt; Secrets.
             Add STRIPE_SECRET_KEY.</span>`
          : `<strong>Key present, payment off in panel.</strong>
             <span class="ipucu">Yukaridaki kutucugu isaretleyip kaydet.</span>`;
      } else if (c.status === 404) {
        kutu.innerHTML = `<strong>Anahtar tamam, fonksiyon calisiyor.</strong>
          <span class="ipucu">Deneme eseri bulunamadi, beklenen cevap bu.</span>`;
      } else {
        kutu.innerHTML = `<strong>Cevap:</strong> ${c.status} ${esc(JSON.stringify(d))}`;
      }
    } catch (e) {
      kutu.innerHTML = `<strong>Fonksiyona ulasilamadi.</strong>
        <span class="ipucu">${esc(String(e))}</span>`;
    }
  });

  document.getElementById("odemeKaydet").addEventListener("click", async () => {
    const yeni = {
      odeme_acik: document.getElementById("od-acik").checked ? "evet" : "hayir",
      odeme_mod: document.getElementById("od-mod").value,
      odeme_para_birimi: document.getElementById("od-birim").value.trim().toUpperCase() || "USD",
      kargo_ucreti: String(document.getElementById("od-kargo").value || "0"),
      kargo_metni: document.getElementById("od-kargometin").value,
      odeme_iade_gun: String(document.getElementById("od-iade").value || "14"),
      talep_eposta: document.getElementById("od-talep").value.trim(),
    };
    const simdi = new Date().toISOString();
    for (const [k, v] of Object.entries(yeni)) {
      const { error } = await sb.from("ayarlar")
        .update({ deger: v, guncellendi: simdi }).eq("anahtar", k);
      if (error) return bildir(error.message, true);
    }
    bildir("Payment settings saved. Publish to show on the site.");
  });

  document.getElementById("hepsiniAc").addEventListener("click", async () => {
    const { error, count } = await sb.from("ilanlar")
      .update({ satin_alinabilir: true }, { count: "exact" })
      .eq("durum", "yayinda").eq("fiyat_gizli", false).not("fiyat", "is", null);
    bildir(error ? error.message : `${count || 0} eserde tek tikla satis acildi.`, !!error);
    if (!error) odemeSayfasi();
  });

  document.getElementById("hepsiniKapat").addEventListener("click", async () => {
    const { error } = await sb.from("ilanlar")
      .update({ satin_alinabilir: false }).eq("satin_alinabilir", true);
    bildir(error ? error.message : "One-click sale closed everywhere.", !!error);
    if (!error) odemeSayfasi();
  });
}

/* ===========================================================================
   Analitik sayfasi + Gelen kutusuna bulten bolumu.
   panel.js'in sonuna eklenir. Sayac cerezsizdir; burada yalnizca sayilir.
   =========================================================================== */

async function analitikSayfasi() {
  kabuk(`<div class="yukleniyor">Loading</div>`, "analitik");
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
    const ad = bas.toLocaleDateString("en-US", { day: "numeric", month: "short" });
    const n = v.filter(x => {
      const t = simdi - new Date(x.olusturuldu).getTime();
      return t >= (i) * gunMs - (simdi % gunMs) && t < (i + 1) * gunMs - (simdi % gunMs);
    }).length;
    gunler.push([ad, n]);
  }
  const enCok = Math.max(1, ...gunler.map(g => g[1]));

  const YOL_ADI = y => y === "#/" ? "Home"
    : y.indexOf("#/item/") === 0 ? "Item: " + y.slice(7)
    : y.indexOf("#/browse") === 0 ? "Vitrin"
    : y.indexOf("#/info/") === 0 ? "Page: " + y.slice(7)
    : y;

  gvd.innerHTML = `
  <div class="ustbilgi"><div><h1>Analytics</h1>
    <p>Cookieless first-party counter: only page path and referrer are stored.
       No IP, cookies or personal data. Logged-in panel users are not counted.</p></div></div>

  <div class="ozet">
    <div><b>${bugun}</b><span>Today</span></div>
    <div><b>${hafta}</b><span>Last 7 days</span></div>
    <div><b>${v.length}</b><span>Last 30 days</span></div>
  </div>

  <div class="kutu" style="padding:1.25rem;margin-block-end:.75rem">
    <h3 style="margin-block-end:.75rem">Last 14 days</h3>
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
      <h3 style="margin-block-end:.75rem">Most viewed items</h3>
      ${!eserler.length ? `<div class="bos" style="padding:1.5rem">No data yet.</div>`
        : eserler.map(([slug, n]) => `
        <div style="display:flex;justify-content:space-between;gap:1rem;padding-block:.35rem;border-block-end:1px solid var(--pnl-line)">
          <a href="https://visionaryobjects.com/#/item/${esc(slug)}" target="_blank" rel="noopener">${esc(slug)}</a>
          <span class="sayisal">${n}</span></div>`).join("")}
    </div>
    <div class="kutu" style="padding:1.25rem">
      <h3 style="margin-block-end:.75rem">Where they come from</h3>
      ${!kaynaklar.length ? `<div class="bos" style="padding:1.5rem">No sources besides direct visits.</div>`
        : kaynaklar.map(([k, n]) => `
        <div style="display:flex;justify-content:space-between;gap:1rem;padding-block:.35rem;border-block-end:1px solid var(--pnl-line)">
          <span>${esc(k)}</span><span class="sayisal">${n}</span></div>`).join("")}
    </div>
  </div>

  <div class="kutu" style="padding:1.25rem;margin-block-start:.75rem">
    <h3 style="margin-block-end:.75rem">Most visited pages</h3>
    ${sayfalar.map(([y, n]) => `
      <div style="display:flex;justify-content:space-between;gap:1rem;padding-block:.35rem;border-block-end:1px solid var(--pnl-line)">
        <span>${esc(YOL_ADI(y))}</span><span class="sayisal">${n}</span></div>`).join("")}
  </div>

  <div class="kutu" style="padding:1.25rem;margin-block-start:.75rem">
    <h3>Cleanup</h3>
    <p class="ipucu" style="margin-block-end:.75rem">Deleting records older than 90 days keeps the table small; reports look at the last 30 days.</p>
    <button class="btn btn--kucuk" id="analitikTemizle">Delete older than 90 days</button>
  </div>`;

  document.getElementById("analitikTemizle").addEventListener("click", async () => {
    const sinir = new Date(Date.now() - 90 * 24 * 3600 * 1000).toISOString();
    const { error } = await sb.from("ziyaretler").delete().lt("olusturuldu", sinir);
    bildir(error ? error.message : "Old records deleted.", !!error);
  });
}

