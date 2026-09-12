"""Currency conversion using dataset/exchange_rates.csv.

Rates are matched by settlement_date and the from/to currency pair. When no
direct pair exists for a date, bridge through USD (every date that has any
rate at all has at least one USD leg in this dataset).
"""
from __future__ import annotations

import csv
import os
from datetime import date, timedelta
from typing import Dict, Tuple

from data_loader import DATASET_DIR

_rates: Dict[Tuple[str, str, str], float] = {}
_dates_sorted = []


def _load():
    global _dates_sorted
    if _rates:
        return
    path = os.path.join(DATASET_DIR, "exchange_rates.csv")
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["rate_date"], row["from_currency"], row["to_currency"])
            _rates[key] = float(row["rate"])
    _dates_sorted = sorted({k[0] for k in _rates})


def _parse(d: str) -> date:
    y, m, dd = d.split("-")
    return date(int(y), int(m), int(dd))


def _nearest_rate_date(target: str) -> str:
    """The dataset publishes one rate snapshot roughly monthly (the 15th).
    Use the snapshot date closest to the target settlement date so every
    event in the dataset's date range can be converted."""
    _load()
    if not _dates_sorted:
        raise RuntimeError("No exchange rate data loaded")
    t = _parse(target)
    best = min(_dates_sorted, key=lambda d: abs((_parse(d) - t).days))
    return best


def _direct_rate(rate_date: str, from_ccy: str, to_ccy: str):
    _load()
    if from_ccy == to_ccy:
        return 1.0
    if (rate_date, from_ccy, to_ccy) in _rates:
        return _rates[(rate_date, from_ccy, to_ccy)]
    if (rate_date, to_ccy, from_ccy) in _rates:
        return 1.0 / _rates[(rate_date, to_ccy, from_ccy)]
    return None


def get_rate(rate_date: str, from_ccy: str, to_ccy: str) -> float:
    """Return the conversion multiplier: amount_in_to = amount_in_from * rate."""
    _load()
    if from_ccy == to_ccy:
        return 1.0

    snap = rate_date if rate_date in _dates_sorted else _nearest_rate_date(rate_date)

    direct = _direct_rate(snap, from_ccy, to_ccy)
    if direct is not None:
        return direct

    # Bridge through USD.
    leg1 = _direct_rate(snap, from_ccy, "USD")
    leg2 = _direct_rate(snap, "USD", to_ccy)
    if leg1 is not None and leg2 is not None:
        return leg1 * leg2

    # Try nearest available snapshot as a last resort (should not normally
    # be needed given monthly coverage across the whole date range).
    for d in sorted(_dates_sorted, key=lambda d: abs((_parse(d) - _parse(rate_date)).days)):
        direct = _direct_rate(d, from_ccy, to_ccy)
        if direct is not None:
            return direct
        leg1 = _direct_rate(d, from_ccy, "USD")
        leg2 = _direct_rate(d, "USD", to_ccy)
        if leg1 is not None and leg2 is not None:
            return leg1 * leg2

    raise RuntimeError(f"No exchange rate path from {from_ccy} to {to_ccy} near {rate_date}")


def convert(amount: float, from_ccy: str, to_ccy: str, settlement_date: str) -> float:
    if amount is None:
        raise RuntimeError("convert() called with amount=None")
    rate = get_rate(settlement_date, from_ccy, to_ccy)
    return amount * rate
