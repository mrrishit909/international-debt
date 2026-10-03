-- The 15 largest borrowers in 2024: how much, what share of the total, and how heavy the debt is for the economy (debt against national
-- income) and for its export earnings (debt service against exports). Ranks by size and by weight show who is big but light, or small but heavy.
WITH y AS (
    SELECT i.country, c.name, c.income_level,
           MAX(i.value) FILTER (WHERE i.series = 'DT.DOD.DECT.CD') AS debt,
           MAX(i.value) FILTER (WHERE i.series = 'NY.GNP.MKTP.CD') AS gni,
           MAX(i.value) FILTER (WHERE i.series = 'DT.TDS.DECT.CD') AS service,
           MAX(i.value) FILTER (WHERE i.series = 'BX.GSR.TOTL.CD') AS exports
    FROM ids i JOIN countries c ON c.code = i.country
    WHERE i.creditor = 'WLD' AND i.year = 2024 AND NOT c.is_aggregate
    GROUP BY i.country, c.name, c.income_level
), r AS (
    SELECT *,
           RANK() OVER (ORDER BY debt DESC)       AS rank_by_size,
           RANK() OVER (ORDER BY debt / gni DESC) AS rank_by_debt_to_gni,
           ROUND(100 * debt / SUM(debt) OVER (), 1) AS share_pct,
           ROUND(100 * SUM(debt) OVER (ORDER BY debt DESC) / SUM(debt) OVER (), 1) AS cumulative_pct
    FROM y WHERE debt IS NOT NULL AND gni IS NOT NULL
)
SELECT name, income_level, ROUND(debt / 1e9, 1) AS debt_bn, share_pct, cumulative_pct,
       ROUND(100 * debt / gni, 1) AS debt_to_gni_pct, ROUND(100 * service / exports, 1) AS service_to_exports_pct,
       rank_by_size, rank_by_debt_to_gni
FROM r ORDER BY rank_by_size LIMIT 15;
