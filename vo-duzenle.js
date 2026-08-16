/* Visionary Object - sitenin ustunde yerinde duzenleme
 *
 * Ziyaretci icin bu dosya hicbir sey yapmaz: ilk is olarak tarayicida bir
 * oturum anahtari var mi diye bakar, yoksa oracikta durur. Supabase kutuphanesi
 * yalnizca giris yapmis yoneticinin tarayicisina iner.
 *
 * Giris yapmis yonetici siteyi normal gezer; ustte ince bir cubuk cikar.
 * Duzenlemeyi acinca baslik, sanatci, donem, fiyat ve aciklama dogrudan
 * sayfanin uzerinde degistirilir. Kaydedilen sey veritabanina yazilir; sitenin
 * kendisi Yayinla dendiginde yeniden uretilir.
 */
(function () {
  "use strict";
  if (!window.VO_AYAR || !window.VO_AYAR.URL || String(window.VO_AYAR.URL).indexOf("BURAYA") === 0) return;

  var ref = "";
  try { ref = new URL(window.VO_AYAR.URL).hostname.split(".")[0]; } catch (e) { return; }
  var anahtarAdi = "sb-" + ref + "-auth-token";

  // Oturum yoksa hicbir sey yukleme. Ziyaretcinin maliyeti sifir.
  try { if (!localStorage.getItem(anahtarAdi)) return; } catch (e) { return; }

  var sb = null, profil = null, duzenle = false, bekleyen = 0, urunler = {};

  var STIL = [
    '.vo-cubuk{position:fixed;inset-block-start:0;inset-inline:0;z-index:200;background:#222;color:#F4F2E3;',
    'display:flex;align-items:center;gap:.75rem;padding:.4rem .9rem;font-size:.8125rem;',
    "font-family:'Instrument',ui-sans-serif,system-ui,sans-serif;flex-wrap:wrap}",
    '.vo-cubuk b{font-weight:500;letter-spacing:.1em;text-transform:uppercase;font-size:.6875rem}',
    '.vo-cubuk button,.vo-cubuk a{background:transparent;border:1px solid rgba(244,242,227,.45);color:inherit;',
    'padding:.3rem .7rem;border-radius:2px;cursor:pointer;font:inherit;text-decoration:none;min-block-size:32px}',
    '.vo-cubuk button:hover,.vo-cubuk a:hover{background:rgba(244,242,227,.14)}',
    '.vo-cubuk .acik{background:#F4F2E3;color:#222;border-color:#F4F2E3}',
    '.vo-cubuk .sag{margin-inline-start:auto;display:flex;gap:.5rem;align-items:center;flex-wrap:wrap}',
    '.vo-cubuk .bekleyen{color:#F0C36A}',
    'body.vo-acik{padding-block-start:44px}',
    'body.vo-duzenle [data-vo]{outline:1px dashed rgba(34,34,34,.45);outline-offset:3px;cursor:text;position:relative}',
    'body.vo-duzenle [data-vo]:hover{outline-color:#222;background:rgba(240,195,106,.16)}',
    'body.vo-duzenle [data-vo-kart]{position:relative}',
    '.vo-rozet{position:absolute;inset-block-start:6px;inset-inline-start:6px;z-index:5;background:#222;color:#F4F2E3;',
    'font-size:.625rem;letter-spacing:.1em;text-transform:uppercase;padding:.15rem .4rem;border-radius:2px}',
    '.vo-giris{position:fixed;inset:0;z-index:210;background:rgba(34,34,34,.55);display:grid;place-items:center}',
    '.vo-giris form{background:#fff;padding:1.75rem;inline-size:min(360px,92vw);display:grid;gap:.75rem;',
    "font-family:'Instrument',ui-sans-serif,system-ui,sans-serif}",
    '.vo-giris input{padding:.6rem;border:1px solid #8A8779;min-block-size:44px;inline-size:100%}',
    '.vo-uyari{position:fixed;inset-block-end:1rem;inset-inline-end:1rem;z-index:220;background:#222;color:#F4F2E3;',
    "padding:.65rem 1rem;font-size:.8125rem;font-family:'Instrument',ui-sans-serif,system-ui,sans-serif;border-radius:2px}",
    '.vo-uyari.hata{background:#8E2B22}',
    '@media (prefers-reduced-motion:reduce){*{animation:none!important}}'
  ].join("");

  function stilKur() {
    var s = document.createElement("style");
    s.textContent = STIL;
    document.head.appendChild(s);
  }

  function uyari(metin, hata) {
    var d = document.createElement("div");
    d.className = "vo-uyari" + (hata ? " hata" : "");
    d.textContent = metin;
    document.body.appendChild(d);
    setTimeout(function () { d.remove(); }, hata ? 5200 : 2600);
  }

  function slugAl() {
    var m = location.hash.match(/#\/item\/([a-z0-9-]+)/i);
    return m ? m[1] : null;
  }

  /* ------------------------------------------------------------- cubuk */
  function cubukCiz() {
    var eski = document.querySelector(".vo-cubuk");
    if (eski) eski.remove();
    var c = document.createElement("div");
    c.className = "vo-cubuk";
    c.innerHTML =
      '<b>Visionary Object yonetim</b>' +
      '<button id="vo-ac" class="' + (duzenle ? "acik" : "") + '">' +
        (duzenle ? "Duzenleme acik" : "Duzenlemeyi ac") + "</button>" +
      '<button id="vo-gorsel">Gorseller</button>' +
      '<button id="vo-durum">Durum</button>' +
      '<button id="vo-kampanya">Kampanya</button>' +
      '<span class="sag">' +
        (bekleyen ? '<span class="bekleyen">' + bekleyen + " degisiklik yayinlanmadi</span>" : "") +
        '<button id="vo-yayinla">Yayinla</button>' +
        '<a href="admin/">Gelismis</a>' +
        '<button id="vo-cikis">Cikis</button>' +
      "</span>";
    document.body.appendChild(c);
    document.body.classList.add("vo-acik");

    c.querySelector("#vo-ac").onclick = function () {
      duzenle = !duzenle;
      document.body.classList.toggle("vo-duzenle", duzenle);
      cubukCiz();
      if (duzenle) alanlariBagla();
    };
    c.querySelector("#vo-gorsel").onclick = gorselPaneli;
    c.querySelector("#vo-durum").onclick = durumPaneli;
    c.querySelector("#vo-kampanya").onclick = kampanyaPaneli;
    c.querySelector("#vo-yayinla").onclick = yayinla;
    c.querySelector("#vo-cikis").onclick = function () {
      sb.auth.signOut().then(function () { location.reload(); });
    };
  }

  /* -------------------------------------------------- alanlari duzenlenebilir yap */
  var ALAN = {
    baslik:   { sutun: "baslik",   tur: "metin" },
    sanatci:  { sutun: "sanatci",  tur: "metin" },
    donem:    { sutun: "donem",    tur: "metin" },
    aciklama: { sutun: "aciklama", tur: "uzun"  },
    fiyat:    { sutun: "fiyat",    tur: "sayi"  }
  };

  function alanlariBagla() {
    var slug = slugAl();
    document.querySelectorAll("[data-vo]").forEach(function (el) {
      if (el.dataset.voBagli) return;
      el.dataset.voBagli = "1";
      el.addEventListener("click", function (e) {
        if (!duzenle) return;
        var kart = el.closest("[data-vo-kart]");
        var hedef = kart ? kart.dataset.voKart : (el.closest("[data-vo-urun]") ?
          el.closest("[data-vo-urun]").dataset.voUrun : slug);
        if (!hedef) return;
        e.preventDefault();
        e.stopPropagation();
        alanDuzenle(el, hedef);
      }, true);
    });
  }

  function alanDuzenle(el, slug) {
    var ad = el.dataset.vo, tanim = ALAN[ad];
    if (!tanim || el.querySelector(".vo-giris-alan")) return;
    var eskiHtml = el.innerHTML;
    var mevcut = (urunler[slug] && urunler[slug][tanim.sutun]);
    if (mevcut == null) mevcut = tanim.tur === "sayi" ? "" : el.textContent.trim();
    if (tanim.tur === "sayi" && /Price Upon Request/i.test(String(mevcut))) mevcut = "";

    var alan = document.createElement(tanim.tur === "uzun" ? "textarea" : "input");
    alan.className = "vo-giris-alan";
    if (tanim.tur === "sayi") { alan.type = "number"; alan.step = "any"; alan.placeholder = "Fiyat"; }
    if (tanim.tur === "uzun") alan.rows = 8;
    alan.value = mevcut;
    alan.style.cssText = "inline-size:100%;font:inherit;color:inherit;background:#fff;border:1px solid #222;padding:.35rem .5rem;min-block-size:44px";
    el.innerHTML = "";
    el.appendChild(alan);
    alan.focus();
    if (alan.select) alan.select();

    function bitir(kaydet) {
      var yeni = alan.value;
      el.innerHTML = eskiHtml;
      if (!kaydet) return;
      var deger = tanim.tur === "sayi" ? (yeni.trim() === "" ? null : Number(yeni)) : yeni.trim();
      if (tanim.tur !== "sayi" && /[–—]/.test(deger)) {
        uyari("Uzun tire kullanilamaz, sitenin kurali bunu yasakliyor.", true);
        return;
      }
      var yama = {};
      yama[tanim.sutun] = deger;
      if (tanim.sutun === "fiyat" && deger != null) yama.fiyat_gizli = false;
      sb.from("ilanlar").update(yama).eq("slug", slug).then(function (c) {
        if (c.error) return uyari(c.error.message, true);
        if (!urunler[slug]) urunler[slug] = {};
        urunler[slug][tanim.sutun] = deger;
        el.textContent = tanim.sutun === "fiyat"
          ? (deger == null ? "Price Upon Request" : yeniFiyat(deger, slug))
          : deger;
        bekleyen++;
        cubukCiz();
        uyari("Kaydedildi. Sitede gorunmesi icin Yayinla.");
      });
    }
    alan.addEventListener("blur", function () { bitir(true); });
    alan.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { e.preventDefault(); bitir(false); }
      if (e.key === "Enter" && tanim.tur !== "uzun") { e.preventDefault(); alan.blur(); }
    });
  }

  function yeniFiyat(deger, slug) {
    var birim = (urunler[slug] && urunler[slug].para_birimi) || "USD";
    try {
      return new Intl.NumberFormat("en-US", { style: "currency", currency: birim, maximumFractionDigits: 0 }).format(deger);
    } catch (e) { return "$" + deger; }
  }

  /* ------------------------------------------------------------ durum paneli */
  var DURUMLAR = [["yayinda","Yayinda"],["taslak","Taslak"],["rezerve","Rezerve"],
                  ["satildi","Satildi"],["arsiv","Arsiv"]];

  function durumPaneli() {
    var slug = slugAl();
    if (!slug) return uyari("Once bir ilan sayfasi ac.", true);
    var u = urunler[slug] || {};
    kutuAc("Durum ve kategori",
      '<label style="display:block;margin-block-end:.9rem">Durum<br>' +
        '<select id="vo-d-durum" style="inline-size:100%;min-block-size:44px;padding:.5rem">' +
        DURUMLAR.map(function (d) {
          return '<option value="' + d[0] + '"' + (u.durum === d[0] ? " selected" : "") + ">" + d[1] + "</option>";
        }).join("") + "</select></label>" +
      '<label style="display:block;margin-block-end:.9rem">Teklife acik<br>' +
        '<input type="checkbox" id="vo-d-pazarlik"' + (u.pazarlik ? " checked" : "") + "></label>" +
      '<label style="display:block">Fiyati sitede gizle<br>' +
        '<input type="checkbox" id="vo-d-gizli"' + (u.fiyat_gizli ? " checked" : "") + "></label>",
      function (kutu) {
        var yama = {
          durum: kutu.querySelector("#vo-d-durum").value,
          pazarlik: kutu.querySelector("#vo-d-pazarlik").checked,
          fiyat_gizli: kutu.querySelector("#vo-d-gizli").checked
        };
        return sb.from("ilanlar").update(yama).eq("slug", slug).then(function (c) {
          if (c.error) { uyari(c.error.message, true); return false; }
          Object.assign(urunler[slug] = urunler[slug] || {}, yama);
          bekleyen++; cubukCiz(); uyari("Durum kaydedildi.");
          return true;
        });
      });
  }

  /* ----------------------------------------------------------- gorsel paneli */
  function gorselPaneli() {
    var slug = slugAl();
    if (!slug) return uyari("Once bir ilan sayfasi ac.", true);
    var u = urunler[slug];
    if (!u) return uyari("Ilan veritabaninda bulunamadi.", true);

    sb.from("kareler").select("*").eq("ilan_id", u.id).order("sira").then(function (c) {
      var kareler = c.data || [];
      kutuAc("Gorseller", '<div id="vo-kareler" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:.6rem"></div>' +
        '<p style="margin-block-start:1rem"><label style="cursor:pointer;text-decoration:underline">Fotograf ekle' +
        '<input type="file" id="vo-yukle" accept="image/*" multiple hidden></label></p>' +
        '<p id="vo-yukleme" style="font-size:.8125rem;color:#5C5A50"></p>', null, function (kutu) {
        function ciz() {
          kutu.querySelector("#vo-kareler").innerHTML = kareler.map(function (k, i) {
            return '<figure style="margin:0;border:1px solid #E0DDCC;position:relative">' +
              (i === 0 ? '<span class="vo-rozet">Kapak</span>' : "") +
              '<img src="' + gorselAdres(k.yol) + '" alt="" style="inline-size:100%;aspect-ratio:1;object-fit:cover;display:block">' +
              '<div style="display:flex;gap:.2rem;padding:.3rem">' +
                (i > 0 ? '<button data-yukari="' + k.id + '" style="flex:1;min-block-size:32px">&#8592;</button>' : "") +
                (i < kareler.length - 1 ? '<button data-asagi="' + k.id + '" style="flex:1;min-block-size:32px">&#8594;</button>' : "") +
                '<button data-sil="' + k.id + '" style="flex:1;min-block-size:32px;color:#8E2B22">Sil</button>' +
              "</div></figure>";
          }).join("") || "<p>Bu ilanda gorsel yok.</p>";

          kutu.querySelectorAll("[data-yukari],[data-asagi]").forEach(function (b) {
            b.onclick = function () {
              var id = Number(b.dataset.yukari || b.dataset.asagi);
              var i = kareler.findIndex(function (k) { return k.id === id; });
              var j = b.dataset.yukari ? i - 1 : i + 1;
              var t = kareler[i]; kareler[i] = kareler[j]; kareler[j] = t;
              siraYaz(kareler).then(ciz);
            };
          });
          kutu.querySelectorAll("[data-sil]").forEach(function (b) {
            b.onclick = function () {
              var id = Number(b.dataset.sil);
              var k = kareler.find(function (x) { return x.id === id; });
              sb.from("kareler").delete().eq("id", id).then(function () {
                if (k) sb.storage.from("gorseller").remove([k.yol]);
                kareler = kareler.filter(function (x) { return x.id !== id; });
                siraYaz(kareler).then(ciz);
                bekleyen++; cubukCiz();
              });
            };
          });
        }
        ciz();

        kutu.querySelector("#vo-yukle").onchange = function (e) {
          var dosyalar = [].slice.call(e.target.files), n = 0;
          var not = kutu.querySelector("#vo-yukleme");
          (function sonraki() {
            if (!dosyalar.length) {
              not.textContent = n + " gorsel eklendi. Sitede gorunmesi icin Yayinla.";
              bekleyen += n; cubukCiz(); ciz(); return;
            }
            var d = dosyalar.shift();
            not.textContent = "Yukleniyor: " + d.name;
            var uz = (d.name.split(".").pop() || "jpg").toLowerCase();
            var yol = slug + "/" + Date.now() + "-" + Math.random().toString(36).slice(2, 8) + "." + uz;
            sb.storage.from("gorseller").upload(yol, d, { cacheControl: "31536000" }).then(function (r) {
              if (r.error) { uyari(d.name + ": " + r.error.message, true); return sonraki(); }
              sb.from("kareler").insert({
                ilan_id: u.id, sira: kareler.length + 1,
                rol: kareler.length === 0 ? "tam" : "detay", yol: yol, kaynak: "orijinal"
              }).select().single().then(function (c2) {
                if (c2.data) { kareler.push(c2.data); n++; }
                sonraki();
              });
            });
          })();
        };
      });
    });
  }

  function siraYaz(kareler) {
    var isler = kareler.map(function (k, i) {
      k.sira = i + 1;
      return sb.from("kareler").update({ sira: i + 1 }).eq("id", k.id);
    });
    return Promise.all(isler);
  }

  function gorselAdres(yol) {
    return sb.storage.from("gorseller").getPublicUrl(yol, {
      transform: { width: 300, height: 300, resize: "contain" }
    }).data.publicUrl;
  }

  /* ------------------------------------------------------------------ kutu */
  function kutuAc(baslik, icerik, kaydet, hazir) {
    var d = document.createElement("dialog");
    d.style.cssText = "border:1px solid #E0DDCC;padding:1.5rem;max-inline-size:min(680px,94vw);" +
      "font-family:'Instrument',ui-sans-serif,system-ui,sans-serif;background:#fff";
    d.innerHTML = '<h2 style="margin:0 0 1rem;font-family:Crimson,serif;font-weight:500">' + baslik + "</h2>" +
      '<div id="vo-govde">' + icerik + "</div>" +
      '<div style="display:flex;gap:.5rem;justify-content:flex-end;margin-block-start:1.25rem">' +
        '<button value="kapat" style="min-block-size:44px;padding:.5rem 1rem;border:1px solid #8A8779;background:#fff;cursor:pointer">Kapat</button>' +
        (kaydet ? '<button value="kaydet" style="min-block-size:44px;padding:.5rem 1rem;border:1px solid #222;background:#222;color:#F4F2E3;cursor:pointer">Kaydet</button>' : "") +
      "</div>";
    document.body.appendChild(d);
    d.showModal();
    if (hazir) hazir(d);
    d.addEventListener("click", function (e) {
      var b = e.target.closest("button[value]");
      if (!b) return;
      if (b.value === "kaydet" && kaydet) {
        Promise.resolve(kaydet(d)).then(function (ok) { if (ok !== false) { d.close(); d.remove(); } });
      } else { d.close(); d.remove(); }
    });
  }

  /* ------------------------------------------------------------- kampanya */
  function kampanyaPaneli() {
    sb.from("kampanyalar").select("*").order("oncelik", { ascending: false }).then(function (c) {
      if (c.error) return uyari("Kampanya tablosu yok. 04_kampanya.sql dosyasini calistir.", true);
      var liste = c.data || [];
      var govde = liste.length ? liste.map(function (k) {
        return '<div style="border:1px solid #E0DDCC;padding:.75rem;margin-block-end:.6rem;' +
          'display:flex;gap:.75rem;align-items:center;flex-wrap:wrap">' +
          '<b style="font-weight:500;flex:1">' + metin(k.ad) + '</b>' +
          '<span style="font-size:.8125rem;color:#5C5A50">' +
            (k.tur === "yuzde" ? k.deger + "%" : "-" + k.deger) + " &middot; " +
            (k.kapsam === "hepsi" ? "butun koleksiyon" : k.kapsam) + "</span>" +
          '<label style="display:flex;gap:.35rem;align-items:center;font-size:.8125rem">' +
            '<input type="checkbox" data-k-aktif="' + k.id + '"' + (k.aktif ? " checked" : "") + '>Acik</label>' +
          '<label style="display:flex;gap:.35rem;align-items:center;font-size:.8125rem">' +
            '<input type="checkbox" data-k-serit="' + k.id + '"' + (k.serit_aktif ? " checked" : "") + '>Serit</label>' +
          "</div>";
      }).join("") : "<p>Henuz kampanya yok.</p>";

      kutuAc("Kampanyalar", govde +
        '<p style="font-size:.8125rem;color:#5C5A50;margin-block-start:.75rem">' +
        'Yeni kampanya acmak, kapsam ve tarih vermek icin Gelismis > Kampanyalar.</p>',
        null, function (kutu) {
          kutu.querySelectorAll("[data-k-aktif],[data-k-serit]").forEach(function (el) {
            el.onchange = function () {
              var id = Number(el.dataset.kAktif || el.dataset.kSerit);
              var yama = el.dataset.kAktif ? { aktif: el.checked } : { serit_aktif: el.checked };
              sb.from("kampanyalar").update(yama).eq("id", id).then(function (r) {
                if (r.error) return uyari(r.error.message, true);
                bekleyen++; cubukCiz();
                uyari("Kampanya guncellendi. Fiyatlarin degismesi icin Yayinla.");
              });
            };
          });
        });
    });
  }

  function metin(t) {
    var d = document.createElement("span");
    d.textContent = t == null ? "" : String(t);
    return d.innerHTML;
  }

  /* --------------------------------------------------------------- yayinla */
  function yayinla() {
    sb.from("yayin_istek").insert({ mesaj: "Site uzerinden istendi" }).then(function (c) {
      if (c.error) return uyari(c.error.message, true);
      bekleyen = 0; cubukCiz();
      uyari("Yayin siraya alindi. Site birkac dakika icinde guncellenir.");
    });
  }

  /* ------------------------------------------------------------- baslangic */
  function urunleriCek() {
    return sb.from("ilanlar")
      .select("id,slug,baslik,sanatci,donem,aciklama,fiyat,fiyat_gizli,para_birimi,durum,pazarlik")
      .then(function (c) {
        (c.data || []).forEach(function (r) { urunler[r.slug] = r; });
      });
  }

  import("https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm").then(function (mod) {
    sb = mod.createClient(window.VO_AYAR.URL, window.VO_AYAR.ANAHTAR);
    return sb.auth.getSession();
  }).then(function (c) {
    if (!c || !c.data || !c.data.session) return;
    return sb.from("profiller").select("rol,ad").eq("id", c.data.session.user.id).single();
  }).then(function (c) {
    if (!c || !c.data || (c.data.rol !== "sahip" && c.data.rol !== "yonetici")) return;
    profil = c.data;
    stilKur();
    return urunleriCek();
  }).then(function () {
    if (!profil) return;
    cubukCiz();
    window.addEventListener("hashchange", function () {
      if (duzenle) setTimeout(alanlariBagla, 60);
    });
    var g = new MutationObserver(function () { if (duzenle) alanlariBagla(); });
    g.observe(document.body, { childList: true, subtree: true });
  }).catch(function (e) {
    if (window.console) console.warn("[vo] duzenleme katmani acilmadi:", e);
  });
})();
