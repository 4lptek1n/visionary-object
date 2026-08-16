-- ============================================================================
--  VISIONARY OBJECT - VERITABANI KURULUMU
--  Supabase > SQL Editor'e bunu yapistir ve RUN'a bas. Tek seferde biter.
--  Sonuc "Success" yazmali.
-- ============================================================================


-- ----------------------------------------------------------------------------
-- 01_semasi.sql
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- 02_guvenlik.sql
-- ----------------------------------------------------------------------------
-- Visionary Object - erisim kurallari (RLS)
-- 01_semasi.sql'den sonra calistir.
--
-- Mantik: giris yapmamis kimse hicbir seyi goremez. Giris yapmis herkesin bir
-- profili vardir; rolu 'sahip' ya da 'yonetici' ise ilan, gorsel, sayfa ve
-- ayarlarin tamamini duzenleyebilir. Kullanici acip silmeyi yalnizca 'sahip'
-- yapabilir. Site zaten statik uretildigi icin ziyaretcinin veritabanina
-- hic dokunmasi gerekmez.

alter table profiller      enable row level security;
alter table ilanlar        enable row level security;
alter table kareler        enable row level security;
alter table sayfalar       enable row level security;
alter table ayarlar        enable row level security;
alter table sanatcilar     enable row level security;
alter table yayin_istek    enable row level security;
alter table degisiklik_log enable row level security;

-- Rol okuma yardimcisi. security definer, cunku profiller uzerinde RLS var.
create or replace function benim_rolum()
returns text language sql stable security definer set search_path = public as $$
  select rol from profiller where id = auth.uid()
$$;

create or replace function duzenleyebilir()
returns boolean language sql stable security definer set search_path = public as $$
  select coalesce(benim_rolum() in ('sahip','yonetici'), false)
$$;

create or replace function sahip_mi()
returns boolean language sql stable security definer set search_path = public as $$
  select coalesce(benim_rolum() = 'sahip', false)
$$;

-- ---------------------------------------------------------------- profiller
drop policy if exists profil_oku on profiller;
create policy profil_oku on profiller for select to authenticated
  using (id = auth.uid() or sahip_mi());

drop policy if exists profil_kendi_guncelle on profiller;
create policy profil_kendi_guncelle on profiller for update to authenticated
  using (id = auth.uid()) with check (id = auth.uid() and rol = benim_rolum());

drop policy if exists profil_sahip_guncelle on profiller;
create policy profil_sahip_guncelle on profiller for update to authenticated
  using (sahip_mi()) with check (sahip_mi());

drop policy if exists profil_sahip_sil on profiller;
create policy profil_sahip_sil on profiller for delete to authenticated
  using (sahip_mi() and id <> auth.uid());

-- ------------------------------------- ilanlar, kareler, sayfalar, ayarlar, sanatcilar
do $$
declare t text;
begin
  foreach t in array array['ilanlar','kareler','sayfalar','ayarlar','sanatcilar'] loop
    execute format('drop policy if exists %I_oku on %I', t, t);
    execute format('create policy %I_oku on %I for select to authenticated using (true)', t, t);

    execute format('drop policy if exists %I_ekle on %I', t, t);
    execute format('create policy %I_ekle on %I for insert to authenticated with check (duzenleyebilir())', t, t);

    execute format('drop policy if exists %I_guncelle on %I', t, t);
    execute format('create policy %I_guncelle on %I for update to authenticated using (duzenleyebilir()) with check (duzenleyebilir())', t, t);

    execute format('drop policy if exists %I_sil on %I', t, t);
    execute format('create policy %I_sil on %I for delete to authenticated using (duzenleyebilir())', t, t);
  end loop;
end $$;

-- ------------------------------------------------------------- yayin istegi
drop policy if exists yayin_oku on yayin_istek;
create policy yayin_oku on yayin_istek for select to authenticated using (true);

drop policy if exists yayin_ekle on yayin_istek;
create policy yayin_ekle on yayin_istek for insert to authenticated
  with check (duzenleyebilir());

-- ------------------------------------------------------------------- log
drop policy if exists log_oku on degisiklik_log;
create policy log_oku on degisiklik_log for select to authenticated using (true);

-- ------------------------------------------------------- baslangic ayarlari
insert into ayarlar (anahtar, deger, aciklama) values
  ('marka',   '{"ad":"Visionary Object","slogan":"One-of-a-kind antique art, direct from the collector"}'::jsonb, 'Site adi ve slogan'),
  ('iletisim','{"eposta":"","telefon":"","instagram":""}'::jsonb, 'Iletisim bilgileri'),
  ('konum',   '{"bolge":"Virginia","ulke":"US","gorunen":"Virginia, United States"}'::jsonb, 'Item Location filtresinde gorunur'),
  ('para',    '{"birim":"USD","simge":"$"}'::jsonb, 'Fiyat para birimi'),
  ('fiyat_politikasi','{"varsayilan_gizli":true,"gizli_metin":"Price Upon Request"}'::jsonb,
   'Fiyat girilmemis ya da gizli isaretlenmis ilanlarda gorunecek metin')
on conflict (anahtar) do nothing;

insert into sayfalar (anahtar, baslik) values
  ('anasayfa','Home'), ('hakkinda','About'), ('kargo','Shipping & Delivery'),
  ('iade','Returns'), ('gizlilik','Privacy'), ('sartlar','Terms')
on conflict (anahtar) do nothing;

-- ----------------------------------------------------------------------------
-- 03_depolama.sql
-- ----------------------------------------------------------------------------
-- Visionary Object - gorsel deposu
-- 02_guvenlik.sql'den sonra calistir.
--
-- Panelden yuklenen her fotograf buraya duser. Site kurulurken GitHub Actions
-- bu dosyalari indirip 190/640/1400 px webp uretir; ziyaretci hicbir zaman
-- Supabase'e baglanmaz, sadece statik webp gorur.

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('gorseller', 'gorseller', true, 52428800,
        array['image/jpeg','image/png','image/webp','image/heic','image/heif','image/tiff'])
on conflict (id) do update
  set public = true,
      file_size_limit = 52428800,
      allowed_mime_types = excluded.allowed_mime_types;

drop policy if exists gorsel_herkes_okur on storage.objects;
create policy gorsel_herkes_okur on storage.objects for select
  using (bucket_id = 'gorseller');

drop policy if exists gorsel_yukle on storage.objects;
create policy gorsel_yukle on storage.objects for insert to authenticated
  with check (bucket_id = 'gorseller' and duzenleyebilir());

drop policy if exists gorsel_guncelle on storage.objects;
create policy gorsel_guncelle on storage.objects for update to authenticated
  using (bucket_id = 'gorseller' and duzenleyebilir());

drop policy if exists gorsel_sil on storage.objects;
create policy gorsel_sil on storage.objects for delete to authenticated
  using (bucket_id = 'gorseller' and duzenleyebilir());

-- ----------------------------------------------------------------------------
-- 04_kampanya.sql
-- ----------------------------------------------------------------------------
-- Visionary Object - kampanyalar
-- 03_depolama.sql'den sonra calistir.
--
-- Bir kampanya sunlari soyler: kime uygulanacak (kapsam), ne kadar indirim
-- (yuzde ya da tutar), ne zaman gecerli (baslangic - bitis) ve sitede ne yazacak
-- (rozet ve serit metni).
--
-- Fiyat hesabi panelde degil, site uretilirken yapilir. Boylece ziyaretcinin
-- gordugu fiyat statik dosyada durur; sayfa acilirken hicbir hesap donmez.

create table if not exists kampanyalar (
  id            bigint generated always as identity primary key,
  ad            text not null,
  aciklama      text default '',

  tur           text not null default 'yuzde' check (tur in ('yuzde','tutar')),
  deger         numeric not null check (deger > 0),

  kapsam        text not null default 'hepsi'
                check (kapsam in ('hepsi','kategori','sanatci','secili')),
  kapsam_deger  jsonb not null default '[]'::jsonb,

  baslangic     timestamptz,
  bitis         timestamptz,
  aktif         boolean not null default false,

  rozet         text default '',        -- urun uzerinde gorunen kisa etiket
  serit_metin   text default '',        -- sitenin en ustundeki serit
  serit_etiket  text default '',        -- seritteki kucuk buyuk-harf etiket
  serit_aktif   boolean not null default false,

  oncelik       integer not null default 0,
  en_dusuk      numeric,                -- bu fiyatin altina inme
  olusturuldu   timestamptz not null default now(),
  guncellendi   timestamptz not null default now(),
  guncelleyen   uuid references auth.users
);
create index if not exists kampanya_aktif_idx on kampanyalar (aktif, oncelik desc);

comment on column kampanyalar.kapsam_deger is
  'kapsam=kategori ise ["tablo","obje"]; sanatci ise ["Tarkay"]; secili ise ["ilan-59"]';
comment on column kampanyalar.en_dusuk is
  'Indirim sonrasi fiyat bunun altina dusmez. Bos birakilabilir.';

drop trigger if exists kampanya_guncelle on kampanyalar;
create trigger kampanya_guncelle before update on kampanyalar
  for each row execute function guncellendi_yaz();

drop trigger if exists kampanya_log on kampanyalar;
create trigger kampanya_log after insert or update or delete on kampanyalar
  for each row execute function log_yaz();

alter table kampanyalar enable row level security;

drop policy if exists kampanya_oku on kampanyalar;
create policy kampanya_oku on kampanyalar for select to authenticated using (true);

drop policy if exists kampanya_ekle on kampanyalar;
create policy kampanya_ekle on kampanyalar for insert to authenticated
  with check (duzenleyebilir());

drop policy if exists kampanya_guncelle_p on kampanyalar;
create policy kampanya_guncelle_p on kampanyalar for update to authenticated
  using (duzenleyebilir()) with check (duzenleyebilir());

drop policy if exists kampanya_sil on kampanyalar;
create policy kampanya_sil on kampanyalar for delete to authenticated
  using (duzenleyebilir());

-- Ornek: kapali durumda bir yaz kampanyasi. Panelden acilir.
insert into kampanyalar (ad, tur, deger, kapsam, rozet, serit_metin, serit_etiket, oncelik)
select 'Yaz secmeleri', 'yuzde', 15, 'hepsi', 'Summer selection',
       'Fifteen percent off the whole collection until the end of the month',
       'Summer', 10
where not exists (select 1 from kampanyalar);
