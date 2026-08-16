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
