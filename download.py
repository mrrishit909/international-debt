"""Step 1: external debt of low- and middle-income countries from the World Bank's International Debt Statistics (IDS), via its API.

    ./venv/bin/python download.py   -> data/ids.csv.gz (country, year, series, creditor, value), data/countries.csv, results/pull.json

Debt stocks are in current US dollars. Creditor "WLD" means the series total; "730" is China (bilateral lending by China).
"""
import csv
import gzip
import json
import ssl
import urllib.request
from datetime import date
from pathlib import Path

import certifi

HERE = Path(__file__).parent
API = "https://api.worldbank.org/v2"
CTX = ssl.create_default_context(cafile=certifi.where())
SERIES = {
    "DT.DOD.DECT.CD": "External debt stocks, total",
    "DT.DOD.DPPG.CD": "Public and publicly guaranteed (PPG) debt",
    "DT.DOD.DPNG.CD": "Private non-guaranteed debt",
    "DT.DOD.DSTC.CD": "Short-term debt",
    "DT.DOD.DIMF.CD": "Use of IMF credit",
    "DT.DOD.MLAT.CD": "PPG owed to multilateral creditors",
    "DT.DOD.BLAT.CD": "PPG owed to bilateral creditors",
    "DT.DOD.PBND.CD": "PPG owed to bondholders",
    "DT.DOD.PCBK.CD": "PPG owed to commercial banks",
    "DT.DOD.PROP.CD": "PPG owed to other private creditors",
    "DT.TDS.DECT.CD": "Total debt service",
    "BX.GSR.TOTL.CD": "Exports of goods, services and primary income",
    "NY.GNP.MKTP.CD": "Gross national income",
}
CHINA = ("DT.DOD.BLAT.CD", "730")


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "research-portfolio (Rishit Raj Mathur)"})
    return json.loads(urllib.request.urlopen(req, context=CTX, timeout=300).read())


def pull(series, creditor):
    d = get(f"{API}/sources/6/country/all/series/{series}/counterpart-area/{creditor}/time/all?format=json&per_page=20000")
    assert d["pages"] == 1, "the API paged: raise per_page"
    rows = []
    for r in d["source"]["data"]:
        v = {x["concept"]: x["id"] for x in r["variable"]}          # fields by name: their order changes with the filters used
        if r["value"] is not None:
            rows.append((v["Country"], int(v["Time"][2:]), series, creditor, r["value"]))
    return rows, d["lastupdated"]


def main():
    (HERE / "data").mkdir(exist_ok=True)
    (HERE / "results").mkdir(exist_ok=True)
    rows, counts, updated = [], {}, set()
    for series, creditor in [(s, "WLD") for s in SERIES] + [CHINA]:
        got, last = pull(series, creditor)
        rows += got
        counts[f"{series}|{creditor}"] = len(got)
        updated.add(last)
    with gzip.open(HERE / "data" / "ids.csv.gz", "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(["country", "year", "series", "creditor", "value"])
        w.writerows(rows)
    meta = get(f"{API}/country?format=json&per_page=400")[1]
    with open(HERE / "data" / "countries.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["code", "name", "region", "income_level", "lending_type", "is_aggregate"])
        for c in meta:
            w.writerow([c["id"], c["name"], c["region"]["value"].strip(), c["incomeLevel"]["value"], c["lendingType"]["value"], c["region"]["id"] == "NA"])
    info = {"pulled": date.today().isoformat(), "ids_last_updated": sorted(updated), "rows": len(rows), "countries_in_metadata": len(meta), "rows_by_series": counts}
    (HERE / "results" / "pull.json").write_text(json.dumps(info, indent=2) + "\n")
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
