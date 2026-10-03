"""Step 6: charts.   ./venv/bin/python charts.py -> charts/00_cover.png, 01_stock.png, 02_borrowers.png, 03_creditors.png, 04_china.png, 05_service.png"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
R = HERE / "results"
INK, DIM, GRID, BG, BLUE, ORANGE, GRAY, GREEN = "#f2f2f0", "#8a8a87", "#1d1d1d", "#0b0b0b", "#3987e5", "#d95926", "#9a9a96", "#3aa876"
plt.rcParams.update({"figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG, "text.color": INK,
                     "axes.edgecolor": "#3a3a3a", "axes.labelcolor": DIM, "xtick.color": DIM, "ytick.color": DIM,
                     "axes.grid": True, "axes.axisbelow": True, "grid.color": GRID, "grid.linewidth": 1,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "font.family": ["Helvetica Neue", "Arial", "DejaVu Sans"], "font.size": 11, "axes.titlesize": 13,
                     "axes.titlelocation": "left", "axes.titlepad": 12})


def save(fig, name):
    fig.tight_layout(); fig.savefig(HERE / "charts" / name, dpi=150); plt.close(fig)


def stock(ax):
    d = pd.read_csv(R / "01_debt_by_year.csv"); bottom = np.zeros(len(d))
    for col, color, name in [("ppg_pct", BLUE, "public and publicly guaranteed"), ("private_nonguaranteed_pct", ORANGE, "private, not guaranteed"),
                             ("short_term_pct", GRAY, "short-term"), ("imf_pct", GREEN, "IMF credit")]:
        h = d["total_bn"] * d[col] / 100 / 1000
        ax.bar(d["year"], h, bottom=bottom, color=color, width=0.75, label=name); bottom += h
    for y in (2000, 2010, 2024):
        t = d.loc[d["year"] == y, "total_bn"].iloc[0] / 1000
        ax.text(y, t + 0.15, f"${t:.1f}tn", ha="center", color=INK, fontsize=10)
    ax.set_xticks(range(2000, 2025, 4)); ax.set_ylim(0, 10.2); ax.set_ylabel("trillion US dollars"); ax.grid(axis="x", visible=False)
    ax.legend(frameon=False, labelcolor=INK, fontsize=9, loc="upper left"); ax.set_title("External debt of the 120 reporting countries")


def creditors(ax):
    d = pd.read_csv(R / "03a_creditors_by_year.csv")
    cols = [("multilateral_pct", GREEN, "multilateral"), ("bilateral_pct", GRAY, "bilateral"), ("bonds_pct", ORANGE, "bondholders"),
            ("banks_pct", BLUE, "commercial banks"), ("other_private_pct", DIM, "other private")]
    ax.stackplot(d["year"], *[d[c] for c, _, _ in cols], colors=[c for _, c, _ in cols], labels=[n for _, _, n in cols], alpha=0.95)
    ax.set_xlim(2005, 2024); ax.set_ylim(0, 100); ax.set_xticks(range(2005, 2025, 3)); ax.set_ylabel("% of public debt"); ax.grid(False)
    first, last = d.iloc[0], d.iloc[-1]
    ax.text(2005.3, first["multilateral_pct"] + first["bilateral_pct"] + first["bonds_pct"] / 2, f"bonds {first['bonds_pct']:.0f}%", color=BG, fontsize=10, va="center")
    ax.text(2023.8, last["multilateral_pct"] + last["bilateral_pct"] + last["bonds_pct"] / 2, f"bonds {last['bonds_pct']:.0f}%", color=BG, fontsize=10, va="center", ha="right")
    ax.legend(frameon=False, labelcolor=INK, fontsize=9, ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.13)); ax.set_title("Who lends: bondholders, not governments")


def main():
    (HERE / "charts").mkdir(exist_ok=True)
    fig, (a, b) = plt.subplots(1, 2, figsize=(14, 8), gridspec_kw={"width_ratios": [1, 1]})
    stock(a); creditors(b)
    for ax in (a, b):
        ax.title.set_fontsize(15)
    fig.suptitle("Who do developing countries owe? Debt of 120 countries, 2000 to 2024", x=0.01, ha="left", fontsize=20, color=INK, y=0.98)
    fig.tight_layout(rect=(0, 0, 1, 0.94)); fig.savefig(HERE / "charts" / "00_cover.png", dpi=100); plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 3.8)); stock(ax); save(fig, "01_stock.png")

    d = pd.read_csv(R / "02_biggest_borrowers.csv"); fig, ax = plt.subplots(figsize=(10, 5.2)); y = np.arange(len(d))[::-1]
    ax.barh(y, d["debt_bn"], color=[ORANGE if s > 20 else BLUE for s in d["service_to_exports_pct"]], height=0.7)
    for yi, (_, r) in zip(y, d.iterrows()):
        ax.text(r["debt_bn"] + 25, yi, f"${r['debt_bn']:,.0f}bn   {r['debt_to_gni_pct']:.0f}% of income   {r['service_to_exports_pct']:.0f}% of exports", va="center", color=INK, fontsize=9)
    ax.set_yticks(y); ax.set_yticklabels(d["name"]); ax.set_xlim(0, 3700); ax.set_xlabel("external debt, billion US dollars (2024)"); ax.grid(axis="y", visible=False)
    ax.barh([], []); ax.text(3650, 0.2, "orange: debt service above 20% of exports", ha="right", color=ORANGE, fontsize=9)
    ax.set_title(f"The 15 largest borrowers hold {d['cumulative_pct'].iloc[-1]:.0f}% of the debt; {(d['service_to_exports_pct'] > 20).sum()} of them spend over a fifth of exports servicing it")
    save(fig, "02_borrowers.png")

    fig, ax = plt.subplots(figsize=(10, 3.8)); creditors(ax); save(fig, "03_creditors.png")

    c = pd.read_csv(R / "04a_china_by_year.csv"); b = pd.read_csv(R / "04b_china_by_borrower.csv")
    fig, (a, b2) = plt.subplots(1, 2, figsize=(10, 4.2), gridspec_kw={"width_ratios": [1, 1.15]})
    a.bar(c["year"], c["owed_bn"], color=[ORANGE if p else BLUE for p in c["is_peak_year"]], width=0.75)
    pk = c[c["is_peak_year"]].iloc[0]; last = c.iloc[-1]
    a.text(pk["year"], pk["owed_bn"] + 4, f"${pk['owed_bn']:.0f}bn\n{int(pk['year'])}", ha="center", color=INK, fontsize=9)
    a.text(last["year"], last["owed_bn"] + 4, f"${last['owed_bn']:.0f}bn", ha="center", color=INK, fontsize=9)
    a.set_xticks(range(2005, 2025, 4)); a.set_ylim(0, 185); a.set_ylabel("billion US dollars"); a.grid(axis="x", visible=False); a.set_title("Owed to China (bilateral)")
    y = np.arange(len(b))[::-1]
    b2.barh(y, b["share_of_public_debt_pct"], color=BLUE, height=0.7)
    for yi, (_, r) in zip(y, b.iterrows()):
        b2.text(r["share_of_public_debt_pct"] + 1, yi, f"${r['china_bn']:.1f}bn", va="center", color=INK, fontsize=9)
    b2.set_yticks(y); b2.set_yticklabels(b["name"], fontsize=9); b2.set_xlim(0, 70); b2.set_xlabel("% of the borrower's public debt (2024)"); b2.grid(axis="y", visible=False); b2.set_title("The twelve biggest debtors to China")
    save(fig, "04_china.png")

    s = pd.read_csv(R / "05a_service_by_income.csv"); e = pd.read_csv(R / "05b_service_by_country.csv"); e = e[e["kind"] == "year"].assign(year=lambda d: d["label"].astype(int))
    fig, (a, b2) = plt.subplots(1, 2, figsize=(10, 3.8))
    for lvl, color in [("Low income", ORANGE), ("Lower middle income", BLUE), ("Upper middle income", GREEN)]:
        d = s[s["income_level"] == lvl]; a.plot(d["year"], d["service_to_exports_pct"], color=color, marker="o", linewidth=2, markersize=4, label=lvl.replace(" income", ""))
    a.set_xticks(range(2005, 2025, 4)); a.set_ylabel("debt service, % of exports"); a.grid(axis="x", visible=False); a.legend(frameon=False, labelcolor=INK, fontsize=9, loc="upper left"); a.set_title("Debt service against exports")
    b2.bar(e["year"], e["above_20pct"], color=[ORANGE if y == 2020 else BLUE for y in e["year"]], width=0.75)
    b2.text(2020, e.loc[e["year"] == 2020, "above_20pct"].iloc[0] + 1, f"{int(e.loc[e['year'] == 2020, 'above_20pct'].iloc[0])}", ha="center", color=INK, fontsize=9)
    b2.set_xticks(range(2005, 2025, 4)); b2.set_ylabel("countries"); b2.grid(axis="x", visible=False); b2.set_title("Countries spending over 20% of exports on debt")
    save(fig, "05_service.png")


if __name__ == "__main__":
    main()
