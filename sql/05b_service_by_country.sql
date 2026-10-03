-- Countries spending more than 20% of export earnings on debt service (an illustrative cut-off, not an official threshold), by year;
-- and the ten heaviest in 2024 among countries exporting at least $1 billion.
WITH r AS (
    SELECT i.year, i.country, c.name,
           MAX(i.value) FILTER (WHERE i.series = 'DT.TDS.DECT.CD') AS service,
           MAX(i.value) FILTER (WHERE i.series = 'BX.GSR.TOTL.CD') AS exports
    FROM ids i JOIN countries c ON c.code = i.country
    WHERE i.creditor = 'WLD' AND NOT c.is_aggregate AND i.year BETWEEN 2005 AND 2024 AND i.series IN ('DT.TDS.DECT.CD', 'BX.GSR.TOTL.CD')
    GROUP BY i.year, i.country, c.name
), ok AS (SELECT *, 100 * service / exports AS ratio FROM r WHERE service IS NOT NULL AND exports > 0)
SELECT * FROM (
    SELECT 'year' AS kind, CAST(year AS VARCHAR) AS label, COUNT(*) AS countries, COUNT(*) FILTER (WHERE ratio > 20) AS above_20pct,
           ROUND(100.0 * COUNT(*) FILTER (WHERE ratio > 20) / COUNT(*), 1) AS share_above_20pct, NULL AS ratio_pct
    FROM ok GROUP BY year
    UNION ALL
    SELECT 'heaviest_2024', name, NULL, NULL, NULL, ROUND(ratio, 1) FROM (SELECT * FROM ok WHERE year = 2024 AND exports >= 1e9 ORDER BY ratio DESC LIMIT 10)
) ORDER BY CASE kind WHEN 'year' THEN 0 ELSE 1 END, CASE WHEN kind = 'year' THEN label END, ratio_pct DESC;
