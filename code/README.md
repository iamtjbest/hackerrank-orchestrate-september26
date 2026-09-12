# Buy or Wait? -- Solution

A deterministic, rules-based financial simulation engine. No LLM calls are
required for a normal run (see `evaluation/usage_report.md` for why, and how
that changes if you opt in to the two optional model-backed paths).

## Setup

Python 3.9+, standard library only -- no `pip install` needed for the core
pipeline.

```bash
cd code
python3 main.py
```

This reads everything from `../dataset/` and writes `../output.csv` (one row
per row of `dataset/requests.csv`, in the required 8-column format). The
run fails loudly (non-zero exit, no `output.csv` written) if any row fails
its deterministic post-hoc verification (`verify.py`) rather than silently
emitting a bad row.

## Optional: the two LLM-backed paths

Both are off by default and never run during a normal `python3 main.py`.
Enabling either requires `pip install anthropic` and `ANTHROPIC_API_KEY`.

```bash
# Re-derive the 16 blank-amount receipt/bill/payslip values from the images
# themselves, as a reproducibility check against the hand-extracted cache
# in evidence/image_cache.json (which is used either way):
BUY_OR_WAIT_ENABLE_VISION=1 ANTHROPIC_API_KEY=... python3 evidence/image_extract.py --regenerate

# Let unmatched messages (none exist in this dataset -- every message
# matches a known regex template) fall back to a live classification call
# instead of the conservative ignore_unconfirmed default:
BUY_OR_WAIT_ENABLE_LLM_MESSAGES=1 ANTHROPIC_API_KEY=... python3 main.py
```

## Scoring against the 25 known samples

```bash
python3 evaluation/evaluate.py                  # summary accuracy per field
python3 evaluation/evaluate.py --show-mismatches  # + per-row diffs
```

`dataset/sample_requests.csv` (`request_01`..`request_25`, `user_01`..`user_25`)
is a disjoint set of users/requests from `dataset/requests.csv`
(`request_26`..`request_275`, `user_26`..`user_275`) -- it is not part of the
250-row evaluation set. `evaluate.py` runs the same pipeline directly against
`sample_requests.csv`'s input columns and scores the result against its
ground-truth columns field by field.

## Architecture

| File | Responsibility |
|---|---|
| `data_loader.py` | Load and index every `dataset/*.csv` file (stdlib `csv` only). Never reads outside `dataset/`. |
| `fx.py` | Currency conversion via `dataset/exchange_rates.csv`, matched by settlement date, bridging through USD when no direct pair exists. |
| `evidence/image_cache.json`, `evidence/image_extract.py` | The 16 blank-`amount` events' values (hand-extracted, verified against `images.csv`) plus the optional live-vision regeneration/verification path. |
| `messages.py` | Regex/keyword classifier for the English/Indonesian message templates into structured signal types (salary changes, expense changes, ignorable noise, and an explicit `ignore_injection` bucket for the phishing-style "pay to claim your prize" message), with an optional LLM fallback for anything unmatched. |
| `reconstruct.py` | Per-user recurring-series detection (empirical cadence + conservative amount, tolerant of the occasional off-cycle duplicate/arrears row), one-off future commitments, message-derived amendments, and blank-amount fill-in -- collapsed into a pure `project_cashflow()` function. |
| `forecast.py` | The 90-day balance simulator: minimum-balance-after-payment, max-safe-amount-today (binary search), earliest-safe-full-payment-date. |
| `decision.py` | Eligibility + ranking rules from `problem_statement.md` / `AGENTS.md` §6.3, applied literally. |
| `verify.py` | Deterministic pre-write checks on every output row; raises rather than writing a bad row. |
| `explain.py` | Template-based `decision_explanation` text built only from numbers `decision.py` already computed. |
| `main.py` | Orchestrates the above; the entry point. |
| `evaluation/evaluate.py` | Scores against the 25 known samples. |
| `evaluation/usage_report.md` | Token/cost accounting for the final run. |

## Known limitations

This is a best-effort mechanical reconstruction of the challenge's decision
rules, built and validated against the 25 solved samples in
`dataset/sample_requests.csv`. Categorical fields (`affordability_status`,
`recommended_payment_method`, `spending_changes_needed`) match the samples
well; the exact `amount_safe_to_pay` figure is more sensitive to the precise
conservative-estimate convention used for variable recurring spending
(this implementation uses the mean of the 3 most recent occurrences) and
will not always match to the cent. See the session's `evaluation/evaluate.py`
output for the current per-field accuracy.
