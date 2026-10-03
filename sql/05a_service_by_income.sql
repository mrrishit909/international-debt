-- How much of export earnings goes to debt service, by income group and year, 2005 to 2024 (debt service of the group's countries over their exports).
SELECT i.year, c.income_level,
       COUNT(DISTINCT i.country) AS countries,
       ROUND(100 * SUM(i.value) FILTER (WHERE i.series = 'DT.TDS.DECT.CD') / SUM(i.value) FILTER (WHERE i.series = 'BX.GSR.TOTL.CD'), 1) AS service_to_exports_pct
FROM ids i JOIN countries c ON c.code = i.country
WHERE i.creditor = 'WLD' AND NOT c.is_aggregate AND i.year BETWEEN 2005 AND 2024 AND i.series IN ('DT.TDS.DECT.CD', 'BX.GSR.TOTL.CD')
GROUP BY i.year, c.income_level ORDER BY c.income_level, i.year;
