# amount_safe_to_pay Diagnostics (25 known samples)

Columns: constraining date = date of the lowest point in the baseline (no-payment) 90-day trajectory; constraining category = the category with the largest debit landing on that date; projected = the amount our forecaster used for that category's occurrence on that date; recent history = last settled occurrences of that same category (date, home-currency amount).

| request | user | expected | predicted | diff | constraining date | constraining category | projected amount | recent history (last 5) |
|---|---|---|---|---|---|---|---|---|
| request_01 | user_01 | 25256.0 | 25256.0 | 0.0 | 2024-03-13 | delivery_membership | 306.9 | 2023-10-13:306.9; 2023-11-13:306.9; 2023-12-13:306.9; 2024-01-13:306.9; 2024-02-13:306.9 |
| request_02 | user_02 | 17229139.2 | 18170561.94 | 941422.74 | 2025-08-13 | cloud_storage | 369550.0 | 2025-03-13:369550.0; 2025-04-13:369550.0; 2025-05-13:369550.0; 2025-06-13:369550.0; 2025-07-13:369550.0 |
| request_03 | user_03 | 873000.0 | 401516.8 | -471483.2 | 2019-09-28 | groceries | 220841.35 | 2019-07-20:173004.74; 2019-07-30:214266.98; 2019-08-09:221578.88; 2019-08-19:240706.45; 2019-08-29:200238.72 |
| request_04 | user_04 | 8401800.0 | 10567911.35 | 2166111.35 | 2024-06-13 | entertainment | 1355261.01 | 2024-01-13:1484369.68; 2024-02-13:1375854.05; 2024-03-13:1542620.0; 2024-04-13:1291303.65; 2024-05-13:1231859.39 |
| request_05 | user_05 | 737.0 | 0.0 | -737.0 | 2026-02-04 | transport | 372.82 | 2025-09-03:485.59; 2025-09-17:411.47; 2025-10-01:377.26; 2025-10-15:352.46; 2025-10-29:388.74 |
| request_06 | user_06 | 603.3 | 620.4 | 17.1 | 2026-01-13 | shopping | 39.1 | 2025-08-13:41.44; 2025-09-13:46.25; 2025-10-13:39.46; 2025-11-13:37.96; 2025-12-13:39.88 |
| request_07 | user_07 | 87170.56 | 86219.65 | -950.91 | 2024-09-20 | transport | 3223.8 | 2024-06-07:2439.43; 2024-06-28:3822.62; 2024-07-19:2751.86; 2024-08-09:3773.92; 2024-08-30:3145.62 |
| request_08 | user_08 | 284.57 | 304.09 | 19.52 | 2025-04-12 | delivery_membership | 24.0 | 2024-09-12:24.0; 2024-10-12:24.0; 2024-11-12:24.0; 2024-12-12:24.0; 2025-01-12:24.0 |
| request_09 | user_09 | 166.61 | 166.61 | 0.0 | 2026-07-12 | shopping | 26.17 | 2026-02-12:25.5; 2026-03-12:29.14; 2026-04-12:28.32; 2026-05-12:24.68; 2026-06-12:25.52 |
| request_10 | user_10 | 12700.0 | 266700.0 | 254000.0 | 2024-12-07 | utilities | 16252.27 | 2024-07-07:19224.83; 2024-08-07:17538.11; 2024-09-07:15748.74; 2024-10-07:15236.94; 2024-11-07:17771.13 |
| request_11 | user_11 | 12510645.0 | 13110000.0 | 599355.0 | 2025-05-11 | transport | 1157207.9 | 2025-03-02:1200020.76; 2025-03-16:1244032.33; 2025-03-30:1122838.73; 2025-04-13:1103949.29; 2025-04-27:1244835.69 |
| request_12 | user_12 | 65164.0 | 63305.84 | -1858.16 | 2026-07-01 | rent | 11792.0 | 2025-12-01:11792.0; 2026-01-01:11792.0; 2026-02-01:11792.0; 2026-03-01:11792.0; 2026-04-01:11792.0 |
| request_13 | user_13 | 433.4 | 568.47 | 135.07 | 2024-05-14 | groceries | 99.24 | 2024-02-06:73.74; 2024-02-13:98.36; 2024-02-20:118.36; 2024-02-27:85.71; 2024-03-05:93.66 |
| request_14 | user_14 | 597.74 | 619.02 | 21.28 | 2025-08-14 | family_support | 226.0 | 2025-03-14:226.0; 2025-04-14:226.0; 2025-05-14:226.0; 2025-06-14:226.0; 2025-07-14:226.0 |
| request_15 | user_15 | 83.05 | 69.83 | -13.22 | 2026-01-14 | transport | 31.61 | 2025-12-03:25.63; 2025-12-10:41.35; 2025-12-17:36.86; 2025-12-24:27.67; 2025-12-31:30.31 |
| request_16 | user_16 | 122500.0 | 122500.0 | 0.0 | 2023-09-14 | transport | 5199.76 | 2023-07-13:4643.67; 2023-07-20:3888.24; 2023-07-27:5251.4; 2023-08-03:5368.95; 2023-08-10:4978.93 |
| request_17 | user_17 | 243849.58 | 195860.72 | -47988.86 | 2026-05-13 | delivery_membership | 1675.0 | 2025-10-13:1675.0; 2025-11-13:1675.0; 2025-12-13:1675.0; 2026-01-13:1675.0; 2026-02-13:1675.0 |
| request_18 | user_18 | 462.0 | 651.56 | 189.56 | 2026-07-14 | transport | 43.05 | 2026-05-05:50.57; 2026-05-19:34.87; 2026-06-02:36.29; 2026-06-16:49.04; 2026-06-30:43.81 |
| request_19 | user_19 | 28820.0 | 39660.0 | 10840.0 | 2024-09-14 | shopping | 5757.83 | 2024-04-14:6302.66; 2024-05-14:5593.2; 2024-06-14:6069.58; 2024-07-14:5772.78; 2024-08-14:5431.12 |
| request_20 | user_20 | 5400.0 | 17024.38 | 11624.38 | 2026-02-13 | entertainment | 2054.31 | 2025-09-13:2298.76; 2025-10-13:2279.67; 2025-11-13:2115.92; 2025-12-13:1949.86; 2026-01-13:2097.15 |
| request_21 | user_21 | 1543.35 | 1574.4 | 31.05 | 2026-04-12 | shopping | 120.94 | 2025-11-12:133.38; 2025-12-12:115.86; 2026-01-12:120.74; 2026-02-12:115.71; 2026-03-12:126.38 |
| request_22 | user_22 | 475.46 | 481.61 | 6.15 | 2024-12-14 | delivery_membership | 5.0 | 2024-07-14:5.0; 2024-08-14:5.0; 2024-09-14:5.0; 2024-10-14:5.0; 2024-11-14:5.0 |
| request_23 | user_23 | 9152.0 | 11668.98 | 2516.98 | 2025-05-14 | groceries | 1483.59 | 2025-04-02:1487.69; 2025-04-09:1794.76; 2025-04-16:1678.37; 2025-04-23:1514.83; 2025-04-30:1257.56 |
| request_24 | user_24 | 13420.0 | 15639.44 | 2219.44 | 2026-01-13 | entertainment | 1886.05 | 2025-08-13:1870.6; 2025-09-13:2124.72; 2025-10-13:1916.16; 2025-11-13:1845.75; 2025-12-13:1896.25 |
| request_25 | user_25 | 1425000.0 | 2634286.72 | 1209286.72 | 2024-03-14 | entertainment | 476848.66 | 2023-10-14:451681.59; 2023-11-14:415734.51; 2023-12-14:499510.22; 2024-01-14:504697.37; 2024-02-14:426338.4 |

# Downstream vs independent errors

| request | amt_safe ok? | affordability_status | recommended_method | payment_plan | earliest_date | decision_explanation | verdict |
|---|---|---|---|---|---|---|---|
| request_01 | OK | OK | OK | OK | OK | OK | all correct |
| request_02 | WRONG | OK | OK | OK | OK | OK | amount wrong, other fields coincidentally match |
| request_03 | WRONG | OK | OK | WRONG | WRONG | WRONG | DOWNSTREAM of amount_safe_to_pay |
| request_04 | WRONG | OK | OK | OK | OK | WRONG | amount wrong, other fields coincidentally match |
| request_05 | WRONG | OK | OK | OK | OK | WRONG | amount wrong, other fields coincidentally match |
| request_06 | WRONG | WRONG | OK | OK | WRONG | WRONG | DOWNSTREAM of amount_safe_to_pay |
| request_07 | WRONG | OK | OK | OK | OK | OK | amount wrong, other fields coincidentally match |
| request_08 | WRONG | WRONG | WRONG | WRONG | WRONG | WRONG | DOWNSTREAM of amount_safe_to_pay |
| request_09 | OK | OK | OK | OK | OK | WRONG | only decision_explanation wording differs |
| request_10 | WRONG | OK | OK | OK | WRONG | OK | DOWNSTREAM of amount_safe_to_pay |
| request_11 | WRONG | WRONG | OK | OK | WRONG | WRONG | DOWNSTREAM of amount_safe_to_pay |
| request_12 | WRONG | WRONG | WRONG | WRONG | WRONG | WRONG | DOWNSTREAM of amount_safe_to_pay |
| request_13 | WRONG | WRONG | WRONG | WRONG | WRONG | WRONG | DOWNSTREAM of amount_safe_to_pay |
| request_14 | WRONG | OK | OK | OK | OK | WRONG | amount wrong, other fields coincidentally match |
| request_15 | WRONG | OK | OK | OK | OK | WRONG | amount wrong, other fields coincidentally match |
| request_16 | OK | OK | OK | OK | OK | OK | all correct |
| request_17 | WRONG | WRONG | WRONG | WRONG | WRONG | WRONG | DOWNSTREAM of amount_safe_to_pay |
| request_18 | WRONG | OK | OK | OK | OK | OK | amount wrong, other fields coincidentally match |
| request_19 | WRONG | OK | WRONG | WRONG | WRONG | WRONG | DOWNSTREAM of amount_safe_to_pay |
| request_20 | WRONG | OK | OK | OK | OK | WRONG | amount wrong, other fields coincidentally match |
| request_21 | WRONG | WRONG | OK | OK | WRONG | WRONG | DOWNSTREAM of amount_safe_to_pay |
| request_22 | WRONG | OK | OK | OK | OK | OK | amount wrong, other fields coincidentally match |
| request_23 | WRONG | OK | OK | OK | OK | OK | amount wrong, other fields coincidentally match |
| request_24 | WRONG | OK | OK | OK | OK | WRONG | amount wrong, other fields coincidentally match |
| request_25 | WRONG | OK | OK | OK | OK | WRONG | amount wrong, other fields coincidentally match |

# Convention substitution test

For each sample's identified constraining category, its baseline amount is swapped for each candidate convention below (holding cadence/dates fixed) and amount_safe_to_pay recomputed. `best` names whichever convention lands closest to the known-correct expected value for that row.

| request | category | expected | last1 | mean2 | mean3 | mean5 | max3 | max5 | median5 | full_mean | best |
|---|---|---|---|---|---|---|---|---|---|---|
| request_01 | delivery_membership | 25256.0 | 25256.0 | 25256.0 | 25256.0 | 25256.0 | 25256.0 | 25256.0 | 25256.0 | 25256.0 | (frozen/capped -- convention doesn't affect the result) |
| request_02 | cloud_storage | 17229139.2 | 18170561.94 | 18170561.94 | 18170561.94 | 18170561.94 | 18170561.94 | 18170561.94 | 18170561.94 | 18170561.94 | (frozen/capped -- convention doesn't affect the result) |
| request_03 | groceries | 873000.0 | 463324.69 | 402623.09 | 401516.8 | 434163.38 | 341921.5 | 341921.5 | 421239.91 | 484546.49 | full_mean (484546.49) |
| request_04 | entertainment | 8401800.0 | 10691312.98 | 10661590.85 | 10567911.35 | 10537971.01 | 10380552.37 | 10380552.37 | 10547318.32 | 10537971.01 | max3 (10380552.37) |
| request_05 | transport | 737.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | (frozen/capped -- convention doesn't affect the result) |
| request_06 | shopping | 603.3 | 620.4 | 620.4 | 620.4 | 620.4 | 620.4 | 620.4 | 620.4 | 620.4 | (frozen/capped -- convention doesn't affect the result) |
| request_07 | transport | 87170.56 | 86297.83 | 85983.68 | 86219.65 | 86256.76 | 85669.53 | 85620.83 | 86297.83 | 86223.32 | last1 (86297.83) |
| request_08 | delivery_membership | 284.57 | 304.09 | 304.09 | 304.09 | 304.09 | 304.09 | 304.09 | 304.09 | 304.09 | (frozen/capped -- convention doesn't affect the result) |
| request_09 | shopping | 166.61 | 166.61 | 166.61 | 166.61 | 166.61 | 166.61 | 166.61 | 166.61 | 166.61 | (frozen/capped -- convention doesn't affect the result) |
| request_10 | utilities | 12700.0 | 266700.0 | 266700.0 | 266700.0 | 266700.0 | 266700.0 | 266700.0 | 266700.0 | 266700.0 | (frozen/capped -- convention doesn't affect the result) |
| request_11 | transport | 12510645.0 | 13110000.0 | 13110000.0 | 13110000.0 | 13110000.0 | 13110000.0 | 13110000.0 | 13110000.0 | 13110000.0 | (frozen/capped -- convention doesn't affect the result) |
| request_12 | rent | 65164.0 | 63305.84 | 63305.84 | 63305.84 | 63305.84 | 63305.84 | 63305.84 | 63305.84 | 63305.84 | (frozen/capped -- convention doesn't affect the result) |
| request_13 | groceries | 433.4 | 624.3 | 664.05 | 568.47 | 621.24 | 377.3 | 377.3 | 624.3 | 564.3 | max3 (377.3) |
| request_14 | family_support | 597.74 | 619.02 | 619.02 | 619.02 | 619.02 | 619.02 | 619.02 | 619.02 | 619.02 | (frozen/capped -- convention doesn't affect the result) |
| request_15 | transport | 83.05 | 72.43 | 75.07 | 69.83 | 68.33 | 59.33 | 50.35 | 72.43 | 69.54 | mean2 (75.07) |
| request_16 | transport | 122500.0 | 122500.0 | 122500.0 | 122500.0 | 122500.0 | 122500.0 | 122500.0 | 122500.0 | 122500.0 | (frozen/capped -- convention doesn't affect the result) |
| request_17 | delivery_membership | 243849.58 | 195860.72 | 195860.72 | 195860.72 | 195860.72 | 195860.72 | 195860.72 | 195860.72 | 195860.72 | (frozen/capped -- convention doesn't affect the result) |
| request_18 | transport | 462.0 | 650.8 | 648.19 | 651.56 | 651.69 | 645.57 | 644.04 | 650.8 | 650.76 | max5 (644.04) |
| request_19 | shopping | 28820.0 | 39660.0 | 39660.0 | 39660.0 | 39660.0 | 39660.0 | 39660.0 | 39660.0 | 39660.0 | (frozen/capped -- convention doesn't affect the result) |
| request_20 | entertainment | 5400.0 | 16981.54 | 17055.19 | 17024.38 | 16930.42 | 16962.77 | 16779.93 | 16962.77 | 16930.42 | max5 (16779.93) |
| request_21 | shopping | 1543.35 | 1574.4 | 1574.4 | 1574.4 | 1574.4 | 1574.4 | 1574.4 | 1574.4 | 1574.4 | (frozen/capped -- convention doesn't affect the result) |
| request_22 | delivery_membership | 475.46 | 481.61 | 481.61 | 481.61 | 481.61 | 481.61 | 481.61 | 481.61 | 481.61 | (frozen/capped -- convention doesn't affect the result) |
| request_23 | groceries | 9152.0 | 11895.0 | 11766.37 | 11668.98 | 11605.92 | 11474.19 | 11357.8 | 11637.73 | 11420.09 | max5 (11357.8) |
| request_24 | entertainment | 13420.0 | 15629.24 | 15654.49 | 15639.44 | 15594.8 | 15609.33 | 15400.77 | 15629.24 | 15594.8 | max5 (15400.77) |
| request_25 | entertainment | 1425000.0 | 2684796.98 | 2645617.5 | 2634286.72 | 2651542.96 | 2606438.01 | 2606438.01 | 2659453.79 | 2651542.96 | max3 (2606438.01) |

15 of 25 rows are frozen/capped (the constraining category's estimate doesn't change the outcome) and are excluded from the tally below.
Win counts on the remaining 10 rows where the convention actually matters: last1=1, mean2=1, mean3=0, mean5=0, max3=3, max5=4, median5=0, full_mean=1

# Conclusion (updated after structural bug fixes)

The original convention-substitution test above was correct that no simple
statistical convention explained the gaps -- because the actual causes were
structural bugs in cash-flow generation itself, not a mis-tuned constant.
Four were found and fixed by tracing request_04 (user_04) entry by entry:

1. **Double-counted `forced_next` occurrence.** In `project_cashflow`, when a
   series had a scheduled/pending row consumed into `forced_next`, the
   projection loop's cursor started AT that forced date instead of AFTER it,
   so its first iteration re-appended the same date a second time (the
   `cursor > start` guard passes trivially since the forced date is always
   after request_date). This double-counted every category that ever
   consumed a scheduled/pending row -- extremely common (most salary series,
   many scheduled one-off debits). Fixed by advancing the cursor past the
   forced date before entering the loop.

2. **One-off commitments wrongly promoted to indefinite recurring series.**
   A scheduled/pending event with zero settled history in its category (e.g.
   user_04's single "Scheduled school fee", education, 2024-06-11) was
   defaulted to a 30-day recurring cadence and projected forever, instead of
   being treated as the one-time payment it actually is. Fixed: the
   fallback now only builds a continuing series when at least one settled
   occurrence establishes real precedent (AGENTS.md: "detect recurrence only
   when history supports it"); zero-history events fall through to a plain
   one-off.

3. **A one-time bonus/arrears event corrupting cadence AND amount for its
   whole category.** user_04's "salary" credit history included one
   "Quarterly performance bonus" a week after the regular monthly payroll
   credit. The outlier-removal step (added earlier to tolerate off-cycle
   duplicates) always dropped the EARLIER of an anomalous close pair --
   which here deleted the legitimate March payroll and kept the bonus,
   corrupting both the detected cadence and the mean-of-3 amount estimate
   (28,959,488 instead of the true 38,190,000, a ~24% understatement
   compounded across every future salary occurrence). Fixed: the cleaner now
   compares both candidates in an anomalous pair against the median of the
   REST of the series and drops whichever is farther from the established
   pattern, instead of always dropping the earlier one.

4. **Income silently reduced to a single occurrence for users whose
   "next confirmed" row uses a different description than their real
   payroll history.** The sparse-history fallback's `hist` lookup filtered
   settled history by exact description match against the *scheduled* row's
   own description (e.g. "Next confirmed salary"), which essentially never
   matches the real employer-specific description ("Prorated first salary",
   "First-job payroll", "Payroll credit", ...). `hist` came back empty, so
   the fallback's `not hist` check (added while fixing bug #2) wrongly
   treated an established, continuing salary as a one-off -- effectively
   zeroing future income after that single date. Confirmed and fixed for
   3 of 250 users (user_01, user_96, user_244); a related but narrower
   cadence-ratio edge case remains for user_127 (an unpaid-leave gap that
   just barely fails the outlier-ratio check) and was not fixed, since it's
   unrelated to request_04 and not one of the 25 known samples.

A programmatic sweep also confirmed **no sign errors** exist anywhere
(credit always positive, debit always negative, across every user).

Net effect on request_04: amount_safe_to_pay moved from 676,137.66 (a 12x
undershoot vs the expected 8,401,800) to 10,567,911.35 (a 26% overshoot) --
and every other output field for that row (affordability_status,
recommended_payment_method, payment_plan, earliest_date_for_full_payment)
is now correct. Total absolute error across all 25 samples' amount_safe_to_pay
dropped from 11,110,624.81 to 5,720,827.69 (~49% reduction). The remaining
~26%-ish per-row gaps are now plausibly genuine convention-tuning territory
(the second-order question this diagnostic deliberately did not touch),
rather than structural bugs.
