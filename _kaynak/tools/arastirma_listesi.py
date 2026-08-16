# -*- coding: utf-8 -*-
"""Arastirma icin kanit dokumu: biyografisiz her sanatci + ilan kanitlari."""
import json, os, urllib.request

URL = "https://vtrwlajtotcnwusjlzgo.supabase.co"
ANON = os.environ["SUPABASE_ANON_KEY"]

def giris():
    g = json.dumps({"email": os.environ["SUPABASE_EPOSTA"],
                    "password": os.environ["SUPABASE_SIFRE"]}).encode()
    r = urllib.request.Request(URL + "/auth/v1/token?grant_type=password", g)
    r.add_header("apikey", ANON); r.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(r, timeout=40) as c:
        return json.loads(c.read())["access_token"]

J = giris()
r = urllib.request.Request(URL + "/rest/v1/ilanlar?select=slug,baslik,sanatci,teknik,baski,belge,etiket,donem,biyografi&order=no.asc")
r.add_header("apikey", ANON); r.add_header("Authorization", "Bearer " + J)
r.add_header("Range", "0-999")
with urllib.request.urlopen(r, timeout=60) as c:
    ilanlar = json.loads(c.read())

sanatci = {}
for il in ilanlar:
    ad = (il["sanatci"] or "").strip()
    if not ad:
        continue
    s = sanatci.setdefault(ad, {"bio_var": False, "ilanlar": []})
    if (il["biyografi"] or "").strip():
        s["bio_var"] = True
    s["ilanlar"].append({
        "slug": il["slug"], "baslik": il["baslik"][:90],
        "teknik": (il["teknik"] or "")[:60], "baski": (il["baski"] or "")[:60],
        "belge": (il["belge"] or "")[:110], "etiket": (il["etiket"] or "")[:110],
        "donem": il["donem"] or "",
    })

biosuz = {a: v["ilanlar"] for a, v in sanatci.items() if not v["bio_var"]}
cikti = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arastirma.json")
json.dump(biosuz, open(cikti, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("biyografisiz sanatci:", len(biosuz))
for a in sorted(biosuz):
    print(" -", a, "(%d ilan)" % len(biosuz[a]))
