# -*- coding: utf-8 -*-
"""Panelin butun sayfalarini headless tarayicida gezer, konsol hatasi toplar.

Giris bilgileri ortam degiskeninden gelir (SUPABASE_EPOSTA / SUPABASE_SIFRE);
bu betik yayinla.bat'in kullandigi ayni demo hesabi kullanir.

Kullanim:
    set SUPABASE_EPOSTA=...& set SUPABASE_SIFRE=...& python tools\\panel_qa.py
"""
import os
import sys

EPOSTA = os.environ.get("SUPABASE_EPOSTA", "")
SIFRE = os.environ.get("SUPABASE_SIFRE", "")
if not (EPOSTA and SIFRE):
    sys.exit("SUPABASE_EPOSTA ve SUPABASE_SIFRE gerekli.")

SAYFALAR = ["#/ilanlar", "#/fiyatlar", "#/kampanyalar", "#/siparisler",
            "#/talepler", "#/odeme", "#/analitik", "#/sayfalar",
            "#/sanatcilar", "#/ayarlar", "#/kullanicilar", "#/gecmis"]

from playwright.sync_api import sync_playwright

hatalar = []
with sync_playwright() as p:
    tarayici = p.chromium.launch(headless=True)
    sayfa = tarayici.new_page()
    sayfa.on("console", lambda m: hatalar.append((sayfa.url, m.text))
             if m.type in ("error",) else None)
    sayfa.on("pageerror", lambda e: hatalar.append((sayfa.url, "PAGEERROR " + str(e))))

    sayfa.goto("https://thetimesfigures.com/admin/", wait_until="domcontentloaded")
    sayfa.wait_for_timeout(2500)
    sayfa.fill("#eposta", EPOSTA) if sayfa.query_selector("#eposta") else None
    # Alan kimlikleri farkli olabilir; ilk e-posta ve sifre girdisini kullan.
    girdiler = sayfa.query_selector_all("input")
    if len(girdiler) >= 2:
        girdiler[0].fill(EPOSTA)
        girdiler[1].fill(SIFRE)
        sayfa.get_by_role("button", name="Giris yap").click()
    sayfa.wait_for_timeout(4000)
    print("giris sonrasi:", sayfa.url)

    for yol in SAYFALAR:
        sayfa.goto("https://thetimesfigures.com/admin/" + yol)
        sayfa.wait_for_timeout(2200)
        govde = sayfa.inner_text("body")
        isaret = "OK"
        if "Yukleniyor" in govde and len(govde) < 400:
            isaret = "TAKILDI"
        if "hata" in govde.lower()[:600]:
            isaret = "HATA-METNI"
        print(f"{yol:16} {isaret}  ({len(govde)} karakter)")

    tarayici.close()

print()
if hatalar:
    print("KONSOL HATALARI (%d):" % len(hatalar))
    for u, t in hatalar[:20]:
        print("  ", u.split('admin/')[-1][:24], "|", t[:160].encode("ascii", "replace").decode())
else:
    print("Konsol hatasi yok.")
