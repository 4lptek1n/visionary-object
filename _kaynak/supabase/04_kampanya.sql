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
