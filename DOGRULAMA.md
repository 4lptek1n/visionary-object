# Doğrulama raporu — localhost:8080 üzerinde

Site yerel HTTP sunucusunda çalıştırıldı (`python3 -m http.server 8080`) ve
tüm ölçümler `file://` değil **http://localhost** üzerinden alındı.

## 5 repo sözleşmesine göre bulunan ve kapatılan hatalar

| # | Bulgu | Kural | Yapılan |
|---|---|---|---|
| 1 | **CLS 0,837** | CLS < 0,1 | İki sebep vardı: `content-visibility:auto` footer'ı yeniden yerleştiriyordu, ve router `#app`'i doldurana kadar footer yukarıda duruyordu. `content-visibility` kaldırıldı, `#app{min-block-size:100dvh}` ile alan baştan ayrıldı. **CLS 0,0067** |
| 2 | Ana sayfada **8 bölüme 8 üst etiket** | her 3 bölüme 1 | Etiketler kaldırıldı, 1stDibs'in kendi bölüm adları (Shop by Category, See What's New, Now Trending, Trending Searches, Shop With Confidence) doğrudan `h2` yapıldı. **8 bölüm / 2 etiket** |
| 3 | Müzede **"ROOM I…V"** numaralı bölüm etiketi | numaralı etiket kesinlikle yasak | Roma rakamları kaldırıldı, oda adı ve adet kaldı |
| 4 | İlan sayfasında başlık sırası **h1 → h3** | atlamasız başlık sırası | Satın alma kolonundaki kart başlıkları `h2` yapıldı; koleksiyon sayfasına sonuç sayısı `h2` olarak eklendi |
| 5 | **35 görselde** iç boyut yok | her görselde `aspect-ratio` veya `width/height` | Küçük resim, benzer şerit, mini satır, öneri, alt kategori görsellerine `aspect-ratio`; büyük alanlara `contain-intrinsic-size` |
| 6 | Kap genişliği **1440 px** | 1240-1400 px | 1400 px |
| 7 | `74vh`, `64vh`, `58vh` | asla `vh`, daima `dvh` | Üçü de `dvh` |
| 8 | Rozet yazısı **`font-size:10px`** | üretimde `px` yok | `.625rem` |
| 9 | `will-change` **sürekli açık** | yalnız animasyon süresince | `[data-open]` durumuna bağlandı |
| 10 | Footer künye satırı **4,42:1** | gövde 4,5:1 | `--ink-3` yerine `--ink-2` → **5,78:1** |
| 11 | Bölüm dolgusu mobilde **64 px** | en az 96 px | `--band-m` → `clamp(6rem,7vw,9rem)` = 96-144 px |
| 12 | Hero'da **6 metin öğesi**, 29 kelimelik alt metin, düğme altında güven şeridi | en fazla 4 öğe, 20 kelime, düğme altına şerit konmaz | Güven şeridi kaldırıldı, alt metin **17 kelime**, **4 öğe** |
| 13 | Telefonda hero düğmesi **katlanın altında** | hero ilk ekrana sığar | Mobil görsel yüksekliği `min(34dvh,270px)`, ikincil düğme 560 px altında gizli. 375/390'da düğme görünür |
| 14 | Purchase Protection 4+2 kırık ızgara | üç eşit kart sırası yasak | 1440'ta 6 sütun tek sıra, altında 2 sütun |
| 15 | Favori/sepet rozeti erişilebilir ada karışıyordu | ikon düğmede `aria-label` | Rozet `aria-hidden`, üst öğenin adı "Favorites, 1 item" olarak güncelleniyor |

## Ölçülen değerler

**Performans** (localhost, tek dosya, gömülü görseller)

| Sayfa | Yükleme | LCP | CLS |
|---|---|---|---|
| Ana sayfa | 304 ms | 352 ms | 0,0067 |
| Kategori | 287 ms | 372 ms | 0,0067 |
| İlan | 268 ms | 324 ms | 0,0067 |
| Müze | 240 ms | 332 ms | 0,0067 |

Hedefler: LCP < 2,5 s ✓ · CLS < 0,1 ✓ · yükleme < 3 s ✓ · filtre etkileşimi 126 ms (INP < 200 ms) ✓

**Kontrast** — ekran görüntüsünün gerçek piksellerinden ölçüldü
(`color-mix`/`oklab` hesaplanmış değerleri okuyan denetimler yanlış alarm veriyordu):

| Yer | Oran |
|---|---|
| Editoryal bant başlığı, koyu zemin | 11,85:1 |
| Editoryal bant paragrafı | 8,79:1 |
| Müze hero metni, görsel üstü | 6,56:1 |
| Promo şeridi bağlantısı | 14,13:1 |
| İlan alt başlığı | 6,10:1 |
| Filtre adetleri, künye etiketleri | 4,71:1 |
| Footer künye satırı | 5,78:1 |

**Erişilebilirlik**
- 24 rota × 1920/1440/1024/768/375 px: yatay taşma 0, sayfa başına tek `h1`,
  `alt` eksiği 0, başlık atlaması 0, konsol hatası 0
- 26 sekme durağı: odak halkası eksiği **0**, görsel sıra sapması yok
  (tek "sapma" iki sütunlu şeridin sol sütunundan sağa geçiş, doğru okuma sırası)
- Kalıcı pencere: odak içeri giriyor, içeride kalıyor, Esc kapatıyor, odak tetikleyiciye dönüyor
- Adsız etkileşimli öğe **0**
- `prefers-reduced-motion: reduce`: çalışan animasyon **0**, gizli kalan açılış öğesi **0**,
  `scroll-behavior: auto`

**Etkileşim testi** (tamamı geçti): çerez, arama önerisi, temizle, giriş modalı, quick view,
favori rozeti, sepet çekmecesi, ilan sekmeleri, politika modalları, lightbox (ok ve Esc),
filtreler, renk kutucukları, sıralama, sayfa boyutu, sanatçı araması, bülten doğrulaması,
mobil filtre paneli, başa dön.

## Kapatılamayan tek kural ve nedeni

**"Yalnız 400 ve 700 kullanılmaz; 500 ve 600 da sisteme girer."**
Ortamdaki lisanslı font dosyaları (Crimson Pro, Instrument Sans, Geist Mono) yalnız
400 ve 700 taşıyor; hiçbiri değişken font değil. Ara ağırlığı tarayıcıya uydurtmak
aynı sözleşmede `font-synthesis-weight:none` ile yasak. Kuralın amacı olan
"düz 400/700 görüntüsünden kaçınmak" üç aile (gösteri serifi, gövde sans, künye mono),
italik, harf aralığı ve renk kademesiyle karşılandı.

## 1stDibs karşılaştırmasından bu turda eklenenler
- Sayfa altında **Popular Searches** çip bulutu + "View All Popular X Searches"
- **Başa dön** düğmesi (kaydırma dinleyicisi yok, IntersectionObserver)
- Promo şeridinde "Terms apply. Details"
- Kategori süzgecinde "Back to All Items"
- Mobilde alt kategori yatay rayı ve tam ekran filtre paneli
