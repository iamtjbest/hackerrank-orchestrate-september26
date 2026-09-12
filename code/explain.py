"""Template-based decision_explanation generation.

Built entirely from the numbers decision.py already computed -- never a
freeform LLM description -- so the explanation can never drift from the
values actually written to the other output columns.
"""
from __future__ import annotations

from datetime import date


def _parse(d: str) -> date:
    y, m, dd = d.split("-")
    return date(int(y), int(m), int(dd))


def _human_date(d: str) -> str:
    dt = _parse(d)
    return f"{dt.day} {dt.strftime('%B')} {dt.year}"


def fmt_money(x: float) -> str:
    if x is None:
        return ""
    rounded = round(x, 2)
    if abs(rounded - round(rounded)) < 1e-9:
        return f"{int(round(rounded)):,}"
    return f"{rounded:,.2f}"


def fmt_natural(x: float) -> str:
    """No thousands separator, minimal decimals (Python's natural float
    string), matching the amount_safe_to_pay column convention: "603.3",
    "87170.56", "9152" -- never zero-padded."""
    if x is None:
        return ""
    rounded = round(x, 2)
    if abs(rounded - round(rounded)) < 1e-9:
        return str(int(round(rounded)))
    return str(rounded)


def fmt_plan_amount(x: float) -> str:
    """No thousands separator, 2dp only when the value has a fractional
    part -- matches the payment_plan / amount_safe_to_pay convention seen in
    dataset/sample_requests.csv (e.g. "620.40" but "68432", not "68432.00")."""
    if x is None:
        return ""
    rounded = round(x, 2)
    if abs(rounded - round(rounded)) < 1e-9:
        return str(int(round(rounded)))
    return f"{rounded:.2f}"


def build_explanation(ds, ctx, request, result: dict) -> str:
    ccy = ctx.profile.home_currency
    min_balance = ctx.profile.minimum_balance_to_keep
    chosen = result.get("chosen")

    if chosen is None:
        deadline_human = _human_date(request.desired_completion_date)
        if result["earliest_date_for_full_payment"] is None:
            return (
                f"Do not proceed with the {ccy} {fmt_money(request.requested_amount)} request. "
                f"Although {ccy} {fmt_money(result['amount_safe_to_pay'])} is available today, "
                f"the full amount cannot be completed safely within 90 days."
            )
        return (
            f"Do not make this payment by {deadline_human}. "
            f"None of the available options keeps the {ccy} {fmt_money(min_balance)} minimum protected."
        )

    method = chosen.method

    if method == "wait":
        pay_date = _human_date(chosen.plan[0][0])
        return (
            f"Pay {ccy} {fmt_money(chosen.plan[0][1])} in full on {pay_date}. "
            f"Paying earlier would take the balance below the {ccy} {fmt_money(min_balance)} minimum."
        )

    if method == "installments":
        n = chosen.num_payments
        amt = chosen.plan[0][1]
        start_human = _human_date(chosen.start_date)
        return (
            f"Use {n} installments of {ccy} {fmt_money(amt)}, starting {start_human}. "
            f"This leaves at least {ccy} {fmt_money(min_balance)} available."
        )

    if method == "partial_payment":
        first_amt, second_amt = chosen.plan[0][1], chosen.plan[1][1]
        second_date = _human_date(chosen.plan[1][0])
        return (
            f"Pay {ccy} {fmt_money(first_amt)} today and the remaining {ccy} {fmt_money(second_amt)} on {second_date}. "
            f"This completes the full request and keeps the {ccy} {fmt_money(min_balance)} minimum protected."
        )

    # full_payment (today), possibly with spending changes.
    if chosen.spending_changes:
        pieces = []
        for c in chosen.spending_changes:
            ev = ds.events.get(c["event_id"])
            desc = (ev.description if ev else c["event_id"]).lower()
            if c["action"] == "stop":
                pieces.append(f"Stop the {desc}")
            else:
                pieces.append(f"reduce the {desc} to {ccy} {fmt_money(c['new_amount'])}")
        lead = " and ".join(pieces)
        lead = lead[0].upper() + lead[1:]
        return (
            f"{lead}, then pay {ccy} {fmt_money(chosen.plan[0][1])} today. "
            f"This leaves at least {ccy} {fmt_money(min_balance)} available."
        )

    return (
        f"Pay {ccy} {fmt_money(chosen.plan[0][1])} today. "
        f"This leaves at least {ccy} {fmt_money(min_balance)} available over the next 90 days."
    )
