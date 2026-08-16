-- Visionary Object - veritabani semasi
-- Supabase > SQL Editor icinde bastan sona calistir. Bir kez.
--
-- Tasarim notu: sitedeki her alan burada bir sutun. Panelden degistirilen sey
-- once buraya yazilir, site sonra bundan uretilir. Tek dogru kaynak burasidir.

create extension if not exists "pgcrypto";

-- ---------------------------------------------------------------- kullanicilar
-- auth.users Supabase'in kendi tablosu. Rolu burada tutuyoruz.
create table if not exists profiller (
  id          uuid primary key references auth.users on delete cascade,
  eposta      text not null,
  ad          text,
  rol         text not null default 'yonetici'
              check (rol in ('sahip','yonetici','okur')),
  son_giris   timestamptz,
  olusturuldu timestamptz not null default now()
);
comment on table profiller is 'sahip: her sey + kullanici yonetimi. yonetici: her sey. okur: sadece bakar.';

-- Yeni kullanici acildiginda profil kendiliginden olussun.
create or replace function profil_ac()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into profiller (id, eposta, ad, rol)
  values (new.id, new.email, coalesce(new.raw_user_meta_data->>'ad', split_part(new.email,'@',1)),
          case when (select count(*) from profiller) = 0 then 'sahip' else 'yonetici' end)
  on conflict (id) do nothing;
  return new;
end $$;

drop trigger if exists profil_ac_tetik on auth.users;
create trigger profil_ac_tetik after insert on auth.users
  for each row execute function profil_ac();

-- ---------------------------------------------------------------------- ilanlar
create table if not exists ilanlar (
  id            bigint generated always as identity primary key,
  no            integer not null unique,
  slug          text not null unique,
  kat           text not null default 'tablo'
                check (kat in ('tablo','obje','belge','rugs','lighting','sculpture')),
  durum         text not null default 'taslak'
                check (durum in ('taslak','yayinda','rezerve','satildi','arsiv')),

  baslik        text not null default '',
  aciklama      text not null default '',
  sanatci       text not null default '',
  eser_adi      text not null default '',
  donem         text not null default '',
  teknik        text not null default '',
  baski         text not null default '',
  ref           text not null default '',
  galeri_adi    text not null default '',
  etiket        text not null default '',
  biyografi     text not null default '',
  aciklama_not  text not null default '',
  belge         text not null default '',
  kaynak_dosya  text not null default '',

  olcu_w        numeric,
  olcu_h        numeric,
  olcu_d        numeric,
  olcu_nesi     text default 'outside of frame',
  agirlik_lb    numeric,

  fiyat         numeric,
  fiyat_eski    numeric,
  para_birimi   text not null default 'USD',
  fiyat_gizli   boolean not null default true,
  pazarlik      boolean not null default true,

  facet         jsonb not null default '{"subject":[],"medium":[],"style":[],"framing":[],"period":"","color":[]}'::jsonb,
  seo_baslik    text default '',
  seo_aciklama  text default '',
  one_cikan     boolean not null default false,
  sira          integer,

  olusturuldu   timestamptz not null default now(),
  guncellendi   timestamptz not null default now(),
  guncelleyen   uuid references auth.users
);
create index if not exists ilanlar_durum_idx on ilanlar (durum);
create index if not exists ilanlar_kat_idx   on ilanlar (kat);
create index if not exists ilanlar_ara_idx   on ilanlar
  using gin (to_tsvector('simple', coalesce(baslik,'') || ' ' || coalesce(sanatci,'') || ' ' || coalesce(aciklama,'')));

-- ---------------------------------------------------------------------- kareler
create table if not exists kareler (
  id          bigint generated always as identity primary key,
  ilan_id     bigint not null references ilanlar on delete cascade,
  sira        integer not null default 1,      -- 1 = kapak
  rol         text not null default 'detay'
              check (rol in ('tam','aci','detay','imza','sertifika','etiket','plaka','arka','olcu')),
  yol         text not null,                   -- storage icindeki yol
  w           integer,
  h           integer,
  alt_metin   text default '',
  kaynak      text default 'orijinal',
  olusturuldu timestamptz not null default now()
);
create index if not exists kareler_ilan_idx on kareler (ilan_id, sira);

-- --------------------------------------------------------------------- sayfalar
-- Sitedeki sabit metinler: ana sayfa, hakkinda, kargo, iade, gizlilik.
create table if not exists sayfalar (
  anahtar     text primary key,
  baslik      text not null default '',
  icerik      text not null default '',
  seo_baslik  text default '',
  seo_aciklama text default '',
  guncellendi timestamptz not null default now(),
  guncelleyen uuid references auth.users
);

-- ---------------------------------------------------------------------- ayarlar
-- Marka adi, iletisim, konum, para birimi, ana sayfa vitrin secimi.
create table if not exists ayarlar (
  anahtar     text primary key,
  deger       jsonb not null,
  aciklama    text default '',
  guncellendi timestamptz not null default now()
);

-- -------------------------------------------------------------------- sanatcilar
create table if not exists sanatcilar (
  id          bigint generated always as identity primary key,
  ad          text not null unique,
  biyografi   text default '',
  dogum       text default '',
  olum        text default '',
  ulke        text default '',
  guncellendi timestamptz not null default now()
);

-- ------------------------------------------------------------------ yayin istegi
-- Panelde Yayinla'ya basilinca buraya satir dusER. GitHub Actions bunu gorup
-- siteyi yeniden uretir ve canliya alir. Boylece tarayicida hicbir gizli anahtar
-- tutulmaz.
create table if not exists yayin_istek (
  id          bigint generated always as identity primary key,
  durum       text not null default 'sirada'
              check (durum in ('sirada','calisiyor','bitti','hata')),
  isteyen     uuid references auth.users,
  mesaj       text default '',
  kayit       text default '',
  istendi     timestamptz not null default now(),
  basladi     timestamptz,
  bitti       timestamptz
);
create index if not exists yayin_durum_idx on yayin_istek (durum, istendi);

-- ------------------------------------------------------------------------- log
create table if not exists degisiklik_log (
  id          bigint generated always as identity primary key,
  tablo       text not null,
  kayit_id    text not null,
  islem       text not null,
  kim         uuid references auth.users,
  ne_zaman    timestamptz not null default now(),
  onceki      jsonb
);
create index if not exists log_zaman_idx on degisiklik_log (ne_zaman desc);

create or replace function guncellendi_yaz()
returns trigger language plpgsql as $$
begin
  new.guncellendi := now();
  new.guncelleyen := auth.uid();
  return new;
end $$;

drop trigger if exists ilanlar_guncelle on ilanlar;
create trigger ilanlar_guncelle before update on ilanlar
  for each row execute function guncellendi_yaz();

create or replace function log_yaz()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into degisiklik_log (tablo, kayit_id, islem, kim, onceki)
  values (tg_table_name,
          coalesce((to_jsonb(coalesce(new, old))->>'id'), '?'),
          tg_op, auth.uid(),
          case when tg_op = 'DELETE' then to_jsonb(old) else null end);
  return coalesce(new, old);
end $$;

drop trigger if exists ilanlar_log on ilanlar;
create trigger ilanlar_log after insert or update or delete on ilanlar
  for each row execute function log_yaz();
