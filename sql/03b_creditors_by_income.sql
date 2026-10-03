-- The same split in 2024 by the borrower's income group: poorer countries owe mostly to official lenders, richer ones to bondholders.
SELECT c.income_level, COUNT(DISTINCT i.country) AS countries,
       ROUND(SUM(i.value) FILTER (WHERE i.series = 'DT.DOD.DPPG.CD') / 1e9, 1) AS ppg_bn,
       ROUND(100 * SUM(i.value) FILTER (WHERE i.series = 'DT.DOD.MLAT.CD') / SUM(i.value) FILTER (WHERE i.series = 'DT.DOD.DPPG.CD'), 1) AS multilateral_pct,
       ROUND(100 * SUM(i.value) FILTER (WHERE i.series = 'DT.DOD.BLAT.CD') / SUM(i.value) FILTER (WHERE i.series = 'DT.DOD.DPPG.CD'), 1) AS bilateral_pct,
       ROUND(100 * (SUM(i.value) FILTER (WHERE i.series = 'DT.DOD.PBND.CD') + SUM(i.value) FILTER (WHERE i.series = 'DT.DOD.PCBK.CD')
                    + SUM(i.value) FILTER (WHERE i.series = 'DT.DOD.PROP.CD')) / SUM(i.value) FILTER (WHERE i.series = 'DT.DOD.DPPG.CD'), 1) AS private_pct
FROM ids i JOIN countries c ON c.code = i.country
WHERE i.creditor = 'WLD' AND i.year = 2024 AND NOT c.is_aggregate AND i.series IN ('DT.DOD.DPPG.CD', 'DT.DOD.MLAT.CD', 'DT.DOD.BLAT.CD', 'DT.DOD.PBND.CD', 'DT.DOD.PCBK.CD', 'DT.DOD.PROP.CD')
GROUP BY c.income_level ORDER BY ppg_bn DESC;
