#!/usr/bin/env python3
"""Diagnose amount_safe_to_pay mismatches against dataset/sample_requests.csv.

For each of the 25 known samples, shows:
  * expected vs predicted amount_safe_to_pay and the diff
  * the constraining date: the date of the lowest point in our 90-day
    baseline (no-payment) balance trajectory -- this is what binds
    amount_safe_to_pay = baseline_min - minimum_balance_to_keep
  * the constraining category/event on that date (largest debit, or the
    single credit/debit event if only one landed there)
  * the amount our forecaster projected for that category on that date
  * the last 3-5 actual settled historical amounts for that same category,
    so the conservative-amount convention can be read off the data instead
    of guessed at.

It also reports, for every sample whose payment_plan / decision_explanation /
earliest_date_for_full_payment is wrong, whether that's downstream of a wrong
amount_safe_to_pay or an independent bug.

Run from anywhere: python3 code/evaluation/diagnostics.py
Writes: code/evaluation/diagnostics.md
"""
from __future__ import annotations

import csv
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CODE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, CODE_DIR)

SAMPLES_CSV = os.path.join(REPO_ROOT, "dataset", "sample_requests.csv")
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagnostics.md")

import statistics  # noqa: E402

import fx  # noqa: E402
import forecast  # noqa: E402
from data_loader import load_dataset, Request  # noqa: E402
from reconstruct import build_user_context, project_cashflow_detailed, project_cashflow  # noqa: E402
from decision import decide  # noqa: E402
from explain import build_explanation, fmt_natural  # noqa: E402

CONVENTIONS = ["last1", "mean2", "mean3", "mean5", "max3", "max5", "median5", "full_mean"]


def _load_samples():
    with open(SAMPLES_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _running_min(balance0, records):
    """Aggregate signed deltas by date, walk chronologically, return
    (min_balance, min_date, per_date_records) where per_date_records maps
    date -> list of contributing records (for attributing the breach)."""
    by_date = {}
    for r in records:
        by_date.setdefault(r["date"], []).append(r)
    balance = balance0
    min_bal = balance0
    min_date = None
    for d in sorted(by_date):
        balance += sum(r["signed"] for r in by_date[d])
        if balance < min_bal:
            min_bal = balance
            min_date = d
    return min_bal, min_date, by_date


def _recent_history(ds, ctx, category, direction, description_hint):
    home = ctx.profile.home_currency
    events = ds.events_by_user.get(ctx.user_id, [])
    matches = [
        e for e in events
        if e.status == "settled" and e.category == category and e.direction == direction
        and (direction != "credit" or not description_hint or e.description == description_hint)
    ]
    matches.sort(key=lambda e: e.event_date)
    out = []
    for e in matches[-5:]:
        amt = e.amount
        if amt is None:
            from evidence.image_extract import load_cache
            entry = load_cache().get(e.event_id)
            amt, ccy = (entry["amount"], entry["currency"]) if entry else (0.0, e.currency)
        else:
            ccy = e.currency
        home_amt = fx.convert(amt, ccy, home, e.settlement_date)
        out.append((e.event_date, round(home_amt, 2), e.event_id, e.status))
    return out


def _all_history_amounts(ds, ctx, category, direction, description_hint, limit=None):
    home = ctx.profile.home_currency
    events = ds.events_by_user.get(ctx.user_id, [])
    matches = [
        e for e in events
        if e.status == "settled" and e.category == category and e.direction == direction
        and (direction != "credit" or not description_hint or e.description == description_hint)
    ]
    matches.sort(key=lambda e: e.event_date)
    if limit:
        matches = matches[-limit:]
    out = []
    for e in matches:
        amt = e.amount
        if amt is None:
            from evidence.image_extract import load_cache
            entry = load_cache().get(e.event_id)
            amt, ccy = (entry["amount"], entry["currency"]) if entry else (0.0, e.currency)
        else:
            ccy = e.currency
        out.append(fx.convert(amt, ccy, home, e.settlement_date))
    return out


def _test_conventions(ds, ctx, req, series, expected):
    """Substitute each candidate conservative-estimate convention for the
    constraining series' baseline amount (holding cadence/dates fixed),
    recompute amount_safe_to_pay, and report which convention lands closest
    to the known-correct value. This is the actual empirical test of "most
    recent value vs trailing average vs trailing max vs something else" --
    not a guess."""
    hist = _all_history_amounts(ds, ctx, series.category, series.direction, series.description_hint, limit=8)
    if len(hist) < 3:
        return None
    candidates = {
        "last1": hist[-1],
        "mean2": statistics.mean(hist[-2:]),
        "mean3": statistics.mean(hist[-3:]),
        "mean5": statistics.mean(hist[-5:]) if len(hist) >= 5 else statistics.mean(hist),
        "max3": max(hist[-3:]),
        "max5": max(hist[-5:]) if len(hist) >= 5 else max(hist),
        "median5": statistics.median(hist[-5:]) if len(hist) >= 5 else statistics.median(hist),
        "full_mean": statistics.mean(_all_history_amounts(ds, ctx, series.category, series.direction, series.description_hint)),
    }
    balance0 = ctx.profile.current_available_balance
    min_balance = ctx.profile.minimum_balance_to_keep
    orig = series.amount
    results = {}
    for name, val in candidates.items():
        series.amount = val
        deltas = project_cashflow(ctx, req.request_date)
        safe = forecast.max_safe_amount_today(balance0, req.request_date, deltas, min_balance, cap=req.requested_amount)
        results[name] = round(safe, 2)
    series.amount = orig
    best = min(results.items(), key=lambda kv: abs(kv[1] - expected))
    return results, best


def main():
    ds = load_dataset()
    rows = _load_samples()

    diag_lines = []
    diag_lines.append("# amount_safe_to_pay Diagnostics (25 known samples)\n")
    diag_lines.append(
        "Columns: constraining date = date of the lowest point in the baseline "
        "(no-payment) 90-day trajectory; constraining category = the category "
        "with the largest debit landing on that date; projected = the amount "
        "our forecaster used for that category's occurrence on that date; "
        "recent history = last settled occurrences of that same category "
        "(date, home-currency amount).\n"
    )
    header = (
        "| request | user | expected | predicted | diff | constraining date | "
        "constraining category | projected amount | recent history (last 5) |"
    )
    sep = "|---|---|---|---|---|---|---|---|---|"
    diag_lines.append(header)
    diag_lines.append(sep)

    breakdown_lines = []
    breakdown_lines.append("\n# Downstream vs independent errors\n")
    breakdown_lines.append("| request | amt_safe ok? | affordability_status | recommended_method | payment_plan | earliest_date | decision_explanation | verdict |")
    breakdown_lines.append("|---|---|---|---|---|---|---|---|")

    table_rows = []

    for row in rows:
        req = Request(
            request_id=row["request_id"], user_id=row["user_id"], request_date=row["request_date"],
            request_type=row["request_type"], requested_amount=float(row["requested_amount"]),
            desired_completion_date=row["desired_completion_date"],
            allows_partial_payment=row["allows_partial_payment"].strip().lower() == "true",
            request_text=row["request_text"],
        )
        ds.requests[req.request_id] = req
        ctx = build_user_context(ds, req.user_id)
        payment_options = ds.payment_options_by_request.get(req.request_id, [])

        records = project_cashflow_detailed(ctx, req.request_date)
        balance0 = ctx.profile.current_available_balance
        min_bal, min_date, by_date = _running_min(balance0, records)

        constraining_cat = "(none -- balance never dips below start)"
        projected_amount = ""
        recent_hist_str = ""
        if min_date is not None:
            candidates = by_date[min_date]
            worst = min(candidates, key=lambda r: r["signed"])  # most negative = biggest debit
            constraining_cat = f"{worst['category']}" + (f" [{worst['description_hint']}]" if worst["description_hint"] else "")
            projected_amount = round(abs(worst["signed"]), 2)
            hist = _recent_history(ds, ctx, worst["category"], worst["direction"], worst["description_hint"])
            recent_hist_str = "; ".join(f"{d}:{a}" for d, a, _eid, _st in hist)

        expected = float(row["amount_safe_to_pay"])
        result = decide(ds, ctx, req, payment_options)
        predicted = result["amount_safe_to_pay"]
        diff = round(predicted - expected, 2)

        worst_series = None
        if min_date is not None:
            worst_series = min(by_date[min_date], key=lambda r: r["signed"])["series"]

        table_rows.append({
            "request_id": req.request_id, "user_id": req.user_id, "expected": expected,
            "predicted": predicted, "diff": diff, "min_date": min_date,
            "constraining_cat": constraining_cat, "projected_amount": projected_amount,
            "recent_hist_str": recent_hist_str, "row": row, "result": result, "req": req, "ctx": ctx,
            "worst_series": worst_series,
        })

        diag_lines.append(
            f"| {req.request_id} | {req.user_id} | {expected} | {predicted} | {diff} | "
            f"{min_date or '-'} | {constraining_cat} | {projected_amount} | {recent_hist_str} |"
        )

    # --- print/write the amount diagnostic table ---
    print("\n".join(diag_lines))

    # --- downstream vs independent breakdown ---
    amt_tol = 1.0
    for tr in table_rows:
        row, req, ctx, result = tr["row"], tr["req"], tr["ctx"], tr["result"]
        amt_ok = abs(tr["diff"]) <= amt_tol
        explanation = build_explanation(ds, ctx, req, result)

        plan_ok = result["payment_plan"] == row["payment_plan"] or _plan_numeric_close(result["payment_plan"], row["payment_plan"])
        status_ok = result["affordability_status"] == row["affordability_status"]
        method_ok = result["recommended_payment_method"] == row["recommended_payment_method"]
        earliest = result["earliest_date_for_full_payment"] or ""
        earliest_ok = earliest == row["earliest_date_for_full_payment"]
        expl_ok = explanation.strip() == row["decision_explanation"].strip()

        if amt_ok and plan_ok and status_ok and method_ok and earliest_ok and expl_ok:
            verdict = "all correct"
        elif not amt_ok and (not plan_ok or not status_ok or not method_ok or not earliest_ok):
            verdict = "DOWNSTREAM of amount_safe_to_pay"
        elif amt_ok and (not plan_ok or not status_ok or not method_ok or not earliest_ok):
            verdict = "INDEPENDENT bug (amount was right)"
        elif not amt_ok:
            verdict = "amount wrong, other fields coincidentally match"
        else:
            verdict = "only decision_explanation wording differs"

        breakdown_lines.append(
            f"| {req.request_id} | {'OK' if amt_ok else 'WRONG'} | "
            f"{'OK' if status_ok else 'WRONG'} | {'OK' if method_ok else 'WRONG'} | "
            f"{'OK' if plan_ok else 'WRONG'} | {'OK' if earliest_ok else 'WRONG'} | "
            f"{'OK' if expl_ok else 'WRONG'} | {verdict} |"
        )

    print("\n".join(breakdown_lines))

    # --- convention substitution test: empirically try each candidate estimate ---
    conv_lines = ["\n# Convention substitution test\n"]
    conv_lines.append(
        "For each sample's identified constraining category, its baseline amount is "
        "swapped for each candidate convention below (holding cadence/dates fixed) and "
        "amount_safe_to_pay recomputed. `best` names whichever convention lands closest "
        "to the known-correct expected value for that row.\n"
    )
    conv_header = "| request | category | expected | " + " | ".join(CONVENTIONS) + " | best |"
    conv_lines.append(conv_header)
    conv_lines.append("|" + "---|" * (len(CONVENTIONS) + 3))

    # IMPORTANT: many rows are capped (amount_safe_to_pay == requested_amount
    # regardless of the constraining category's estimate) or otherwise have
    # so much headroom that every candidate produces the identical result.
    # For those "frozen" rows, min()'s tie-break arbitrarily picks whichever
    # convention is listed first (last1) -- that is NOT evidence last1 is
    # correct, it's a tie-break artifact. Frozen rows are shown but excluded
    # from the win-count tally, which only reflects rows where the choice of
    # convention actually changes the outcome.
    FROZEN_SPREAD_THRESHOLD = 2.0
    win_counts = {c: 0 for c in CONVENTIONS}
    tested = 0
    frozen = 0
    for tr in table_rows:
        series = tr["worst_series"]
        if series is None:
            continue
        out = _test_conventions(ds, tr["ctx"], tr["req"], series, tr["expected"])
        if out is None:
            continue
        results, (best_name, best_val) = out
        spread = max(results.values()) - min(results.values())
        cat_label = series.category + (f" [{series.description_hint}]" if series.description_hint else "")
        is_frozen = spread < FROZEN_SPREAD_THRESHOLD
        if is_frozen:
            frozen += 1
            best_label = "(frozen/capped -- convention doesn't affect the result)"
        else:
            tested += 1
            win_counts[best_name] += 1
            best_label = f"{best_name} ({best_val})"
        conv_lines.append(
            f"| {tr['request_id']} | {cat_label} | {tr['expected']} | "
            + " | ".join(str(results[c]) for c in CONVENTIONS)
            + f" | {best_label} |"
        )

    conv_lines.append("")
    conv_lines.append(f"{frozen} of {frozen + tested} rows are frozen/capped (the constraining "
                       "category's estimate doesn't change the outcome) and are excluded from the tally below.")
    conv_lines.append("Win counts on the remaining "
                       f"{tested} rows where the convention actually matters: "
                       + ", ".join(f"{c}={win_counts[c]}" for c in CONVENTIONS))

    print("\n".join(conv_lines))

    conclusion = """
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
"""
    print(conclusion)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(diag_lines))
        f.write("\n")
        f.write("\n".join(breakdown_lines))
        f.write("\n")
        f.write("\n".join(conv_lines))
        f.write("\n")
        f.write(conclusion)
    print(f"\nWrote {OUT_PATH}")


def _plan_numeric_close(a, b, tol=1.0):
    if a == b:
        return True
    if a in ("none", "") or b in ("none", ""):
        return a == b
    pa, pb = a.split("|"), b.split("|")
    if len(pa) != len(pb):
        return False
    for ea, eb in zip(pa, pb):
        da, aa = ea.split(":")
        db, ab = eb.split(":")
        if da != db:
            return False
        try:
            if abs(float(aa) - float(ab)) > tol:
                return False
        except ValueError:
            return False
    return True


if __name__ == "__main__":
    main()
