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
