-- ============================================================================
--  DEMO YONETICI HESABI
--  KUR.sql ve VERI.sql'den sonra calistir.
--
--  Bu hesap gecicidir. Musteriye teslimde silinir ya da sifresi degistirilir:
--    Supabase > Authentication > Users > ... > Delete user
--  Sifre degistirmek icin panelde "Sifremi unuttum" ya da ayni ekrandan
--  "Send password recovery".
-- ============================================================================

do $$
declare
  kimlik uuid := gen_random_uuid();
  eposta text := 'demo@thetimesfigures.com';
  sifre  text := 'VisionaryDemo2026';
begin
  if exists (select 1 from auth.users where email = eposta) then
    -- Hesap zaten varsa sifreyi tazele, kopya olusturma.
    update auth.users
       set encrypted_password = extensions.crypt(sifre, extensions.gen_salt('bf')),
           email_confirmed_at = now(),
           updated_at = now()
     where email = eposta;
    raise notice 'Var olan demo hesabinin sifresi yenilendi.';
    return;
  end if;

  insert into auth.users (
    instance_id, id, aud, role, email, encrypted_password,
    email_confirmed_at, created_at, updated_at,
    raw_app_meta_data, raw_user_meta_data,
    confirmation_token, email_change, email_change_token_new, recovery_token
  ) values (
    '00000000-0000-0000-0000-000000000000', kimlik, 'authenticated', 'authenticated',
    eposta, extensions.crypt(sifre, extensions.gen_salt('bf')),
    now(), now(), now(),
    '{"provider":"email","providers":["email"]}'::jsonb,
    '{"ad":"Demo yonetici"}'::jsonb,
    '', '', '', ''
  );

  -- GoTrue e-posta girisi icin kimlik satirini da bekler.
  begin
    insert into auth.identities (
      id, user_id, identity_data, provider, provider_id,
      last_sign_in_at, created_at, updated_at
    ) values (
      gen_random_uuid(), kimlik,
      jsonb_build_object('sub', kimlik::text, 'email', eposta),
      'email', kimlik::text, now(), now(), now()
    );
  exception when undefined_column then
    insert into auth.identities (
      id, user_id, identity_data, provider, last_sign_in_at, created_at, updated_at
    ) values (
      gen_random_uuid(), kimlik,
      jsonb_build_object('sub', kimlik::text, 'email', eposta),
      'email', now(), now(), now()
    );
  end;

  raise notice 'Demo hesabi acildi.';
end $$;

-- Panele erisim profilden gelir. Ilk kullanici sahip olur.
insert into profiller (id, eposta, ad, rol)
select u.id, u.email, 'Demo yonetici', 'sahip'
from auth.users u
where u.email = 'demo@thetimesfigures.com'
on conflict (id) do update set rol = 'sahip', ad = 'Demo yonetici';

select p.eposta, p.rol, p.olusturuldu
from profiller p
join auth.users u on u.id = p.id
where u.email = 'demo@thetimesfigures.com';
