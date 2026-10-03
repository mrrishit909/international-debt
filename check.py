"""Step 5: the project's check. Rebuild every result table with plain Python (csv, gzip and dictionaries: no DuckDB, no SQL, no pandas) from the
raw snapshot and require it to equal what the SQL wrote to results/.

    ./venv/bin/python check.py
"""
import csv
import gzip
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
R = HERE / "results"
n_ok = 0


def table(name):
    return list(csv.DictReader(open(R / f"{name}.csv")))


def same(label, got, want, tol=0.0501):
    """results are rounded to one decimal; allow half a unit in the last place"""
    global n_ok
    n_ok += 1
    assert abs(float(got) - float(want)) <= tol, f"{label}: recount {got} != SQL {want}"


def load():
    country = {r["code"]: r for r in csv.DictReader(open(HERE / "data" / "countries.csv"))}
    v = {}
    for r in csv.DictReader(gzip.open(HERE / "data" / "ids.csv.gz", "rt")):
        if country[r["country"]]["is_aggregate"] == "False":
            v[r["country"], int(r["year"]), r["series"], r["creditor"]] = float(r["value"])
    return country, v


def total(v, year, series, creditor="WLD", countries=None):
    xs = [x for (c, y, s, k), x in v.items() if y == year and s == series and k == creditor and (countries is None or c in countries)]
    return sum(xs) if xs else None


def pct(a, b):
    return 100 * a / b


def main():
    country, v = load()
    # 01: debt by year
    prev = None
    for r in table("01_debt_by_year"):
        y = int(r["year"])
        t, ppg, png = total(v, y, "DT.DOD.DECT.CD"), total(v, y, "DT.DOD.DPPG.CD"), total(v, y, "DT.DOD.DPNG.CD")
        imf, st = total(v, y, "DT.DOD.DIMF.CD"), total(v, y, "DT.DOD.DSTC.CD")
        same(f"{y} countries", len({c for (c, yy, s, k) in v if yy == y and s == "DT.DOD.DECT.CD" and k == "WLD"}), r["countries"], 0)
        same(f"{y} total", t / 1e9, r["total_bn"])
        if prev:
            same(f"{y} growth", 100 * (t / prev - 1), r["growth_pct"])
        prev = t
        for k, x in [("ppg", ppg), ("private_nonguaranteed", png), ("imf", imf), ("short_term", st)]:
            same(f"{y} {k} share", pct(x, t), r[f"{k}_pct"])
        same(f"{y} unexplained", pct(t - ppg - png - imf - st, t), r["unexplained_pct"])
    # 02: biggest borrowers, 2024
    rows = {}
    for c in {c for (c, y, s, k) in v if y == 2024 and s == "DT.DOD.DECT.CD" and k == "WLD"}:
        g = lambda s: v.get((c, 2024, s, "WLD"))
        if g("NY.GNP.MKTP.CD") is not None:
            rows[c] = (g("DT.DOD.DECT.CD"), g("NY.GNP.MKTP.CD"), g("DT.TDS.DECT.CD"), g("BX.GSR.TOTL.CD"))
    grand = sum(x[0] for x in rows.values())
    by_size = sorted(rows, key=lambda c: -rows[c][0])
    by_weight = sorted(rows, key=lambda c: -rows[c][0] / rows[c][1])
    cum = 0
    names = {r["name"]: c for c, r in country.items()}
    for i, r in enumerate(table("02_biggest_borrowers")):
        c = names[r["name"]]
        d, gni, svc, exp = rows[c]
        cum += d
        assert c == by_size[i], f"order differs at {i}: {c} vs {by_size[i]}"
        same(f"{c} debt", d / 1e9, r["debt_bn"]); same(f"{c} share", pct(d, grand), r["share_pct"]); same(f"{c} cumulative", pct(cum, grand), r["cumulative_pct"])
        same(f"{c} debt/GNI", pct(d, gni), r["debt_to_gni_pct"]); same(f"{c} service/exports", pct(svc, exp), r["service_to_exports_pct"])
        same(f"{c} rank by size", i + 1, r["rank_by_size"], 0); same(f"{c} rank by debt/GNI", by_weight.index(c) + 1, r["rank_by_debt_to_gni"], 0)
    # 03a: creditors by year
    for r in table("03a_creditors_by_year"):
        y = int(r["year"])
        ppg = total(v, y, "DT.DOD.DPPG.CD")
        parts = {k: total(v, y, s) for k, s in [("multilateral", "DT.DOD.MLAT.CD"), ("bilateral", "DT.DOD.BLAT.CD"), ("bonds", "DT.DOD.PBND.CD"),
                                                ("banks", "DT.DOD.PCBK.CD"), ("other_private", "DT.DOD.PROP.CD")]}
        same(f"{y} ppg", ppg / 1e9, r["ppg_bn"])
        for k, x in parts.items():
            same(f"{y} {k}", pct(x, ppg), r[f"{k}_pct"])
        same(f"{y} private", pct(parts["bonds"] + parts["banks"] + parts["other_private"], ppg), r["private_pct"])
        same(f"{y} gap", pct(sum(parts.values()) - ppg, ppg), r["gap_pct"])
    # 03b: creditors by income group, 2024
    for r in table("03b_creditors_by_income"):
        cs = {c for c in country if country[c]["income_level"] == r["income_level"] and country[c]["is_aggregate"] == "False"}
        ppg = total(v, 2024, "DT.DOD.DPPG.CD", countries=cs)
        same(r["income_level"] + " countries", len({c for c in cs if (c, 2024, "DT.DOD.DPPG.CD", "WLD") in v}), r["countries"], 0)
        same(r["income_level"] + " ppg", ppg / 1e9, r["ppg_bn"])
        same(r["income_level"] + " multilateral", pct(total(v, 2024, "DT.DOD.MLAT.CD", countries=cs), ppg), r["multilateral_pct"])
        same(r["income_level"] + " bilateral", pct(total(v, 2024, "DT.DOD.BLAT.CD", countries=cs), ppg), r["bilateral_pct"])
        priv = sum(total(v, 2024, s, countries=cs) or 0 for s in ("DT.DOD.PBND.CD", "DT.DOD.PCBK.CD", "DT.DOD.PROP.CD"))
        same(r["income_level"] + " private", pct(priv, ppg), r["private_pct"])
    # 04a: China by year
    prev, owed = None, {y: total(v, y, "DT.DOD.BLAT.CD", "730") for y in range(2005, 2025)}
    peak = max(owed.values())
    for r in table("04a_china_by_year"):
        y = int(r["year"])
        same(f"{y} China borrowers", len([1 for (c, yy, s, k) in v if yy == y and s == "DT.DOD.BLAT.CD" and k == "730"]), r["borrowers"], 0)
        same(f"{y} China owed", owed[y] / 1e9, r["owed_bn"])
        if prev:
            same(f"{y} China growth", 100 * (owed[y] / prev - 1), r["growth_pct"])
        prev = owed[y]
        same(f"{y} China peak", peak / 1e9, r["peak_bn"])
        assert (owed[y] == peak) == (r["is_peak_year"] == "True"), f"{y} peak flag"
    # 04b: China by borrower, 2024
    ch = sorted(((x, c) for (c, y, s, k), x in v.items() if y == 2024 and s == "DT.DOD.BLAT.CD" and k == "730"), reverse=True)
    for i, r in enumerate(table("04b_china_by_borrower")):
        x, c = ch[i]
        assert country[c]["name"] == r["name"], f"China order {i}"
        same(f"{c} China bn", x / 1e9, r["china_bn"], 0.0051)
        same(f"{c} share of PPG", pct(x, v[c, 2024, "DT.DOD.DPPG.CD", "WLD"]), r["share_of_public_debt_pct"])
        same(f"{c} share of bilateral", pct(x, v[c, 2024, "DT.DOD.BLAT.CD", "WLD"]), r["share_of_bilateral_pct"])
        same(f"{c} rank", i + 1, r["rank"], 0)
    # 05a: debt service over exports by income group
    for r in table("05a_service_by_income"):
        y = int(r["year"])
        cs = {c for c in country if country[c]["income_level"] == r["income_level"]}
        same(f"{y} {r['income_level']} countries", len({c for c in cs if (c, y, "DT.TDS.DECT.CD", "WLD") in v or (c, y, "BX.GSR.TOTL.CD", "WLD") in v}), r["countries"], 0)
        same(f"{y} {r['income_level']} service/exports", pct(total(v, y, "DT.TDS.DECT.CD", countries=cs), total(v, y, "BX.GSR.TOTL.CD", countries=cs)), r["service_to_exports_pct"])
    # 05b: countries above 20% of exports, and the ten heaviest in 2024
    ratio = defaultdict(dict)
    for (c, y, s, k), x in v.items():
        if s == "DT.TDS.DECT.CD" and k == "WLD" and 2005 <= y <= 2024 and (c, y, "BX.GSR.TOTL.CD", "WLD") in v and v[c, y, "BX.GSR.TOTL.CD", "WLD"] > 0:
            ratio[y][c] = 100 * x / v[c, y, "BX.GSR.TOTL.CD", "WLD"]
    heavy = sorted(((r_, c) for c, r_ in ratio[2024].items() if v[c, 2024, "BX.GSR.TOTL.CD", "WLD"] >= 1e9), reverse=True)[:10]
    k = 0
    for r in table("05b_service_by_country"):
        if r["kind"] == "year":
            y = int(r["label"])
            n, above = len(ratio[y]), sum(1 for x in ratio[y].values() if x > 20)
            same(f"{y} countries", n, r["countries"], 0); same(f"{y} above 20%", above, r["above_20pct"], 0); same(f"{y} share above", pct(above, n), r["share_above_20pct"])
        else:
            x, c = heavy[k]
            k += 1
            assert country[c]["name"] == r["label"], f"heaviest order {k}: {country[c]['name']} vs {r['label']}"
            same(f"{c} heavy ratio", x, r["ratio_pct"])
    print(f"check.py: {n_ok} recomputed numbers agree with the SQL results")


if __name__ == "__main__":
    main()
