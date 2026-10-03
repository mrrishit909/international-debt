-- Who lends? Public and publicly guaranteed (PPG) debt of the reporting countries by type of creditor, 2005 to 2024.
WITH d AS (
    SELECT i.year,
           SUM(i.value) FILTER (WHERE i.series = 'DT.DOD.MLAT.CD') AS multilateral,
           SUM(i.value) FILTER (WHERE i.series = 'DT.DOD.BLAT.CD') AS bilateral,
           SUM(i.value) FILTER (WHERE i.series = 'DT.DOD.PBND.CD') AS bonds,
           SUM(i.value) FILTER (WHERE i.series = 'DT.DOD.PCBK.CD') AS banks,
           SUM(i.value) FILTER (WHERE i.series = 'DT.DOD.PROP.CD') AS other_private,
           SUM(i.value) FILTER (WHERE i.series = 'DT.DOD.DPPG.CD') AS ppg
    FROM ids i JOIN countries c ON c.code = i.country
    WHERE i.creditor = 'WLD' AND NOT c.is_aggregate AND i.year BETWEEN 2005 AND 2024
    GROUP BY i.year
)
SELECT year, ROUND(ppg / 1e9, 1) AS ppg_bn,
       ROUND(100 * multilateral / ppg, 1) AS multilateral_pct, ROUND(100 * bilateral / ppg, 1) AS bilateral_pct,
       ROUND(100 * bonds / ppg, 1) AS bonds_pct, ROUND(100 * banks / ppg, 1) AS banks_pct, ROUND(100 * other_private / ppg, 1) AS other_private_pct,
       ROUND(100 * (bonds + banks + other_private) / ppg, 1) AS private_pct,
       ROUND(100 * (multilateral + bilateral + bonds + banks + other_private - ppg) / ppg, 1) AS gap_pct
FROM d ORDER BY year;
