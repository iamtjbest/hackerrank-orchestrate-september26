"""Eligibility + ranking rules (problem_statement.md / AGENTS.md §6.3), applied literally."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional, Tuple

import forecast
from explain import fmt_plan_amount
from reconstruct import project_cashflow

MAX_SPENDING_CHANGES = 3


def _parse(d: str) -> date:
    y, m, dd = d.split("-")
    return date(int(y), int(m), int(dd))


def _fmt(d: date) -> str:
    return d.strftime("%Y-%m-%d")


@dataclass
class Candidate:
    method: str  # full_payment | partial_payment | installments | wait
    plan: List[Tuple[str, float]]
    spending_changes: List[dict]
    completes_by_deadline: bool
    total_paid: float
    start_date: str
    num_payments: int
    payment_option_id: Optional[str] = None

    def sort_key(self):
        opt_num = 10**9
        if self.payment_option_id:
            digits = "".join(c for c in self.payment_option_id if c.isdigit())
            opt_num = int(digits) if digits else 10**9
        return (
            0 if self.completes_by_deadline else 1,
            0 if not self.spending_changes else 1,
            round(self.total_paid, 6),
            self.start_date,
            self.num_payments,
            opt_num,
        )


def _flexible_candidates(ctx, profile):
    """One candidate spending action per eligible flexible recurring series:
    stop or reduce_to, whichever frees more, restricted to categories the
    user actually permits and that are not protected."""
    actions = []
    for series in ctx.recurring:
        if series.direction != "debit":
            continue
        if series.category in profile.expense_categories_to_protect:
            continue
        can_stop = (
            series.flexibility in ("stoppable", "reducible_or_stoppable")
            and series.category in profile.expense_categories_user_is_willing_to_stop
        )
        can_reduce = (
            series.flexibility in ("reducible", "reducible_or_stoppable")
            and series.category in profile.expense_categories_user_is_willing_to_reduce
            and series.minimum_allowed_amount is not None
        )
        if can_stop and can_reduce:
            freed_stop = series.amount
            freed_reduce = series.amount - series.minimum_allowed_amount
            if freed_stop >= freed_reduce:
                actions.append({"action": "stop", "event_id": series.last_event_id, "freed": freed_stop})
            else:
                actions.append({"action": "reduce_to", "event_id": series.last_event_id,
                                 "new_amount": series.minimum_allowed_amount, "freed": freed_reduce})
        elif can_stop:
            actions.append({"action": "stop", "event_id": series.last_event_id, "freed": series.amount})
        elif can_reduce:
            actions.append({"action": "reduce_to", "event_id": series.last_event_id,
                             "new_amount": series.minimum_allowed_amount,
                             "freed": series.amount - series.minimum_allowed_amount})
    actions.sort(key=lambda a: a["event_id"])
    return actions


def _minimal_spending_changes_for_full_today(ctx, request, balance0, min_balance, actions):
    """Smallest (deterministic) subset of up to MAX_SPENDING_CHANGES actions
    that makes the full requested amount safe to pay on request_date."""
    from itertools import combinations
    for size in range(1, MAX_SPENDING_CHANGES + 1):
        for combo in combinations(actions, size):
            deltas = project_cashflow(ctx, request.request_date, spending_changes=list(combo))
            if forecast.is_amount_safe_on_date(balance0, deltas, min_balance, request.request_date, request.requested_amount):
                return list(combo)
    return None


def _installment_duration_months(option) -> float:
    if option.number_of_payments <= 1:
        return 0.0
    span_days = (option.number_of_payments - 1) * (option.payment_frequency_days or 0)
    return span_days / 30.44


def decide(ds, ctx, request, payment_options: List) -> dict:
    profile = ctx.profile
    balance0 = profile.current_available_balance
    min_balance = profile.minimum_balance_to_keep
    accepted = profile.payment_methods_user_will_consider

    baseline_deltas = project_cashflow(ctx, request.request_date)
    amount_safe_to_pay = forecast.max_safe_amount_today(
        balance0, request.request_date, baseline_deltas, min_balance, cap=request.requested_amount
    )
    earliest_date = forecast.earliest_safe_full_payment_date(
        balance0, request.request_date, baseline_deltas, request.requested_amount, min_balance
    )

    candidates: List[Candidate] = []
    deadline = request.desired_completion_date

    # --- full_payment today, no spending changes ---
    if "full_payment" in accepted and amount_safe_to_pay >= request.requested_amount - 1e-6:
        candidates.append(Candidate(
            method="full_payment", plan=[(request.request_date, request.requested_amount)],
            spending_changes=[], completes_by_deadline=request.request_date <= deadline,
            total_paid=request.requested_amount, start_date=request.request_date, num_payments=1,
        ))

    # --- full_payment today, WITH spending changes ---
    if "full_payment" in accepted and amount_safe_to_pay < request.requested_amount - 1e-6:
        actions = _flexible_candidates(ctx, profile)
        combo = _minimal_spending_changes_for_full_today(ctx, request, balance0, min_balance, actions)
        if combo:
            combo = [{"action": a["action"], "event_id": a["event_id"], "new_amount": a.get("new_amount")} for a in combo]
            candidates.append(Candidate(
                method="full_payment", plan=[(request.request_date, request.requested_amount)],
                spending_changes=combo, completes_by_deadline=request.request_date <= deadline,
                total_paid=request.requested_amount, start_date=request.request_date, num_payments=1,
            ))

    # --- wait: full payment later, no spending changes ---
    if "full_payment" in accepted and earliest_date is not None and earliest_date != request.request_date:
        candidates.append(Candidate(
            method="wait", plan=[(earliest_date, request.requested_amount)],
            spending_changes=[], completes_by_deadline=earliest_date <= deadline,
            total_paid=request.requested_amount, start_date=earliest_date, num_payments=1,
        ))

    # --- partial_payment ---
    if (
        request.allows_partial_payment
        and "partial_payment" in accepted
        and 0 < amount_safe_to_pay < request.requested_amount - 1e-9
    ):
        remainder = request.requested_amount - amount_safe_to_pay
        start = _parse(request.request_date)
        for offset in range(0, forecast.HORIZON_DAYS + 1):
            d = _fmt(start + timedelta(days=offset))
            if d > deadline:
                break
            schedule = [(request.request_date, amount_safe_to_pay), (d, remainder)]
            if forecast.min_balance_with_schedule(balance0, baseline_deltas, schedule) >= min_balance:
                candidates.append(Candidate(
                    method="partial_payment", plan=schedule, spending_changes=[],
                    completes_by_deadline=d <= deadline, total_paid=request.requested_amount,
                    start_date=request.request_date, num_payments=2,
                ))
                break

    # --- installments ---
    if "installments" in accepted and profile.max_installment_months:
        for opt in payment_options:
            if opt.payment_method != "installments":
                continue
            if _installment_duration_months(opt) > profile.max_installment_months + 1e-9:
                continue
            schedule = []
            d = _parse(opt.first_payment_date)
            for i in range(opt.number_of_payments):
                schedule.append((_fmt(d), opt.payment_amount))
                d = d + timedelta(days=opt.payment_frequency_days or 0)
            if forecast.min_balance_with_schedule(balance0, baseline_deltas, schedule) >= min_balance:
                last_date = schedule[-1][0]
                candidates.append(Candidate(
                    method="installments", plan=schedule, spending_changes=[],
                    completes_by_deadline=last_date <= deadline,
                    total_paid=opt.total_payable_amount, start_date=schedule[0][0],
                    num_payments=opt.number_of_payments, payment_option_id=opt.payment_option_id,
                ))

    result = {
        "amount_safe_to_pay": round(min(amount_safe_to_pay, request.requested_amount), 2),
        "earliest_date_for_full_payment": earliest_date,
    }

    if not candidates:
        result.update({
            "affordability_status": "not_affordable",
            "recommended_payment_method": "not_recommended",
            "payment_plan": "none",
            "spending_changes_needed": "none",
            "chosen": None,
        })
        return result

    candidates.sort(key=lambda c: c.sort_key())
    chosen = candidates[0]

    if chosen.method == "wait":
        status = "affordable_later"
    elif chosen.method == "full_payment" and chosen.start_date == request.request_date:
        status = "affordable_now" if not chosen.spending_changes else "affordable_with_plan"
    else:
        status = "affordable_with_plan"

    spending_str = "none"
    if chosen.spending_changes:
        parts = []
        for c in chosen.spending_changes:
            if c["action"] == "stop":
                parts.append(f"stop:{c['event_id']}")
            else:
                parts.append(f"reduce_to:{c['event_id']}:{fmt_plan_amount(c['new_amount'])}")
        spending_str = "|".join(parts)

    plan_str = "|".join(f"{d}:{fmt_plan_amount(amt)}" for d, amt in chosen.plan)

    result.update({
        "affordability_status": status,
        "recommended_payment_method": chosen.method,
        "payment_plan": plan_str,
        "spending_changes_needed": spending_str,
        "chosen": chosen,
    })
    return result
