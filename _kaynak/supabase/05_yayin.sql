-- Yayin isteklerinin durumunu guncelleme yetkisi.
--
-- GitHub Actions is akisi yayinci hesabiyla giris yapip istekleri
-- 'sirada' -> 'calisiyor' -> 'bitti' diye ilerletir. Update kurali
-- olmadan RLS bunu sessizce engeller ve istek sonsuza kadar sirada
-- kalir; site her bes dakikada bir bosuna yeniden uretilir.

drop policy if exists yayin_guncelle on yayin_istek;
create policy yayin_guncelle on yayin_istek for update to authenticated
  using (duzenleyebilir()) with check (duzenleyebilir());

-- Sirada takilip kalmis eski istekleri temizle (varsa).
update yayin_istek set durum = 'hata', bitti = now()
 where durum in ('sirada', 'calisiyor')
   and istendi < now() - interval '2 hours';
