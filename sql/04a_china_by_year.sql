-- Bilateral lending by China to the reporting countries: the stock owed to China each year, its growth, and its peak.
WITH t AS (
    SELECT i.year, SUM(i.value) AS owed, COUNT(*) AS borrowers
    FROM ids i JOIN countries c ON c.code = i.country
    WHERE i.series = 'DT.DOD.BLAT.CD' AND i.creditor = '730' AND NOT c.is_aggregate AND i.year BETWEEN 2005 AND 2024
    GROUP BY i.year
)
SELECT year, borrowers, ROUND(owed / 1e9, 1) AS owed_bn,
       ROUND(100 * (owed / LAG(owed) OVER (ORDER BY year) - 1), 1) AS growth_pct,
       ROUND(MAX(owed) OVER () / 1e9, 1) AS peak_bn,
       year = FIRST_VALUE(year) OVER (ORDER BY owed DESC) AS is_peak_year
FROM t ORDER BY year;
