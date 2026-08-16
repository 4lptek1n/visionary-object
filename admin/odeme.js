/* ===========================================================================
   Odeme, Siparisler ve Gelen kutusu sayfalari.

   panel.js'in sonuna eklenir (build sirasinda degil, dogrudan dosyada).
   Buradaki hicbir sey gizli anahtar tasimaz; Stripe'in gizli anahtari
   yalnizca Supabase Edge Function'in gizli degiskeninde durur.
   =========================================================================== */

const SIPARIS_DURUM = {
  basladi: "Baslatildi", odendi: "Odendi", iptal: "Iptal",
  iade: "Iade edildi", basarisiz: "Basarisiz",
};
const TALEP_DURUM = {
  yeni: "Yeni", okundu: "Okundu", yanitlandi: "Yanitlandi",
  kapandi: "Kapandi", spam: "Spam",
};

function paraGoster(v, birim) {
  const n = Number(v || 0);
  try {
    return new Intl.NumberFormat("tr-TR", { style: "currency",
      currency: birim || "USD", maximumFractionDigits: 0 }).format(n);
  } catch (e) { return n.toLocaleString("tr-TR") + " " + (birim || "USD"); }
}

function zaman(t) { return t ? new Date(t).toLocaleString("tr-TR") : "-"; }

/* --------------------------------------------------------------- siparisler */
async function siparisSayfasi() {
  kabuk(`<div class="yukleniyor">Yukleniyor</div>`, "siparisler");
  const { data, error } = await sb.from("siparisler")
    .select("*").order("olusturuldu", { ascending: false }).limit(200);
  const gvd = document.getElementById("icerik");
  if (error) return void (gvd.innerHTML = hataKutusu(error));

  const s = data || [];
  const odenen = s.filter(x => x.durum === "odendi");
  const toplam = odenen.reduce((t, x) => t + Number(x.tutar || 0) + Number(x.kargo || 0), 0);

  gvd.innerHTML = `
  <div class="ustbilgi"><div><h1>Siparisler</h1>
    <p>Stripe uzerinden gelen satislar. Odeme tamamlaninca eser otomatik olarak
       satildi isaretlenir ve site yeniden yayinlanir.</p></div></div>

  <div class="kutu" style="padding:1.25rem;margin-block-end:.75rem;display:flex;gap:2.5rem;flex-wrap:wrap">
    <div><div class="ipucu">Odenen siparis</div><strong style="font-size:1.5rem">${odenen.length}</strong></div>
    <div><div class="ipucu">Toplam tahsilat</div><strong style="font-size:1.5rem">${paraGoster(toplam, odenen[0]?.para_birimi)}</strong></div>
    <div><div class="ipucu">Tamamlanmamis</div><strong style="font-size:1.5rem">${s.filter(x => x.durum === "basladi").length}</strong></div>
  </div>

  <div class="kutu" style="overflow-x:auto">
    ${!s.length ? `<div class="bos">Henuz siparis yok. Stripe anahtari girilip odeme acildiginda
      buraya dusecek.</div>` : `
    <table><thead><tr>
      <th>Tarih</th><th>Eser</th><th>Musteri</th><th>Tutar</th><th>Durum</th><th></th>
    </tr></thead><tbody>${s.map(x => `<tr>
      <td style="white-space:nowrap">${zaman(x.olusturuldu)}${x.test_mi ? ` <span class="ipucu">test</span>` : ""}</td>
      <td>${x.ilan_slug ? `<a href="#/ilan/${x.ilan_id}">${esc(x.ilan_baslik || x.ilan_slug)}</a>` : "-"}</td>
      <td>${esc(x.ad || "-")}<br><span class="ipucu">${esc(x.eposta || "")}</span></td>
      <td style="white-space:nowrap">${paraGoster(Number(x.tutar) + Number(x.kargo || 0), x.para_birimi)}</td>
      <td>${esc(SIPARIS_DURUM[x.durum] || x.durum)}</td>
      <td><button class="btn btn--kucuk" data-siparis="${x.id}">Detay</button></td>
    </tr>`).join("")}</tbody></table>`}
  </div>
  <div id="siparisDetay" style="margin-block-start:.75rem"></div>`;

  gvd.querySelectorAll("[data-siparis]").forEach(b => b.addEventListener("click", () => {
    const x = s.find(v => String(v.id) === b.dataset.siparis);
    const a = x.adres || {};
    document.getElementById("siparisDetay").innerHTML = `
    <div class="kutu" style="padding:1.25rem">
      <h3>Siparis #${x.id}</h3>
      <p class="ipucu">Stripe oturumu: ${esc(x.oturum || "-")}</p>
      <div class="alan" style="max-inline-size:520px">
        <label>Adres</label>
        <div>${[a.line1, a.line2, a.postal_code, a.city, a.state, a.country]
              .filter(Boolean).map(esc).join(", ") || "-"}</div>
      </div>
      <div class="alan" style="max-inline-size:520px">
        <label>Telefon</label><div>${esc(x.telefon || "-")}</div>
      </div>
      <div class="alan" style="max-inline-size:320px">
        <label for="sd-${x.id}">Durum</label>
        <select id="sd-${x.id}">${Object.entries(SIPARIS_DURUM).map(([k, v]) =>
          `<option value="${k}" ${x.durum === k ? "selected" : ""}>${v}</option>`).join("")}</select>
      </div>
      <button class="btn btn--kucuk" id="sk-${x.id}">Kaydet</button>
    </div>`;
    document.getElementById("sk-" + x.id).addEventListener("click", async () => {
      const yeni = document.getElementById("sd-" + x.id).value;
      const { error } = await sb.from("siparisler")
        .update({ durum: yeni, guncellendi: new Date().toISOString() }).eq("id", x.id);
      bildir(error ? error.message : "Siparis guncellendi.", !!error);
      if (!error) siparisSayfasi();
    });
  }));
}

/* ------------------------------------------------------------ gelen kutusu */
async function talepSayfasi() {
  kabuk(`<div class="yukleniyor">Yukleniyor</div>`, "talepler");
  const { data, error } = await sb.from("talepler")
    .select("*").order("olusturuldu", { ascending: false }).limit(300);
  const gvd = document.getElementById("icerik");
  if (error) return void (gvd.innerHTML = hataKutusu(error));

  const t = data || [];
  const yeni = t.filter(x => x.durum === "yeni").length;

  gvd.innerHTML = `
  <div class="ustbilgi"><div><h1>Gelen kutusu</h1>
    <p>Sitedeki "Contact Seller" formundan gelen mesajlar.
       ${yeni ? `<strong>${yeni} yeni</strong>` : "Yeni mesaj yok."}</p></div></div>

  ${!t.length ? `<div class="kutu"><div class="bos">Henuz mesaj yok.</div></div>` : t.map(x => `
    <div class="kutu" style="padding:1.25rem;margin-block-end:.75rem">
      <div style="display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap">
        <div>
          <h3 style="margin:0">${esc(x.ad || "Isimsiz")}
            <span class="ipucu" style="font-weight:400">&lt;${esc(x.eposta)}&gt;</span></h3>
          <p class="ipucu" style="margin-block:.25rem 0">${zaman(x.olusturuldu)}
            ${x.ilan_slug ? ` &middot; ${esc(x.ilan_slug)}` : ""}
            ${x.telefon ? ` &middot; ${esc(x.telefon)}` : ""}
            ${x.teklif ? ` &middot; teklif ${paraGoster(x.teklif, x.para_birimi)}` : ""}</p>
        </div>
        <div style="display:flex;gap:.5rem;align-items:flex-start">
          <select id="td-${x.id}" style="inline-size:auto">${Object.entries(TALEP_DURUM).map(([k, v]) =>
            `<option value="${k}" ${x.durum === k ? "selected" : ""}>${v}</option>`).join("")}</select>
          <button class="btn btn--kucuk" data-talep="${x.id}">Kaydet</button>
          <a class="btn btn--kucuk" href="mailto:${encodeURIComponent(x.eposta)}?subject=${
            encodeURIComponent("Re: " + (x.ilan_slug || "your message"))}">Yanitla</a>
        </div>
      </div>
      <p style="margin-block-start:.9rem;white-space:pre-wrap">${esc(x.mesaj)}</p>
    </div>`).join("")}`;

  gvd.querySelectorAll("[data-talep]").forEach(b => b.addEventListener("click", async () => {
    const id = b.dataset.talep;
    const { error } = await sb.from("talepler")
      .update({ durum: document.getElementById("td-" + id).value,
                guncellendi: new Date().toISOString() }).eq("id", id);
    bildir(error ? error.message : "Kaydedildi.", !!error);
  }));
}

/* ---------------------------------------------------------------- odeme */
const ODEME_ANAHTARLARI = ["odeme_acik", "odeme_mod", "odeme_para_birimi",
                           "kargo_ucreti", "kargo_metni", "odeme_iade_gun",
                           "talep_eposta"];

async function odemeSayfasi() {
  kabuk(`<div class="yukleniyor">Yukleniyor</div>`, "odeme");
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
  <div class="ustbilgi"><div><h1>Odeme</h1>
    <p>Tek tikla satin alma Stripe uzerinden calisir. Gizli anahtar burada degil,
       Supabase'in gizli ayarlarinda durur; bu ekran onu ne gorur ne saklar.</p></div></div>

  <div class="kutu" style="padding:1.25rem;margin-block-end:.75rem">
    <h3>Baglanti durumu</h3>
    <p class="ipucu">Asagidaki dugme Supabase'deki odeme fonksiyonuna bir soru sorar
       ve anahtarin girilip girilmedigini soyler. Anahtarin kendisi hicbir zaman
       tarayiciya inmez.</p>
    <div id="odemeDurum" style="margin-block:.75rem 0"></div>
    <button class="btn btn--kucuk" id="odemeKontrol">Baglantiyi kontrol et</button>
  </div>

  <div class="kutu" style="padding:1.25rem;margin-block-end:.75rem">
    <h3>Ayarlar</h3>
    <div class="alan" style="max-inline-size:480px">
      <label class="etiketler" style="margin:0">
        <input type="checkbox" id="od-acik" ${a.odeme_acik === "evet" ? "checked" : ""}>
        Tek tikla satin alma acik</label>
      <p class="ipucu">Kapaliyken sitede yalnizca "Contact Seller" gorunur.</p>
    </div>
    <div class="alan" style="max-inline-size:320px">
      <label for="od-mod">Mod</label>
      <select id="od-mod">
        <option value="test" ${a.odeme_mod === "test" ? "selected" : ""}>Test</option>
        <option value="canli" ${a.odeme_mod === "canli" ? "selected" : ""}>Canli</option>
      </select>
      <p class="ipucu">Supabase'e hangi anahtari yazdiysan onu sec: sk_test... ya da sk_live...</p>
    </div>
    <div class="alan" style="max-inline-size:320px">
      <label for="od-birim">Para birimi</label>
      <input id="od-birim" value="${esc(a.odeme_para_birimi || "USD")}" maxlength="3">
    </div>
    <div class="alan" style="max-inline-size:320px">
      <label for="od-kargo">Sabit kargo ucreti</label>
      <input id="od-kargo" type="number" step="0.01" min="0" value="${esc(a.kargo_ucreti || "0")}">
      <p class="ipucu">0 ise odeme ekraninda kargo satiri cikmaz.</p>
    </div>
    <div class="alan" style="max-inline-size:480px">
      <label for="od-kargometin">Urun sayfasindaki kargo yazisi</label>
      <input id="od-kargometin" value="${esc(a.kargo_metni || "")}">
    </div>
    <div class="alan" style="max-inline-size:320px">
      <label for="od-iade">Iade suresi (gun)</label>
      <input id="od-iade" type="number" min="0" value="${esc(a.odeme_iade_gun || "14")}">
    </div>
    <div class="alan" style="max-inline-size:480px">
      <label for="od-talep">Talep bildirim e-postasi</label>
      <input id="od-talep" type="email" value="${esc(a.talep_eposta || "")}"
             placeholder="ornek@thetimesfigures.com">
      <p class="ipucu">Gelen kutusuna yeni mesaj dustugunde buraya haber gider.
         Bos birakirsan mesaj yine panele duser, sadece e-posta gitmez.</p>
    </div>
    <button class="btn" id="odemeKaydet">Kaydet</button>
  </div>

  <div class="kutu" style="padding:1.25rem">
    <h3>Hangi eserler tek tikla satilir</h3>
    <p class="ipucu">Su an <strong>${acikAdet || 0}</strong> eserde tek tikla satis acik.
       Her eserin kendi sayfasinda "Fiyat ve durum" sekmesinden acilir. Bir eserin
       satilabilmesi icin fiyati girilmis, gizli olmamali ve durumu Yayinda olmali.</p>
    <button class="btn btn--kucuk" id="hepsiniAc">Fiyati olan tum eserlerde ac</button>
    <button class="btn btn--kucuk" id="hepsiniKapat">Hepsinde kapat</button>
  </div>`;

  document.getElementById("odemeKontrol").addEventListener("click", async () => {
    const kutu = document.getElementById("odemeDurum");
    kutu.textContent = "Kontrol ediliyor...";
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
          ? `<strong>Stripe anahtari henuz girilmedi.</strong>
             <span class="ipucu">Supabase &gt; Edge Functions &gt; Secrets ekranina
             STRIPE_SECRET_KEY ekle.</span>`
          : `<strong>Anahtar var, odeme panelden kapali.</strong>
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
    bildir("Odeme ayarlari kaydedildi. Sitede gorunmesi icin Yayinla.");
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
    bildir(error ? error.message : "Tek tikla satis her yerde kapatildi.", !!error);
    if (!error) odemeSayfasi();
  });
}
