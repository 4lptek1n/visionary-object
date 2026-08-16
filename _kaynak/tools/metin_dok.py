# -*- coding: utf-8 -*-
"""Belirli ilanlarin gorunur metinlerini tam haliyle doker (duzeltme icin)."""
import json, os, sys, urllib.request

URL = "https://vtrwlajtotcnwusjlzgo.supabase.co"
ANON = os.environ["SUPABASE_ANON_KEY"]

def giris():
    g = json.dumps({"email": os.environ["SUPABASE_EPOSTA"],
                    "password": os.environ["SUPABASE_SIFRE"]}).encode()
    r = urllib.request.Request(URL + "/auth/v1/token?grant_type=password", g)
    r.add_header("apikey", ANON); r.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(r, timeout=40) as c:
        return json.loads(c.read())["access_token"]

JETON = giris()
istenen = sys.argv[1:] or ["ilan-23"]
r = urllib.request.Request(URL + "/rest/v1/ilanlar?select=slug,baslik,sanatci,aciklama,belge,etiket,seo_aciklama&slug=in.(%s)" % ",".join('"%s"' % s for s in istenen))
r.add_header("apikey", ANON); r.add_header("Authorization", "Bearer " + JETON)
with urllib.request.urlopen(r, timeout=60) as c:
    veri = json.loads(c.read())
cikti = os.path.join(os.path.dirname(os.path.abspath(__file__)), "metin_dok.json")
json.dump(veri, open(cikti, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("yazildi:", cikti, len(veri), "ilan")
