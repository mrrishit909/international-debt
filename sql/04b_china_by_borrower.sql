-- Who owes China most in 2024, and how much of each borrower's public debt that is.
WITH y AS (
    SELECT i.country, c.name,
           MAX(i.value) FILTER (WHERE i.creditor = '730' AND i.series = 'DT.DOD.BLAT.CD') AS china,
           MAX(i.value) FILTER (WHERE i.creditor = 'WLD' AND i.series = 'DT.DOD.BLAT.CD') AS bilateral,
           MAX(i.value) FILTER (WHERE i.creditor = 'WLD' AND i.series = 'DT.DOD.DPPG.CD') AS ppg
    FROM ids i JOIN countries c ON c.code = i.country
    WHERE i.year = 2024 AND NOT c.is_aggregate AND i.series IN ('DT.DOD.BLAT.CD', 'DT.DOD.DPPG.CD')
    GROUP BY i.country, c.name
)
SELECT name, ROUND(china / 1e9, 2) AS china_bn, ROUND(100 * china / ppg, 1) AS share_of_public_debt_pct, ROUND(100 * china / bilateral, 1) AS share_of_bilateral_pct,
       RANK() OVER (ORDER BY china DESC) AS rank
FROM y WHERE china IS NOT NULL ORDER BY china DESC LIMIT 12;
