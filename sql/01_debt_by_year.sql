-- How much do the reporting countries owe, and what kind of debt is it? One row per year, 2000 to 2024, summed over countries
-- (not the Bank's regional aggregates). Total = public and publicly guaranteed (PPG) + private non-guaranteed + IMF credit + short-term.
WITH d AS (
    SELECT i.year,
           SUM(i.value) FILTER (WHERE i.series = 'DT.DOD.DECT.CD') AS total,
           SUM(i.value) FILTER (WHERE i.series = 'DT.DOD.DPPG.CD') AS ppg,
           SUM(i.value) FILTER (WHERE i.series = 'DT.DOD.DPNG.CD') AS private_nonguaranteed,
           SUM(i.value) FILTER (WHERE i.series = 'DT.DOD.DIMF.CD') AS imf,
           SUM(i.value) FILTER (WHERE i.series = 'DT.DOD.DSTC.CD') AS short_term,
           COUNT(DISTINCT i.country) FILTER (WHERE i.series = 'DT.DOD.DECT.CD') AS countries
    FROM ids i JOIN countries c ON c.code = i.country
    WHERE i.creditor = 'WLD' AND NOT c.is_aggregate AND i.year BETWEEN 2000 AND 2024
    GROUP BY i.year
)
SELECT year, countries,
       ROUND(total / 1e9, 1)                                                       AS total_bn,
       ROUND(100 * (total / LAG(total) OVER (ORDER BY year) - 1), 1)               AS growth_pct,
       ROUND(100 * ppg / total, 1)                                                 AS ppg_pct,
       ROUND(100 * private_nonguaranteed / total, 1)                               AS private_nonguaranteed_pct,
       ROUND(100 * imf / total, 1)                                                 AS imf_pct,
       ROUND(100 * short_term / total, 1)                                          AS short_term_pct,
       ROUND(100 * (total - ppg - private_nonguaranteed - imf - short_term) / total, 1) AS unexplained_pct
FROM d
ORDER BY year;
