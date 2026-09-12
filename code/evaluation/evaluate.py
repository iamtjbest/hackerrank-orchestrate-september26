#!/usr/bin/env python3
"""Score the pipeline against dataset/sample_requests.csv field by field.

sample_requests.csv covers request_01..request_25 / user_01..user_25, which
are DISJOINT from dataset/requests.csv (request_26.. / user_26..) -- the 25
solved samples are not part of the 250-row evaluation set. So this script
runs the pipeline directly against sample_requests.csv's input columns
(ignoring its ground-truth columns as input) and compares the result to
those same ground-truth columns.

Run from anywhere: python3 code/evaluation/evaluate.py
"""
from __future__ import annotations

import csv
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CODE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, CODE_DIR)

SAMPLES_CSV = os.path.join(REPO_ROOT, "dataset", "sample_requests.csv")

FIELDS = [
    "amount_safe_to_pay", "affordability_status", "recommended_payment_method",
    "payment_plan", "earliest_date_for_full_payment", "spending_changes_needed",
    "decision_explanation",
]


def _read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return {row["request_id"]: row for row in csv.DictReader(f)}


def _run_pipeline_on_samples():
    from data_loader import load_dataset, Request
    from main import process_request

    ds = load_dataset()
    predicted = {}
    with open(SAMPLES_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            req = Request(
                request_id=row["request_id"],
                user_id=row["user_id"],
                request_date=row["request_date"],
                request_type=row["request_type"],
                requested_amount=float(row["requested_amount"]),
                desired_completion_date=row["desired_completion_date"],
                allows_partial_payment=row["allows_partial_payment"].strip().lower() == "true",
                request_text=row["request_text"],
            )
            ds.requests[req.request_id] = req
            try:
                out_row = process_request(ds, req)
            except Exception as e:  # noqa: BLE001
                out_row = {"request_id": req.request_id, "amount_safe_to_pay": "-1",
                           "affordability_status": "ERROR", "recommended_payment_method": "ERROR",
                           "payment_plan": "ERROR", "earliest_date_for_full_payment": "ERROR",
                           "spending_changes_needed": "ERROR", "decision_explanation": f"ERROR: {e!r}"}
            predicted[req.request_id] = {k: str(v) for k, v in out_row.items()}
    return predicted


def _num_close(a, b, tol=1.0):
    try:
        return abs(float(a) - float(b)) <= tol
    except (ValueError, TypeError):
        return False


def _plan_close(a, b, tol=1.0):
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
        if da != db or not _num_close(aa, ab, tol):
            return False
    return True


def main():
    predicted = _run_pipeline_on_samples()
    truth = _read(SAMPLES_CSV)

    field_hits = {f: 0 for f in FIELDS}
    field_total = {f: 0 for f in FIELDS}
    row_exact = 0
    missing = []

    for rid, t in truth.items():
        p = predicted.get(rid)
        if p is None:
            missing.append(rid)
            continue
        all_match = True
        for f in FIELDS:
            field_total[f] += 1
            if f == "amount_safe_to_pay":
                ok = _num_close(p[f], t[f], tol=1.0)
            elif f == "payment_plan":
                ok = _plan_close(p[f], t[f], tol=1.0)
            elif f == "decision_explanation":
                ok = p[f].strip() == t[f].strip()
            else:
                ok = p[f].strip() == t[f].strip()
            if ok:
                field_hits[f] += 1
            else:
                all_match = False
        if all_match:
            row_exact += 1

    n = len(truth) - len(missing)
    print(f"Scored {n}/{len(truth)} sample rows (missing/errored: {missing})")
    print()
    print(f"{'field':32s} accuracy")
    for f in FIELDS:
        total = field_total[f]
        acc = field_hits[f] / total * 100 if total else 0.0
        print(f"{f:32s} {field_hits[f]:2d}/{total:2d}  {acc:5.1f}%")
    print()
    print(f"Exact full-row matches: {row_exact}/{n} ({row_exact/n*100:.1f}%)" if n else "no rows scored")

    if "--show-mismatches" in sys.argv:
        print()
        for rid, t in truth.items():
            p = predicted.get(rid)
            if p is None:
                continue
            diffs = [f for f in FIELDS if p[f].strip() != t[f].strip()]
            if diffs:
                print(f"--- {rid} mismatches: {diffs}")
                for f in diffs:
                    print(f"    {f}: pred={p[f]!r}  truth={t[f]!r}")


if __name__ == "__main__":
    main()
