"""Pure 90-day-forward daily balance simulator.

Balance only changes on days with a cash-flow event, so the minimum balance
over the forecast window is just the running minimum after each
chronologically-ordered (same-day events summed together) delta -- no need
for a literal day-by-day loop.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import List, Optional, Tuple

HORIZON_DAYS = 90


def _parse(d: str) -> date:
    y, m, dd = d.split("-")
    return date(int(y), int(m), int(dd))


def _fmt(d: date) -> str:
    return d.strftime("%Y-%m-%d")


def _aggregate(events: List[Tuple[str, float]]):
    agg = defaultdict(float)
    for d, delta in events:
        agg[d] += delta
    return sorted(agg.items())


def min_balance_with_payment(
    balance0: float,
    deltas: List[Tuple[str, float]],
    payment_date: Optional[str] = None,
    payment_amount: float = 0.0,
) -> float:
    """Minimum balance over the whole window, including today's opening
    balance, after inserting a single payment of `payment_amount` (a debit)
    on `payment_date`. Pass payment_amount=0 to check the baseline trajectory."""
    events = list(deltas)
    if payment_date is not None and payment_amount:
        events.append((payment_date, -payment_amount))
    balance = balance0
    min_bal = balance0
    for _, delta in _aggregate(events):
        balance += delta
        min_bal = min(min_bal, balance)
    return min_bal


def max_safe_amount_today(
    balance0: float,
    request_date: str,
    deltas: List[Tuple[str, float]],
    minimum_balance_to_keep: float,
    cap: float,
) -> float:
    """Binary search the largest payment (0..cap) payable on request_date
    that keeps the balance >= minimum_balance_to_keep throughout the window."""
    if cap <= 0:
        return 0.0
    if min_balance_with_payment(balance0, deltas, request_date, cap) >= minimum_balance_to_keep:
        return round(cap, 2)
    if min_balance_with_payment(balance0, deltas, request_date, 0.0) < minimum_balance_to_keep:
        return 0.0

    lo, hi = 0.0, cap
    for _ in range(60):
        mid = (lo + hi) / 2
        if min_balance_with_payment(balance0, deltas, request_date, mid) >= minimum_balance_to_keep:
            lo = mid
        else:
            hi = mid
    return round(lo, 2)


def earliest_safe_full_payment_date(
    balance0: float,
    request_date: str,
    deltas: List[Tuple[str, float]],
    requested_amount: float,
    minimum_balance_to_keep: float,
    horizon_days: int = HORIZON_DAYS,
) -> Optional[str]:
    """First date in [request_date, request_date+horizon_days] on which paying
    the full requested_amount keeps the balance safe throughout the window."""
    start = _parse(request_date)
    for offset in range(horizon_days + 1):
        d = _fmt(start + timedelta(days=offset))
        if min_balance_with_payment(balance0, deltas, d, requested_amount) >= minimum_balance_to_keep:
            return d
    return None


def is_amount_safe_on_date(
    balance0: float,
    deltas: List[Tuple[str, float]],
    minimum_balance_to_keep: float,
    payment_date: str,
    payment_amount: float,
) -> bool:
    return min_balance_with_payment(balance0, deltas, payment_date, payment_amount) >= minimum_balance_to_keep


def min_balance_with_schedule(
    balance0: float,
    deltas: List[Tuple[str, float]],
    payments: List[Tuple[str, float]],
) -> float:
    """Like min_balance_with_payment but for a full multi-payment schedule."""
    events = list(deltas) + [(d, -amt) for d, amt in payments]
    balance = balance0
    min_bal = balance0
    for _, delta in _aggregate(events):
        balance += delta
        min_bal = min(min_bal, balance)
    return min_bal
