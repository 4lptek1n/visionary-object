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
      getSession: () => Promise.resolve({ data: { session: { user: { id: "onizleme" } } } }),
      signInWithPassword: () => Promise.resolve({ error: null }),
      signOut: () => Promise.resolve({}),
      resetPasswordForEmail: () => Promise.resolve({ error: hataCevap.error }),
      onAuthStateChange: () => ({ data: { subscription: { unsubscribe() {} } } }),
    },
    ONIZLEME: true,
  };
})();
