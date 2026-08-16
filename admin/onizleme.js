/* Onizleme modu.
 *
 * Supabase henuz baglanmamissa panel bu dosyadaki sahte istemciyle calisir:
 * gercek 270 ilan ve 879 gorselle, gercek ekranlarla, ama salt okunur.
 * Amaci paneli Supabase kurulmadan once gozle gormek. Kaydetme, silme,
 * yukleme ve yayinlama bu modda calismaz.
 *
 * config.js doldurulunca bu dosya devreye girmez.
 */
(function () {
  const baglandi = window.VO && window.VO.URL && !String(window.VO.URL).startsWith("BURAYA");
  if (baglandi) return;


  /* ------------------------------------------------------------------ kilit
   * Supabase baglanana kadar panele bir sifre kapisi koyuyoruz. Bunun ne
   * oldugunu acikca soyleyelim: bu bir PERDE, kilit degil. Denetim tarayicida
   * yapiliyor, yani bilen biri gecebilir. Arkasinda gizli veri de yok; ayni 270
   * ilan zaten sitede herkese acik ve bu ekran hicbir sey kaydetmiyor.
   * Gercek kilit Supabase baglandiginda gelir: sifre orada durur, denetim
   * sunucuda yapilir, her kullanicinin kendi hesabi olur.
   */
  var SIFRE_OZETI = "6bafea4cc4988c9e56968eeda677c352914bcf2a724af75bdb663ae9cab27d82";
  var ANAHTAR = "vo-onizleme-acik";

  function ozet(metin) {
    var veri = new TextEncoder().encode(metin);
    return crypto.subtle.digest("SHA-256", veri).then(function (b) {
      return Array.from(new Uint8Array(b))
        .map(function (x) { return x.toString(16).padStart(2, "0"); }).join("");
    });
  }

  function acikMi() {
    try { return sessionStorage.getItem(ANAHTAR) === "1"; } catch (e) { return false; }
  }

  const yuklendi = fetch("onizleme.json").then(r => r.json());
  const hataCevap = {
    data: null,
    error: { message: "Onizleme modu: veritabani bagli degil, degisiklik kaydedilmez." }
  };

  function suz(satirlar, kosullar) {
    return satirlar.filter(r => kosullar.every(k => {
      if (k.tur === "eq") return String(r[k.alan]) === String(k.deger);
      if (k.tur === "in") return k.deger.includes(String(r[k.alan]));
      if (k.tur === "or") {
        return k.deger.split(",").some(p => {
          const [alan, op, ...kalan] = p.split(".");
          const ara = kalan.join(".").replace(/%/g, "").toLowerCase();
          return op === "ilike" && String(r[alan] ?? "").toLowerCase().includes(ara);
        });
      }
      return true;
    }));
  }

  function Sorgu(tablo) {
    const durum = { tablo, kosul: [], sira: null, bas: 0, son: 999999, tek: false, sayim: false };
    const nesne = {
      select(_c, o) { if (o && o.count) durum.sayim = true; return nesne; },
      eq(a, v) { durum.kosul.push({ tur: "eq", alan: a, deger: v }); return nesne; },
      in(a, v) { durum.kosul.push({ tur: "in", alan: a, deger: v.map(String) }); return nesne; },
      or(s) { durum.kosul.push({ tur: "or", deger: s }); return nesne; },
      order(a, o) { durum.sira = { alan: a, artan: !o || o.ascending !== false }; return nesne; },
      range(a, b) { durum.bas = a; durum.son = b; return nesne; },
      limit(n) { durum.son = durum.bas + n - 1; return nesne; },
      single() { durum.tek = true; return nesne; },
      maybeSingle() { durum.tek = true; return nesne; },
      insert() { return sahteYazma(); },
      update() { return sahteYazma(); },
      delete() { return sahteYazma(); },
      upsert() { return sahteYazma(); },
      then(coz) {
        return yuklendi.then(veri => {
          let satir = (veri[durum.tablo] || []).slice();
          satir = suz(satir, durum.kosul);
          if (durum.tablo === "ilanlar") {
            satir = satir.map(r => ({ ...r, kareler: (veri.kareler || []).filter(k => k.ilan_id === r.id) }));
          }
          if (durum.sira) {
            const { alan, artan } = durum.sira;
            satir.sort((a, b) => {
              const x = a[alan], y = b[alan];
              if (x == null) return 1;
              if (y == null) return -1;
              return (x > y ? 1 : x < y ? -1 : 0) * (artan ? 1 : -1);
            });
          }
          const sayim = satir.length;
          satir = satir.slice(durum.bas, durum.son + 1);
          coz(durum.tek
            ? { data: satir[0] || null, error: satir.length ? null : { message: "kayit yok" } }
            : { data: satir, error: null, count: durum.sayim ? sayim : null });
        });
      },
    };
    function sahteYazma() {
      const y = {
        select: () => y, single: () => y, eq: () => y, in: () => y,
        then(coz) { coz(hataCevap); return Promise.resolve(hataCevap); },
      };
      return y;
    }
    return nesne;
  }

  window.__VO_SB = {
    from: t => Sorgu(t),
    storage: {
      from() {
        return {
          getPublicUrl(yol) { return { data: { publicUrl: "../" + yol + "-c.webp" } }; },
          upload() { return Promise.resolve({ error: hataCevap.error }); },
          remove() { return Promise.resolve({ error: hataCevap.error }); },
        };
      },
    },
    auth: {
      getSession: function () {
        return Promise.resolve({
          data: { session: acikMi() ? { user: { id: "onizleme" } } : null }
        });
      },
      signInWithPassword: function (g) {
        return ozet(String((g && g.password) || "")).then(function (h) {
          if (h !== SIFRE_OZETI) {
            return { error: { message: "Sifre dogru degil." } };
          }
          try { sessionStorage.setItem(ANAHTAR, "1"); } catch (e) {}
          return { error: null };
        });
      },
      signOut: function () {
        try { sessionStorage.removeItem(ANAHTAR); } catch (e) {}
        return Promise.resolve({});
      },
      resetPasswordForEmail: function () {
        return Promise.resolve({ error: { message:
          "Onizleme sifresi sabittir. Supabase baglaninca kendi sifreni belirleyeceksin." } });
      },
      onAuthStateChange: () => ({ data: { subscription: { unsubscribe() {} } } }),
    },
    ONIZLEME: true,
  };
})();
