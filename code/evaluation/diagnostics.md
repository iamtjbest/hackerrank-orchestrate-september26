# amount_safe_to_pay Diagnostics (25 known samples)

Columns: constraining date = date of the lowest point in the baseline (no-payment) 90-day trajectory; constraining category = the category with the largest debit landing on that date; projected = the amount our forecaster used for that category's occurrence on that date; recent history = last settled occurrences of that same category (date, home-currency amount).

| request | user | expected | predicted | diff | constraining date | constraining category | projected amount | recent history (last 5) |
|---|---|---|---|---|---|---|---|---|
| request_01 | user_01 | 25256.0 | 25256.0 | 0.0 | 2024-03-13 | delivery_membership | 306.9 | 2023-10-13:306.9; 2023-11-13:306.9; 2023-12-13:306.9; 2024-01-13:306.9; 2024-02-13:306.9 |
| request_02 | user_02 | 17229139.2 | 16519461.94 | -709677.26 | 2025-08-13 | cloud_storage | 369550.0 | 2025-03-13:369550.0; 2025-04-13:369550.0; 2025-05-13:369550.0; 2025-06-13:369550.0; 2025-07-13:369550.0 |
| request_03 | user_03 | 873000.0 | 306516.8 | -566483.2 | 2019-09-28 | groceries | 220841.35 | 2019-07-20:173004.74; 2019-07-30:214266.98; 2019-08-09:221578.88; 2019-08-19:240706.45; 2019-08-29:200238.72 |
| request_04 | user_04 | 8401800.0 | 676137.66 | -7725662.34 | 2024-08-13 | entertainment | 1355261.01 | 2024-01-13:1484369.68; 2024-02-13:1375854.05; 2024-03-13:1542620.0; 2024-04-13:1291303.65; 2024-05-13:1231859.39 |
| request_05 | user_05 | 737.0 | 0.0 | -737.0 | 2026-02-04 | transport | 372.82 | 2025-09-03:485.59; 2025-09-17:411.47; 2025-10-01:377.26; 2025-10-15:352.46; 2025-10-29:388.74 |
| request_06 | user_06 | 603.3 | 620.4 | 17.1 | 2026-01-13 | shopping | 39.1 | 2025-08-13:41.44; 2025-09-13:46.25; 2025-10-13:39.46; 2025-11-13:37.96; 2025-12-13:39.88 |
| request_07 | user_07 | 87170.56 | 86219.65 | -950.91 | 2024-09-20 | transport | 3223.8 | 2024-06-07:2439.43; 2024-06-28:3822.62; 2024-07-19:2751.86; 2024-08-09:3773.92; 2024-08-30:3145.62 |
| request_08 | user_08 | 284.57 | 304.09 | 19.52 | 2025-04-12 | delivery_membership | 24.0 | 2024-09-12:24.0; 2024-10-12:24.0; 2024-11-12:24.0; 2024-12-12:24.0; 2025-01-12:24.0 |
| request_09 | user_09 | 166.61 | 166.61 | 0.0 | 2026-07-12 | shopping | 26.17 | 2026-02-12:25.5; 2026-03-12:29.14; 2026-04-12:28.32; 2026-05-12:24.68; 2026-06-12:25.52 |
| request_10 | user_10 | 12700.0 | 266700.0 | 254000.0 | 2024-12-07 | utilities | 16252.27 | 2024-07-07:19224.83; 2024-08-07:17538.11; 2024-09-07:15748.74; 2024-10-07:15236.94; 2024-11-07:17771.13 |
| request_11 | user_11 | 12510645.0 | 13110000.0 | 599355.0 | 2025-05-11 | transport | 1157207.9 | 2025-03-02:1200020.76; 2025-03-16:1244032.33; 2025-03-30:1122838.73; 2025-04-13:1103949.29; 2025-04-27:1244835.69 |
| request_12 | user_12 | 65164.0 | 63305.84 | -1858.16 | 2026-07-01 | rent | 11792.0 | 2025-12-01:11792.0; 2026-01-01:11792.0; 2026-02-01:11792.0; 2026-03-01:11792.0; 2026-04-01:11792.0 |
| request_13 | user_13 | 433.4 | 941.6 | 508.2 | 2024-03-14 | dining | 56.55 | 2024-01-04:61.59; 2024-01-18:48.2; 2024-02-01:60.34; 2024-02-15:48.02; 2024-02-29:61.28 |
| request_14 | user_14 | 597.74 | 619.02 | 21.28 | 2025-08-14 | family_support | 226.0 | 2025-03-14:226.0; 2025-04-14:226.0; 2025-05-14:226.0; 2025-06-14:226.0; 2025-07-14:226.0 |
| request_15 | user_15 | 83.05 | 69.83 | -13.22 | 2026-01-14 | transport | 31.61 | 2025-12-03:25.63; 2025-12-10:41.35; 2025-12-17:36.86; 2025-12-24:27.67; 2025-12-31:30.31 |
| request_16 | user_16 | 122500.0 | 122500.0 | 0.0 | 2023-09-14 | transport | 5199.76 | 2023-07-13:4643.67; 2023-07-20:3888.24; 2023-07-27:5251.4; 2023-08-03:5368.95; 2023-08-10:4978.93 |
| request_17 | user_17 | 243849.58 | 221495.56 | -22354.02 | 2026-03-14 | transport | 5005.38 | 2026-01-31:4661.7; 2026-02-07:5650.43; 2026-02-14:3902.91; 2026-02-21:5741.08; 2026-02-28:5372.15 |
| request_18 | user_18 | 462.0 | 651.56 | 189.56 | 2026-07-14 | transport | 43.05 | 2026-05-05:50.57; 2026-05-19:34.87; 2026-06-02:36.29; 2026-06-16:49.04; 2026-06-30:43.81 |
| request_19 | user_19 | 28820.0 | 39660.0 | 10840.0 | 2024-09-14 | shopping | 5757.83 | 2024-04-14:6302.66; 2024-05-14:5593.2; 2024-06-14:6069.58; 2024-07-14:5772.78; 2024-08-14:5431.12 |
| request_20 | user_20 | 5400.0 | 12554.38 | 7154.38 | 2026-02-13 | entertainment | 2054.31 | 2025-09-13:2298.76; 2025-10-13:2279.67; 2025-11-13:2115.92; 2025-12-13:1949.86; 2026-01-13:2097.15 |
| request_21 | user_21 | 1543.35 | 1574.4 | 31.05 | 2026-04-12 | shopping | 120.94 | 2025-11-12:133.38; 2025-12-12:115.86; 2026-01-12:120.74; 2026-02-12:115.71; 2026-03-12:126.38 |
| request_22 | user_22 | 475.46 | 438.61 | -36.85 | 2024-12-14 | delivery_membership | 5.0 | 2024-07-14:5.0; 2024-08-14:5.0; 2024-09-14:5.0; 2024-10-14:5.0; 2024-11-14:5.0 |
| request_23 | user_23 | 9152.0 | 10290.48 | 1138.48 | 2025-05-14 | groceries | 1483.59 | 2025-04-02:1487.69; 2025-04-09:1794.76; 2025-04-16:1678.37; 2025-04-23:1514.83; 2025-04-30:1257.56 |
| request_24 | user_24 | 13420.0 | 13129.44 | -290.56 | 2026-01-13 | entertainment | 1886.05 | 2025-08-13:1870.6; 2025-09-13:2124.72; 2025-10-13:1916.16; 2025-11-13:1845.75; 2025-12-13:1896.25 |
| request_25 | user_25 | 1425000.0 | 2634286.72 | 1209286.72 | 2024-03-14 | entertainment | 476848.66 | 2023-10-14:451681.59; 2023-11-14:415734.51; 2023-12-14:499510.22; 2024-01-14:504697.37; 2024-02-14:426338.4 |

# Downstream vs independent errors

| request | amt_safe ok? | affordability_status | recommended_method | payment_plan | earliest_date | decision_explanation | verdict |
|---|---|---|---|---|---|---|---|
| request_01 | OK | OK | OK | OK | OK | OK | all correct |
| request_02 | WRONG | OK | OK | OK | OK | OK | amount wrong, other fields coincidentally match |
| request_03 | WRONG | OK | OK | WRONG | WRONG | WRONG | DOWNSTREAM of amount_safe_to_pay |
| request_04 | WRONG | WRONG | WRONG | WRONG | WRONG | WRONG | DOWNSTREAM of amount_safe_to_pay |
| request_05 | WRONG | OK | OK | OK | OK | WRONG | amount wrong, other fields coincidentally match |
| request_06 | WRONG | WRONG | OK | OK | WRONG | WRONG | DOWNSTREAM of amount_safe_to_pay |
| request_07 | WRONG | OK | OK | OK | WRONG | OK | DOWNSTREAM of amount_safe_to_pay |
| request_08 | WRONG | WRONG | WRONG | WRONG | WRONG | WRONG | DOWNSTREAM of amount_safe_to_pay |
| request_09 | OK | OK | OK | OK | OK | WRONG | only decision_explanation wording differs |
| request_10 | WRONG | OK | OK | OK | WRONG | OK | DOWNSTREAM of amount_safe_to_pay |
| request_11 | WRONG | WRONG | OK | OK | WRONG | WRONG | DOWNSTREAM of amount_safe_to_pay |
| request_12 | WRONG | WRONG | WRONG | WRONG | WRONG | WRONG | DOWNSTREAM of amount_safe_to_pay |
| request_13 | WRONG | WRONG | WRONG | WRONG | WRONG | WRONG | DOWNSTREAM of amount_safe_to_pay |
| request_14 | WRONG | OK | OK | OK | OK | WRONG | amount wrong, other fields coincidentally match |
| request_15 | WRONG | OK | OK | OK | OK | WRONG | amount wrong, other fields coincidentally match |
| request_16 | OK | OK | OK | OK | OK | OK | all correct |
| request_17 | WRONG | OK | OK | OK | OK | OK | amount wrong, other fields coincidentally match |
| request_18 | WRONG | OK | OK | OK | OK | OK | amount wrong, other fields coincidentally match |
| request_19 | WRONG | OK | WRONG | WRONG | WRONG | WRONG | DOWNSTREAM of amount_safe_to_pay |
| request_20 | WRONG | OK | OK | OK | OK | WRONG | amount wrong, other fields coincidentally match |
| request_21 | WRONG | WRONG | OK | OK | WRONG | WRONG | DOWNSTREAM of amount_safe_to_pay |
| request_22 | WRONG | WRONG | WRONG | WRONG | WRONG | WRONG | DOWNSTREAM of amount_safe_to_pay |
| request_23 | WRONG | OK | OK | OK | OK | OK | amount wrong, other fields coincidentally match |
| request_24 | WRONG | OK | OK | OK | OK | WRONG | amount wrong, other fields coincidentally match |
| request_25 | WRONG | OK | OK | OK | OK | WRONG | amount wrong, other fields coincidentally match |

# Convention substitution test

For each sample's identified constraining category, its baseline amount is swapped for each candidate convention below (holding cadence/dates fixed) and amount_safe_to_pay recomputed. `best` names whichever convention lands closest to the known-correct expected value for that row.

| request | category | expected | last1 | mean2 | mean3 | mean5 | max3 | max5 | median5 | full_mean | best |
|---|---|---|---|---|---|---|---|---|---|---|
| request_01 | delivery_membership | 25256.0 | 25256.0 | 25256.0 | 25256.0 | 25256.0 | 25256.0 | 25256.0 | 25256.0 | 25256.0 | (frozen/capped -- convention doesn't affect the result) |
| request_02 | cloud_storage | 17229139.2 | 16519461.94 | 16519461.94 | 16519461.94 | 16519461.94 | 16519461.94 | 16519461.94 | 16519461.94 | 16519461.94 | (frozen/capped -- convention doesn't affect the result) |
| request_03 | groceries | 873000.0 | 368324.69 | 307623.09 | 306516.8 | 339163.38 | 246921.5 | 246921.5 | 326239.91 | 389546.49 | full_mean (389546.49) |
| request_04 | entertainment | 8401800.0 | 1046342.53 | 957176.14 | 676137.66 | 586316.64 | 114060.7 | 114060.7 | 614358.55 | 586316.64 | last1 (1046342.53) |
| request_05 | transport | 737.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | (frozen/capped -- convention doesn't affect the result) |
| request_06 | shopping | 603.3 | 620.4 | 620.4 | 620.4 | 620.4 | 620.4 | 620.4 | 620.4 | 620.4 | (frozen/capped -- convention doesn't affect the result) |
| request_07 | transport | 87170.56 | 86297.83 | 85983.68 | 86219.65 | 86256.76 | 85669.53 | 85620.83 | 86297.83 | 86223.32 | last1 (86297.83) |
| request_08 | delivery_membership | 284.57 | 304.09 | 304.09 | 304.09 | 304.09 | 304.09 | 304.09 | 304.09 | 304.09 | (frozen/capped -- convention doesn't affect the result) |
| request_09 | shopping | 166.61 | 166.61 | 166.61 | 166.61 | 166.61 | 166.61 | 166.61 | 166.61 | 166.61 | (frozen/capped -- convention doesn't affect the result) |
| request_10 | utilities | 12700.0 | 266700.0 | 266700.0 | 266700.0 | 266700.0 | 266700.0 | 266700.0 | 266700.0 | 266700.0 | (frozen/capped -- convention doesn't affect the result) |
| request_11 | transport | 12510645.0 | 13110000.0 | 13110000.0 | 13110000.0 | 13110000.0 | 13110000.0 | 13110000.0 | 13110000.0 | 13110000.0 | (frozen/capped -- convention doesn't affect the result) |
| request_12 | rent | 65164.0 | 63305.84 | 63305.84 | 63305.84 | 63305.84 | 63305.84 | 63305.84 | 63305.84 | 63305.84 | (frozen/capped -- convention doesn't affect the result) |
| request_13 | dining | 433.4 | 941.6 | 941.6 | 941.6 | 941.6 | 941.6 | 941.6 | 941.6 | 941.6 | (frozen/capped -- convention doesn't affect the result) |
| request_14 | family_support | 597.74 | 619.02 | 619.02 | 619.02 | 619.02 | 619.02 | 619.02 | 619.02 | 619.02 | (frozen/capped -- convention doesn't affect the result) |
| request_15 | transport | 83.05 | 72.43 | 75.07 | 69.83 | 68.33 | 59.33 | 50.35 | 72.43 | 69.54 | mean2 (75.07) |
| request_16 | transport | 122500.0 | 122500.0 | 122500.0 | 122500.0 | 122500.0 | 122500.0 | 122500.0 | 122500.0 | 122500.0 | (frozen/capped -- convention doesn't affect the result) |
| request_17 | transport | 243849.58 | 220762.02 | 220393.09 | 221495.56 | 221375.02 | 220024.16 | 220024.16 | 220762.02 | 220950.24 | mean3 (221495.56) |
| request_18 | transport | 462.0 | 650.8 | 648.19 | 651.56 | 651.69 | 645.57 | 644.04 | 650.8 | 650.76 | max5 (644.04) |
| request_19 | shopping | 28820.0 | 39660.0 | 39660.0 | 39660.0 | 39660.0 | 39660.0 | 39660.0 | 39660.0 | 39660.0 | (frozen/capped -- convention doesn't affect the result) |
| request_20 | entertainment | 5400.0 | 12511.54 | 12585.19 | 12554.38 | 12460.42 | 12492.77 | 12309.93 | 12492.77 | 12460.42 | max5 (12309.93) |
| request_21 | shopping | 1543.35 | 1574.4 | 1574.4 | 1574.4 | 1574.4 | 1574.4 | 1574.4 | 1574.4 | 1574.4 | (frozen/capped -- convention doesn't affect the result) |
| request_22 | delivery_membership | 475.46 | 438.61 | 438.61 | 438.61 | 438.61 | 438.61 | 438.61 | 438.61 | 438.61 | (frozen/capped -- convention doesn't affect the result) |
| request_23 | groceries | 9152.0 | 10516.51 | 10387.88 | 10290.48 | 10227.43 | 10095.7 | 9979.31 | 10259.24 | 10041.59 | max5 (9979.31) |
| request_24 | entertainment | 13420.0 | 13119.24 | 13144.49 | 13129.44 | 13084.8 | 13099.33 | 12890.77 | 13119.24 | 13084.8 | mean2 (13144.49) |
| request_25 | entertainment | 1425000.0 | 2684796.98 | 2645617.5 | 2634286.72 | 2651542.96 | 2606438.01 | 2606438.01 | 2659453.79 | 2651542.96 | max3 (2606438.01) |

15 of 25 rows are frozen/capped (the constraining category's estimate doesn't change the outcome) and are excluded from the tally below.
Win counts on the remaining 10 rows where the convention actually matters: last1=2, mean2=2, mean3=1, mean5=0, max3=1, max5=3, median5=0, full_mean=1

# Conclusion

15 of the 25 samples are "frozen": the constraining category's estimate has
so much headroom (or the result is capped at requested_amount) that every
candidate convention produces the identical amount_safe_to_pay. Naively
tallying "closest convention" across all 25 rows makes last-value look like
the dominant winner (17/25) -- but that is a tie-break artifact of min()
picking whichever candidate is listed first when everything ties, not a real
signal. Restricting the tally to the 10 rows where the convention actually
changes the outcome gives a near-even split (max5=3, last1=2, mean2=2,
mean3=1, max3=1, full_mean=1, median5=0, mean5=0): no single tested
convention (most recent value, trailing mean of 2/3/5, trailing max of 3/5,
trailing median of 5, or full-history mean) wins consistently. For several
of those 10 rows even the *best-fitting* candidate still misses the expected
value by a wide margin (request_04, request_17, request_20, request_25),
while the currently-coded mean-of-3 already lands closest on request_17
specifically.

Two additional structural hypotheses were tested and both made the aggregate
fit *worse*, not better, so neither is the fix either:
  * Restricting the baseline forecast to `flexibility == "fixed"` categories
    only (i.e. never counting reducible/stoppable spend against the baseline)
    -- moved several rows further from expected.
  * Using a conservative (minimum-of-recent) estimate for income instead of
    the mean -- only helped request_10 and request_13 (marginally, and for
    request_13 the salary IS confirmed via a scheduled row, so zeroing/
    minimizing it isn't well-motivated) while making request_03/04/08 much
    worse.

One genuine, non-spurious finding: request_10's user has *zero* scheduled or
pending income rows at all -- pure week-to-week gig/platform payouts
("Delivery platform payout", "Weekly app earnings", ...) with no employer
confirmation of any future payment. Fully excluding that income moved the
prediction from 266,700 (a ~21x overshoot) to 1,042 (much closer to the
expected 12,700, though still not exact). But blanket-excluding all
income without a scheduled row hurts request_02/03/04/06/08/09/11/16/18-25,
which have equally "unscheduled" but clearly real and continuing salaries.
Distinguishing "confirmed recurring salary with no scheduled row this
window" from "genuinely unconfirmed gig income" would need a signal beyond
what's tested here (e.g. category name / description keyword heuristics for
gig-platform language), which risks overfitting to this dataset's specific
employer-name vocabulary.

Given none of this cleanly generalizes, no change to the estimate convention
is applied by this diagnostic run. The likely remaining source of error is
structural rather than a mis-set constant: e.g. which categories belong in
the mandatory baseline at all, a different reserve/buffer mechanism, or
date-window mechanics the diagnostic above doesn't probe. Recommend deciding
next steps with a human in the loop rather than trying further blind
substitutions.
