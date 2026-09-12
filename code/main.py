#!/usr/bin/env python3
"""Entry point: reads dataset/requests.csv, writes output.csv in the repo root.

Usage:
    python3 code/main.py

No third-party dependencies. Reads only from dataset/. See README.md for
setup/run instructions and evaluation/usage_report.md for the token/cost
accounting of the (optional, disabled-by-default) LLM paths.
"""
from __future__ import annotations

import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_loader import load_dataset, REPO_ROOT  # noqa: E402
from reconstruct import build_user_context  # noqa: E402
from decision import decide  # noqa: E402
from explain import build_explanation, fmt_natural  # noqa: E402
from verify import verify_row, VerificationError  # noqa: E402

OUTPUT_COLUMNS = [
    "request_id", "amount_safe_to_pay", "affordability_status",
    "recommended_payment_method", "payment_plan", "earliest_date_for_full_payment",
    "spending_changes_needed", "decision_explanation",
]


def process_request(ds, request):
    ctx = build_user_context(ds, request.user_id)
    payment_options = ds.payment_options_by_request.get(request.request_id, [])
    result = decide(ds, ctx, request, payment_options)
    explanation = build_explanation(ds, ctx, request, result)

    row = {
        "request_id": request.request_id,
        "amount_safe_to_pay": fmt_natural(result["amount_safe_to_pay"]),
        "affordability_status": result["affordability_status"],
        "recommended_payment_method": result["recommended_payment_method"],
        "payment_plan": result["payment_plan"],
        "earliest_date_for_full_payment": result["earliest_date_for_full_payment"] or "",
        "spending_changes_needed": result["spending_changes_needed"],
        "decision_explanation": explanation,
    }
    verify_row(row, request, payment_options, ctx)
    return row


def main():
    ds = load_dataset()
    rows = []
    errors = []
    for request in ds.requests_in_order:
        try:
            rows.append(process_request(ds, request))
        except VerificationError as e:
            errors.append(str(e))
        except Exception as e:  # noqa: BLE001
            errors.append(f"{request.request_id}: unhandled error: {e!r}")

    if errors:
        sys.stderr.write(f"FAILED: {len(errors)} request(s) failed verification/processing:\n")
        for e in errors[:50]:
            sys.stderr.write(f"  - {e}\n")
        sys.exit(1)

    out_path = os.path.join(REPO_ROOT, "output.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"Wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
