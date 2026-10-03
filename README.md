# Who do developing countries owe?

External debt of the 120 low- and middle-income countries that report to the World Bank, from 2000 to 2024, analysed in SQL (DuckDB):
- how much is owed, and what kind of debt it is;
- who the biggest borrowers are, and how heavy the debt is for the economy and for export earnings;
- who lends, and how that changed (bondholders now hold almost half of public debt);
- how much is owed to China;
- how much of export earnings goes to debt service.

The questions follow DataCamp's "Analyze International Debt Statistics" project (SQL on the World Bank's international debt data).
The data here is the Bank's current release, with many more series and years.

Build log: https://mrrishit909.github.io/projects/international-debt/

## Data

World Bank International Debt Statistics (IDS), release of 2025-12-03, through its API (`api.worldbank.org/v2/sources/6`), pulled
2026-10-03. Free to reuse under CC BY 4.0 (World Bank Open Data); cite "World Bank, International Debt Statistics". Fourteen series
(total external debt, public and publicly guaranteed debt by creditor type, short-term debt, IMF credit, debt service, exports,
gross national income, and bilateral lending by China) and the Bank's country list, with income groups. The snapshot is small
(750 KB), so it is committed in `data/`; `download.py` refreshes it, but the Bank revises its data.

```
./venv/bin/pip install duckdb pandas matplotlib certifi      # in a venv
./venv/bin/python download.py    # data/ids.csv.gz, data/countries.csv
./venv/bin/python run_sql.py     # results/*.csv from sql/*.sql
./venv/bin/python check.py
./venv/bin/python charts.py
```

## Steps

1. **Download** the series and the country list. The API returns each series for every country and year in one call.
2. **Queries** (`sql/`, one file per question, each result written to `results/`), using CTEs, `FILTER` aggregates and window
   functions (`LAG`, `RANK`, `SUM() OVER`, `FIRST_VALUE`):
   - `01_debt_by_year`: total and its parts, with year-on-year growth;
   - `02_biggest_borrowers`: top 15 in 2024 with share, cumulative share, debt against income, debt service against exports, two ranks;
   - `03a`, `03b`: public debt by creditor type, by year and by borrower income group;
   - `04a`, `04b`: bilateral debt owed to China, by year (with the peak) and by borrower;
   - `05a`, `05b`: debt service against exports, by income group and by country.
3. **Check.** `check.py` rebuilds every table with plain Python (no SQL, no DuckDB, no pandas) and requires all 841 numbers to equal the
   SQL results.
4. **Charts.**

Sums are over the reporting countries, not the Bank's regional aggregates.

## Results

- **The stock grew almost fivefold.** The reporting countries owed $1.83 trillion in 2000, $3.84tn in 2010 and $8.94tn in 2024. In 2024, 39.8%
  was public and publicly guaranteed, 29.2% private and not guaranteed, 26.8% short-term and 4.2% IMF credit.
- **A few borrowers dominate.** China owes $2.42tn (27.4%), India $716bn, Brazil $606bn, Mexico $591bn, Turkiye $515bn: five
  countries hold 55.0%, fifteen hold 77.9%. Size is not weight: China's debt is 13% of national income and its debt service 9% of exports.
  Seven of the fifteen spend over 20% of export earnings on debt service (Egypt 49%, Kazakhstan 48%, Colombia 43%, Argentina 38%).
  Ukraine's debt is 101% of national income.
- **Bondholders replaced governments.** Bondholders held 28.8% of public debt in 2005, 50.3% in 2021 and 46.0% in 2024. Bilateral
  lenders fell from 27.2% to 13.4%, multilateral lenders from 31.4% to 23.5% (2019) and back to 27.8%. Poorer countries are the
  other way round: in low-income countries 52.9% of public debt is multilateral, 34.7% bilateral and 12.4% private; in upper-middle
  income countries 71.1% is private.
- **China.** Bilateral debt owed to China grew from $6.5bn in 2005 to a peak of $157.2bn in 2021 and was $148.0bn in 2024. Pakistan owes
  $22.4bn (25.0% of its public debt), Sri Lanka $8.7bn (22.0%), Lao PDR $5.2bn (52.3%), Cambodia $4.1bn (34.1%).
- **Debt service.** Low-income countries spent 3.7% of exports on debt service in 2010, 19.6% in 2021 and 11.7% in 2024. Countries above
  20% of exports: 13 in 2010, 44 in 2020 (37.9% of those reporting), 33 in 2024 (30.6%).

## Not done, and caveats

- Values are current US dollars: growth since 2000 mixes new borrowing, exchange rates and inflation.
- The data is what borrowers report. Advanced economies are not covered, and loans that governments did not report, including some
  Chinese lending, are missing, so the China figures are a floor. Chinese bank loans may also be classed as commercial.
- Debt service includes IMF charges and repurchases; a single year can be dominated by a one-off payment (El Salvador shows 96% in 2024).
- The 20% cut-off is illustrative, not an IMF or World Bank threshold. Coverage varies by year (108 countries have both debt service and
  exports in 2024, 120 have debt stocks).
- Debt stocks are not debt sustainability: nothing here compares debt with a country's ability to repay beyond two simple ratios.
