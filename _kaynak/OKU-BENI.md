# _kaynak

Siteyi ureten Python dosyalarinin kopyasi. GitHub Actions
(.github/workflows/yayinla.yml) burayi kullanir:

    cd _kaynak
    VO_CIKTI=<depo koku> python tools/supabase_cek.py
    VO_CIKTI=<depo koku> python build_en.py

Elle degisiklik proje kokunde yapilir, sonra
`python tools/kaynak_kopyala.py` ile buraya tazelenir.
