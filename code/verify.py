"""Deterministic pre-write checks on every output row. Raises AssertionError
(failing the build) rather than silently writing a bad row."""
from __future__ import annotations

VALID_STATUS = {"affordable_now", "affordable_with_plan", "affordable_later", "not_affordable"}
VALID_METHOD = {"full_payment", "partial_payment", "installments", "wait", "not_recommended"}


class VerificationError(Exception):
    pass


def _fail(request_id, msg):
    raise VerificationError(f"{request_id}: {msg}")


def verify_row(row: dict, request, payment_options, ctx):
    rid = row["request_id"]
    amt = float(row["amount_safe_to_pay"])
    if not (-1e-6 <= amt <= request.requested_amount + 1e-6):
        _fail(rid, f"amount_safe_to_pay {amt} out of [0, {request.requested_amount}]")

    if row["affordability_status"] not in VALID_STATUS:
        _fail(rid, f"bad affordability_status {row['affordability_status']}")
    if row["recommended_payment_method"] not in VALID_METHOD:
        _fail(rid, f"bad recommended_payment_method {row['recommended_payment_method']}")

    plan = row["payment_plan"]
    if plan != "none":
        entries = []
        prev_date = None
        for part in plan.split("|"):
            d, a = part.split(":")
            a = float(a)
            if prev_date is not None and d < prev_date:
                _fail(rid, f"payment_plan dates not chronological: {plan}")
            prev_date = d
            entries.append((d, a))

        method = row["recommended_payment_method"]
        if method == "partial_payment":
            if len(entries) != 2:
                _fail(rid, "partial_payment must have exactly two payments")
            total = entries[0][1] + entries[1][1]
            if abs(total - request.requested_amount) > 0.01:
                _fail(rid, f"partial_payment total {total} != requested_amount {request.requested_amount}")
            if not (0 < amt < request.requested_amount):
                _fail(rid, "partial_payment requires 0 < amount_safe_to_pay < requested_amount")
            if entries[1][0] > request.desired_completion_date:
                _fail(rid, "partial_payment second payment is after desired_completion_date")
        elif method == "installments":
            opts = [o for o in payment_options if o.payment_method == "installments"]
            match = None
            for o in opts:
                if o.number_of_payments == len(entries) and abs(entries[0][1] - o.payment_amount) < 0.01:
                    match = o
                    break
            if match is None:
                _fail(rid, "installments plan does not match any supplied payment_option")
        elif method in ("full_payment", "wait"):
            if len(entries) != 1:
                _fail(rid, f"{method} must have exactly one payment")
            if abs(entries[0][1] - request.requested_amount) > 0.01:
                _fail(rid, f"{method} payment amount != requested_amount")

    if row["affordability_status"] == "affordable_now":
        if row["earliest_date_for_full_payment"] != request.request_date:
            _fail(rid, "affordable_now requires earliest_date_for_full_payment == request_date")

    spend = row["spending_changes_needed"]
    if spend != "none":
        parts = spend.split("|")
        if len(parts) > 3:
            _fail(rid, "more than 3 spending changes")
        seen_events = set()
        stop_events, reduce_events = set(), set()
        for p in parts:
            fields = p.split(":")
            action = fields[0]
            event_id = fields[1]
            if action not in ("stop", "reduce_to"):
                _fail(rid, f"bad spending change action {action}")
            if action == "stop":
                stop_events.add(event_id)
            else:
                reduce_events.add(event_id)
            seen_events.add(event_id)
        if stop_events & reduce_events:
            _fail(rid, "same event both stopped and reduced")

    if row["recommended_payment_method"] == "not_recommended" and row["payment_plan"] != "none":
        _fail(rid, "not_recommended must have payment_plan == none")
