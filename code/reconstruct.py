"""Reconstruct each user's forward-looking cash-flow model.

Builds, per user:
  * recurring series (income and expense categories) with an empirically
    detected cadence and a conservative per-occurrence amount,
  * one-off future commitments (scheduled events, pending debits),
  * message-derived amendments layered on top of both,
  * blank amounts filled in from the image cache before any of the above.

`project_cashflow` then turns a user's static model into a list of dated,
signed cash deltas (home currency) for a specific forecast window, optionally
applying a proposed set of spending changes (stop / reduce_to).
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple

import fx
from evidence.image_extract import load_cache as load_image_cache
from messages import parse_messages

RECURRING_MIN_OCCURRENCES = 3
RECURRING_MAX_GAP_RATIO = 3.0  # max_gap / min_gap must be <= this to call it "recurring"
RECENT_WINDOW = 8  # how many recent occurrences feed the amount/cadence estimate

EXPENSE_TYPES = {"expense", "subscription", "debt_payment"}
INCOME_TYPES = {"income"}


def _parse(d: str) -> date:
    y, m, dd = d.split("-")
    return date(int(y), int(m), int(dd))


def _fmt(d: date) -> str:
    return d.strftime("%Y-%m-%d")


def _add_month(d: date, months: int = 1) -> date:
    import calendar
    m = d.month - 1 + months
    y = d.year + m // 12
    m = m % 12 + 1
    day = min(d.day, calendar.monthrange(y, m)[1])
    return date(y, m, day)


def _cadence_kind(cadence_days: int) -> str:
    """Most monthly bills/salaries land on the same day-of-month, so a fixed
    28-31 day step drifts across several cycles. Treat anything in that band
    as calendar-monthly (advance by month, preserving day-of-month) instead
    of literal day-count addition; everything else (weekly, biweekly, ...)
    keeps exact day-count stepping."""
    return "monthly" if 27 <= cadence_days <= 31 else "daily"


def _advance(d: date, series: "RecurringSeries") -> date:
    if series.cadence_kind == "monthly":
        return _add_month(d, 1)
    return d + timedelta(days=series.cadence_days)


@dataclass
class RecurringSeries:
    category: str
    direction: str  # "credit" or "debit"
    event_type: str
    cadence_days: int
    cadence_kind: str  # "monthly" or "daily"
    amount: float  # home-currency conservative per-occurrence estimate (ongoing baseline)
    flexibility: str
    minimum_allowed_amount: Optional[float]
    last_event_id: str
    last_date: str
    description_hint: str = ""  # distinguishes concurrent income streams under one category
    cutoff_date: Optional[str] = None  # no occurrences strictly after this (salary_ended)
    forced_next: Optional[Tuple[str, float]] = None  # (date, amount) override for the very next occurrence
    temporary_next_amount: Optional[float] = None  # applies once to next occurrence only, then reverts
    one_time_addon: Optional[Tuple[str, float]] = None  # (date, amount) added once on top of that date's occurrence


@dataclass
class OneOff:
    date: str
    amount: float  # signed: +credit -debit, home currency
    event_id: str
    category: str


@dataclass
class UserContext:
    user_id: str
    profile: object
    recurring: List[RecurringSeries]
    one_offs: List[OneOff]


_image_cache = None


def _get_amount_home_ccy(ds, event, home_ccy: str) -> float:
    global _image_cache
    amount = event.amount
    if amount is None:
        if _image_cache is None:
            _image_cache = load_image_cache()
        entry = _image_cache.get(event.event_id)
        if entry is None:
            raise RuntimeError(
                f"Event {event.event_id} has a blank amount and no image_cache.json entry. "
                "Refusing to treat a blank amount as zero."
            )
        amount = entry["amount"]
        src_ccy = entry["currency"]
    else:
        src_ccy = event.currency
    return fx.convert(amount, src_ccy, home_ccy, event.settlement_date)


def _clean_and_detect_cadence(evs_sorted: List, amount_fn=None) -> Tuple[Optional[int], List]:
    """Detect cadence from a chronological event list, tolerating the
    occasional off-cycle duplicate/correction/one-off row (e.g. a "net
    salary" restatement, or a quarterly bonus/arrears payment posted a few
    days after the regular monthly payment) by iteratively dropping one
    event out of whichever pair produced the smallest, clearly-outlying gap.

    Which one to drop matters: a same-amount restatement should keep the
    LATER record ("a newer record from the same source" wins), but a
    same-category one-off with a DIFFERENT amount (a bonus, an arrears
    top-up) is not a restatement of the regular payment at all -- dropping
    the earlier one would wrongly discard a legitimate, on-cadence payment
    and keep the anomalous one-off, corrupting the cadence AND the amount
    estimate. So when amount_fn is available, whichever of the pair is
    farther from the established amount pattern (the median of the other
    events) is the one dropped; ties keep the newer-wins default.

    Returns (cadence_days_or_None, cleaned_event_list)."""
    working = list(evs_sorted)
    for _ in range(3):
        if len(working) < RECURRING_MIN_OCCURRENCES:
            break
        gaps = [(_parse(working[i + 1].event_date) - _parse(working[i].event_date)).days
                for i in range(len(working) - 1)]
        if not all(g > 0 for g in gaps):
            # drop exact-duplicate-date entries, keeping the later list position
            dedup = [working[0]]
            for i in range(1, len(working)):
                if working[i].event_date == dedup[-1].event_date:
                    dedup[-1] = working[i]
                else:
                    dedup.append(working[i])
            working = dedup
            continue
        med = statistics.median(gaps)
        min_gap = min(gaps)
        if min_gap < max(3, 0.4 * med):
            idx = gaps.index(min_gap)
            drop_idx = idx  # default: drop the earlier of the outlying pair
            if amount_fn is not None:
                others = [amount_fn(e) for j, e in enumerate(working) if j not in (idx, idx + 1)]
                if others:
                    baseline = statistics.median(others)
                    dist_a = abs(amount_fn(working[idx]) - baseline)
                    dist_b = abs(amount_fn(working[idx + 1]) - baseline)
                    if dist_b > dist_a:
                        drop_idx = idx + 1
            del working[drop_idx]
        else:
            break

    if len(working) < RECURRING_MIN_OCCURRENCES:
        return None, working
    gaps = [(_parse(working[i + 1].event_date) - _parse(working[i].event_date)).days
            for i in range(len(working) - 1)]
    if not gaps or max(gaps) > RECURRING_MAX_GAP_RATIO * min(gaps):
        return None, working
    return max(1, round(statistics.median(gaps))), working


_signals_by_user_cache: Dict[str, list] = {}


def _signals_for_user(ds, user_id):
    if not _signals_by_user_cache:
        for s in parse_messages(ds):
            _signals_by_user_cache.setdefault(s.user_id, []).append(s)
    return sorted(_signals_by_user_cache.get(user_id, []), key=lambda s: s.sent_at)


def build_user_context(ds, user_id: str) -> UserContext:
    profile = ds.profiles[user_id]
    home = profile.home_currency
    events = ds.events_by_user.get(user_id, [])

    excluded_ids = set()
    signals = _signals_for_user(ds, user_id)
    for s in signals:
        if s.type in ("reimbursement_reclassify",) and s.related_event_id:
            excluded_ids.add(s.related_event_id)

    settled = [e for e in events if e.status == "settled" and e.event_id not in excluded_ids]

    # Category alone is the primary grouping: expense categories vary
    # description per occurrence (different grocery stores, restaurants,
    # freelance income varies by client/project) but represent one recurring
    # habit or income pattern. Income can, less often, hold multiple
    # genuinely concurrent streams under one category (e.g. "Primary
    # household salary" and "Second household income" both category=salary,
    # each with its own regular description, amount and cadence) -- that
    # case makes the merged group's gaps irregular, so credit groups that
    # fail cadence detection get retried split by description before giving
    # up on the category entirely.
    def _make_series(category, direction, evs, desc_hint=""):
        evs = sorted(evs, key=lambda e: e.event_date)
        recent = evs[-RECENT_WINDOW:]
        cadence, cleaned = _clean_and_detect_cadence(recent, amount_fn=lambda e: _get_amount_home_ccy(ds, e, home))
        if cadence is None:
            return None
        amounts = [_get_amount_home_ccy(ds, e, home) for e in cleaned]
        conservative_amount = statistics.mean(amounts[-3:])
        last = cleaned[-1]
        return RecurringSeries(
            category=category, direction=direction, event_type=last.event_type,
            cadence_days=cadence, cadence_kind=_cadence_kind(cadence), amount=conservative_amount,
            flexibility=last.flexibility, minimum_allowed_amount=last.minimum_allowed_amount,
            last_event_id=last.event_id, last_date=last.event_date, description_hint=desc_hint,
        )

    groups: Dict[Tuple[str, str], List] = {}
    for e in settled:
        if e.direction == "debit" and e.event_type in EXPENSE_TYPES:
            groups.setdefault((e.category, e.direction), []).append(e)
        elif e.direction == "credit" and e.event_type in INCOME_TYPES:
            groups.setdefault((e.category, e.direction), []).append(e)

    recurring: List[RecurringSeries] = []
    for (category, direction), evs in groups.items():
        series = _make_series(category, direction, evs)
        if series is not None:
            recurring.append(series)
            continue
        if direction != "credit":
            continue
        by_desc: Dict[str, List] = {}
        for e in evs:
            by_desc.setdefault(e.description, []).append(e)
        for desc, desc_evs in by_desc.items():
            sub = _make_series(category, direction, desc_evs, desc_hint=desc)
            if sub is not None:
                recurring.append(sub)

    # A data-only signal of termination: the most recent settled event in a
    # category+direction is itself labelled as final (e.g. "Final employer
    # payroll"), with no message needed to know the stream has stopped. This
    # can land on a different description than the series' own history (a
    # generic "Payroll credit" stream ending on one "Final employer payroll"
    # row), so it's checked against the true most-recent event per
    # category+direction, not just within one description group.
    TERMINATION_KEYWORDS = ("final employer", "final payroll", "severance", "last payroll")
    latest_by_catdir = {}
    for e in settled:
        key = (e.category, e.direction)
        if key not in latest_by_catdir or e.event_date > latest_by_catdir[key].event_date:
            latest_by_catdir[key] = e
    for (category, direction), e in latest_by_catdir.items():
        if any(kw in e.description.lower() for kw in TERMINATION_KEYWORDS):
            for r in recurring:
                if r.category == category and r.direction == direction:
                    if r.cutoff_date is None or e.event_date < r.cutoff_date:
                        r.cutoff_date = e.event_date

    series_by_cat = {(r.category, r.direction, r.description_hint): r for r in recurring}

    def _series_for(category, direction):
        return [r for r in recurring if r.category == category and r.direction == direction]

    consumed_ids = set()
    one_offs: List[OneOff] = []
    explicit_future = [
        e for e in events
        if e.event_id not in excluded_ids and (
            e.status == "scheduled" or (e.status == "pending" and e.direction == "debit")
        )
    ]

    # A scheduled/pending future row either continues an existing recurring
    # series (most often: "Next confirmed salary" is the next occurrence of
    # whichever salary stream it lines up with by date -- generic payroll
    # placeholder text, not a new stream) or, when history is too sparse to
    # have formed a series at all (a brand-new job), seeds a fresh one so the
    # user's only known future income/expense in that category doesn't just
    # vanish from the 90-day forecast after this single occurrence.
    for e in explicit_future:
        if e.direction == "debit" and e.event_type not in EXPENSE_TYPES:
            continue
        if e.direction == "credit" and e.event_type not in INCOME_TYPES:
            continue
        amt = _get_amount_home_ccy(ds, e, home)

        candidates = _series_for(e.category, e.direction)
        best = None
        for cand in candidates:
            if cand.forced_next is not None:
                continue
            gap = abs((_parse(e.settlement_date) - _parse(cand.last_date)).days - cand.cadence_days)
            if gap <= max(3, cand.cadence_days // 2):
                if best is None or gap < best[1]:
                    best = (cand, gap)
        if best is not None:
            best[0].forced_next = (e.settlement_date, amt)
            consumed_ids.add(e.event_id)
            continue

        if candidates:
            # An existing recurring series already covers this category, but
            # this event doesn't land near its next expected occurrence --
            # a genuine one-off (e.g. a special "outstanding balance"
            # catch-up payment), not a new recurring habit. Let it fall
            # through to the one_offs pass below rather than spawning a
            # phantom series from a single date.
            continue

        desc = e.description if e.direction == "credit" else ""
        # Deliberately NOT filtered by description: a scheduled/pending
        # placeholder row (e.g. "Next confirmed salary") almost never shares
        # its generic description with the actual employer-specific rows
        # ("Prorated first salary", "First-job payroll", "Payroll credit",
        # ...) that establish the real historical pattern. Filtering by
        # description here would make `hist` spuriously empty and wrongly
        # demote an established, continuing salary to a one-off (see the
        # `candidates` check above, which already handles the case where a
        # distinct concurrent income stream exists under this category).
        hist = sorted(
            [ev for ev in settled if ev.category == e.category and ev.direction == e.direction],
            key=lambda ev: ev.event_date,
        )
        if not hist:
            # No settled history at all for this category+direction: nothing
            # "supports" recurrence (per AGENTS.md's "detect recurrence only
            # when history supports it"). A scheduled/pending row with zero
            # precedent is a genuine one-off (e.g. a one-time school fee),
            # not a new recurring habit -- fall through to the one_offs pass
            # below instead of fabricating an indefinite monthly repeat of it.
            continue

        key = (e.category, e.direction, desc)
        last_hist = hist[-1]
        gap_days = (_parse(e.settlement_date) - _parse(last_hist.event_date)).days
        cadence = max(1, gap_days) if gap_days > 0 else 30
        flexibility, min_allowed = last_hist.flexibility, last_hist.minimum_allowed_amount
        new_series = RecurringSeries(
            category=e.category, direction=e.direction, event_type=e.event_type,
            cadence_days=cadence, cadence_kind=_cadence_kind(cadence), amount=amt,
            flexibility=flexibility, minimum_allowed_amount=min_allowed,
            last_event_id=e.event_id, last_date=e.settlement_date,
            description_hint=desc, forced_next=(e.settlement_date, amt),
        )
        recurring.append(new_series)
        series_by_cat[key] = new_series
        consumed_ids.add(e.event_id)

    for e in explicit_future:
        if e.event_id in consumed_ids:
            continue
        signed = _get_amount_home_ccy(ds, e, home) * (1 if e.direction == "credit" else -1)
        one_offs.append(OneOff(date=e.settlement_date, amount=signed, event_id=e.event_id, category=e.category))

    def _primary_salary_series():
        """Payroll messages describe one employer's salary; when a user has
        multiple concurrent income streams under category=salary (e.g. a
        "Primary household salary" and a smaller "Second household income"),
        assume the message concerns the larger, primary one."""
        candidates = _series_for("salary", "credit")
        if not candidates:
            return None
        return max(candidates, key=lambda r: r.amount)

    # Apply message-derived amendments.
    for s in signals:
        d = s.data
        if s.type == "salary_increase" and d.get("amount") is not None:
            series = _primary_salary_series()
            if series:
                series.amount = fx.convert(d["amount"], d["currency"], home, d.get("effective_date") or s.sent_at[:10])
        elif s.type == "salary_decrease_temporary" and d.get("amount") is not None:
            series = _primary_salary_series()
            if series:
                series.temporary_next_amount = fx.convert(d["amount"], d["currency"], home, s.sent_at[:10])
        elif s.type == "salary_date_amendment" and d.get("new_date"):
            series = _primary_salary_series()
            if series:
                base_amount = series.forced_next[1] if series.forced_next else series.amount
                series.forced_next = (d["new_date"], base_amount)
        elif s.type == "salary_first_payment" and d.get("amount") is not None and d.get("date"):
            amt_home = fx.convert(d["amount"], d["currency"], home, d["date"])
            series = _primary_salary_series()
            if series:
                series.amount = amt_home
                series.forced_next = (d["date"], amt_home)
                series.cutoff_date = None
            else:
                cadence = 30
                new_series = RecurringSeries(
                    category="salary", direction="credit", event_type="income",
                    cadence_days=cadence, cadence_kind=_cadence_kind(cadence), amount=amt_home,
                    flexibility="fixed", minimum_allowed_amount=None, last_event_id="", last_date=d["date"],
                    forced_next=(d["date"], amt_home),
                )
                recurring.append(new_series)
                series_by_cat[("salary", "credit", "")] = new_series
        elif s.type == "salary_ended":
            series = _primary_salary_series()
            if series:
                series.cutoff_date = s.sent_at[:10]
                series.forced_next = None
                series.temporary_next_amount = None
        elif s.type == "salary_partial_end" and d.get("remaining_amount") is not None:
            series = _primary_salary_series()
            if series:
                series.amount = fx.convert(d["remaining_amount"], d["currency"], home, s.sent_at[:10])
                series.forced_next = None
        elif s.type == "salary_resumed" and d.get("amount") is not None and d.get("date"):
            amt_home = fx.convert(d["amount"], d["currency"], home, d["date"])
            series = _primary_salary_series()
            if series:
                series.amount = amt_home
                series.forced_next = (d["date"], amt_home)
                series.cutoff_date = None
                # The pre-leave/post-leave gap that produced this series'
                # detected cadence is exactly the irregularity this message
                # is announcing the end of ("Regular salary ... resumes on
                # DATE"): recompute cadence from the settled history that
                # predates the gap (its own internal spacing is the real,
                # regular cadence), falling back to a standard month if that
                # history is itself too sparse to tell.
                hist = sorted(
                    [ev for ev in settled if ev.category == "salary" and ev.direction == "credit"],
                    key=lambda ev: ev.event_date,
                )
                pre_gap_cadence = None
                if len(hist) >= 2:
                    gaps = [(_parse(hist[i + 1].event_date) - _parse(hist[i].event_date)).days
                            for i in range(len(hist) - 1)]
                    regular_gaps = [g for g in gaps if g <= 35]
                    if regular_gaps:
                        pre_gap_cadence = round(statistics.median(regular_gaps))
                series.cadence_days = pre_gap_cadence or 30
                series.cadence_kind = _cadence_kind(series.cadence_days)
        elif s.type == "salary_with_arrears" and d.get("amount") is not None:
            series = _primary_salary_series()
            if series:
                series.amount = fx.convert(d["amount"], d["currency"], home, s.sent_at[:10])
                if d.get("arrears_amount") is not None:
                    next_date = series.forced_next[0] if series.forced_next else _fmt(_advance(_parse(series.last_date), series))
                    series.one_time_addon = (next_date, fx.convert(d["arrears_amount"], d["currency"], home, s.sent_at[:10]))
        elif s.type == "salary_base_confirmed" and d.get("amount") is not None:
            series = _primary_salary_series()
            if series:
                series.amount = fx.convert(d["amount"], d["currency"], home, s.sent_at[:10])
        elif s.type == "salary_confirmed_for_date" and d.get("amount") is not None and d.get("date"):
            amt_home = fx.convert(d["amount"], d["currency"], home, d["date"])
            series = _primary_salary_series()
            if series:
                series.amount = amt_home
                series.forced_next = (d["date"], amt_home)
        elif s.type == "expense_rent_increase" and d.get("multiplier"):
            series = series_by_cat.get(("rent", "debit"))
            if series:
                series.amount = series.amount * d["multiplier"]
        elif s.type == "income_confirmed_one_time" and d.get("amount") is not None and d.get("date"):
            amt_home = fx.convert(d["amount"], d["currency"], home, d["date"])
            one_offs.append(OneOff(date=d["date"], amount=amt_home, event_id=f"msg:{s.message_id}", category="invoice_income"))

    return UserContext(user_id=user_id, profile=profile, recurring=recurring, one_offs=one_offs)


def project_cashflow_detailed(
    ctx: UserContext,
    request_date: str,
    horizon_days: int = 90,
    spending_changes: Optional[List[dict]] = None,
) -> List[dict]:
    """Like project_cashflow, but each record keeps its provenance:
    {date, signed, category, direction, description_hint, source, series}
    (source is "recurring" or "one_off"; series is the RecurringSeries object
    or None). Used by project_cashflow (which strips this down to plain
    (date, signed) tuples) and by evaluation/diagnostics.py, which needs to
    explain *why* a given date is the binding constraint."""
    spending_changes = spending_changes or []
    stop_ids = {c["event_id"] for c in spending_changes if c["action"] == "stop"}
    reduce_map = {c["event_id"]: c["new_amount"] for c in spending_changes if c["action"] == "reduce_to"}

    start = _parse(request_date)
    end = start + timedelta(days=horizon_days)
    records: List[dict] = []

    for series in ctx.recurring:
        sign = 1.0 if series.direction == "credit" else -1.0
        is_stopped = series.last_event_id in stop_ids
        reduced_amount = reduce_map.get(series.last_event_id)

        if is_stopped:
            continue

        occurrences: List[Tuple[str, float]] = []
        if series.forced_next is not None:
            occurrences.append(series.forced_next)
            # Advance PAST the forced date before the loop below starts,
            # otherwise the loop's first iteration re-appends this same
            # date (its `cursor > start` check passes trivially since the
            # forced date is always after request_date), double-counting it.
            cursor = _advance(_parse(series.forced_next[0]), series)
        else:
            cursor = _advance(_parse(series.last_date), series)

        first_projected_done = series.forced_next is not None
        while cursor <= end:
            if cursor > start:
                if not first_projected_done and series.temporary_next_amount is not None:
                    occurrences.append((_fmt(cursor), series.temporary_next_amount))
                else:
                    occurrences.append((_fmt(cursor), series.amount))
            first_projected_done = True
            cursor = _advance(cursor, series)

        for occ_date, occ_amount in occurrences:
            od = _parse(occ_date)
            if od <= start or od > end:
                continue
            if series.cutoff_date and occ_date > series.cutoff_date:
                continue
            amount = occ_amount
            if reduced_amount is not None:
                amount = min(amount, reduced_amount)
            if series.one_time_addon and series.one_time_addon[0] == occ_date:
                amount = amount + series.one_time_addon[1]
            records.append({
                "date": occ_date, "signed": sign * amount, "category": series.category,
                "direction": series.direction, "description_hint": series.description_hint,
                "source": "recurring", "series": series,
            })

    for oo in ctx.one_offs:
        od = _parse(oo.date)
        if start < od <= end:
            records.append({
                "date": oo.date, "signed": oo.amount, "category": oo.category,
                "direction": "credit" if oo.amount > 0 else "debit", "description_hint": "",
                "source": "one_off", "series": None,
            })

    records.sort(key=lambda r: r["date"])
    return records


def project_cashflow(
    ctx: UserContext,
    request_date: str,
    horizon_days: int = 90,
    spending_changes: Optional[List[dict]] = None,
) -> List[Tuple[str, float]]:
    """Return [(date_str, signed_delta)] for every projected cash movement in
    (request_date, request_date + horizon_days], home currency.

    spending_changes: list of {"action": "stop"|"reduce_to", "event_id": ..., "new_amount": ...}
    keyed by the series' last_event_id (the identifier used in spending_changes_needed).
    """
    records = project_cashflow_detailed(ctx, request_date, horizon_days, spending_changes)
    return [(r["date"], r["signed"]) for r in records]
