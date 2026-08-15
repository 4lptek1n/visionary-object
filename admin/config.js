/* Visionary Object - panel ayarlari
 *
 * Bu iki degeri Supabase panelinden alip buraya yapistir:
 *   Supabase > Project Settings > Data API
 *     Project URL   -> URL
 *     anon public   -> ANAHTAR
 *
 * Bu iki deger gizli degildir; tarayiciya inmesi normaldir. Veriyi koruyan sey
 * veritabanindaki erisim kurallari (RLS), bu anahtar degil. Gizli olan
 * service_role anahtarini buraya ASLA yazma; o yalnizca GitHub Secrets'ta durur.
 */
window.VO = {
  URL: "BURAYA_PROJE_URL",
  ANAHTAR: "BURAYA_ANON_ANAHTAR",
  SITE: "https://thetimesfigures.com"
};
