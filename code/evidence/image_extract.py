"""Regenerate / verify code/evidence/image_cache.json.

dataset/financial_events.csv has 16 rows with a blank `amount`. Each maps
1:1 through dataset/images.csv to a receipt/bill/payslip PNG under
dataset/media/images/. The cache in this directory was extracted by hand
and is used by default (deterministic, zero API cost).

Run with `--verify` (default, no network) to confirm every blank-amount
event has a cache entry and that images.csv agrees with it.

Run with `--regenerate` AND the environment variable
BUY_OR_WAIT_ENABLE_VISION=1 (plus ANTHROPIC_API_KEY) to re-derive the cache
from scratch with a vision-capable Claude call, as a reproducibility check
against the hand-extracted values. This path is optional and never runs
implicitly, so a normal `python3 code/main.py` run stays deterministic and
free of network calls.
"""
from __future__ import annotations

import base64
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_loader import load_dataset  # noqa: E402

CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image_cache.json")

VISION_PROMPT = (
    "This is a financial receipt, bill, or payslip. Extract the single most "
    "relevant total amount that represents this financial event's cash value "
    "(e.g. net salary on a payslip, balance due / total due on a bill, total "
    "paid on a receipt). Respond with ONLY the numeric amount, no currency "
    "symbol, no commas, no other text."
)


def load_cache() -> dict:
    with open(CACHE_PATH, encoding="utf-8") as f:
        return json.load(f)


def blank_amount_events():
    ds = load_dataset()
    return [e for e in ds.events.values() if e.amount is None]


def verify() -> bool:
    ds = load_dataset()
    cache = load_cache()
    blanks = blank_amount_events()
    ok = True
    print(f"Found {len(blanks)} financial_events.csv rows with a blank amount.")
    for e in blanks:
        img = ds.images_by_event.get(e.event_id)
        if img is None:
            print(f"  FAIL: {e.event_id} has no matching row in images.csv")
            ok = False
            continue
        if e.event_id not in cache:
            print(f"  FAIL: {e.event_id} (image {img.image_id}) missing from image_cache.json")
            ok = False
            continue
        entry = cache[e.event_id]
        if entry.get("image_id") != img.image_id:
            print(f"  FAIL: {e.event_id} cache image_id {entry.get('image_id')} != images.csv {img.image_id}")
            ok = False
        img_path = ds.image_path(img.image_id)
        if not os.path.exists(img_path):
            print(f"  FAIL: image file missing at {img_path}")
            ok = False
    extra = set(cache) - {e.event_id for e in blanks}
    if extra:
        print(f"  NOTE: cache has entries for events that are not blank in the current dataset: {sorted(extra)}")
    if ok:
        print("All blank-amount events are covered by image_cache.json. OK.")
    return ok


def regenerate():
    if os.environ.get("BUY_OR_WAIT_ENABLE_VISION") != "1":
        print("Skipping regeneration: set BUY_OR_WAIT_ENABLE_VISION=1 and ANTHROPIC_API_KEY to enable the "
              "optional live vision-extraction path. Using the existing hand-extracted cache.")
        return load_cache()

    try:
        import anthropic
    except ImportError:
        print("The 'anthropic' package is not installed; cannot regenerate via vision API. "
              "pip install anthropic to enable this optional path.")
        return load_cache()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ANTHROPIC_API_KEY not set; cannot regenerate via vision API.")
        return load_cache()

    client = anthropic.Anthropic(api_key=api_key)
    ds = load_dataset()
    cache = load_cache()
    usage_log = []

    for e in blank_amount_events():
        img = ds.images_by_event.get(e.event_id)
        if img is None:
            continue
        img_path = ds.image_path(img.image_id)
        with open(img_path, "rb") as f:
            img_b64 = base64.standard_b64encode(f.read()).decode("utf-8")

        resp = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=64,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img_b64}},
                    {"type": "text", "text": VISION_PROMPT},
                ],
            }],
        )
        text = resp.content[0].text.strip()
        usage_log.append({
            "event_id": e.event_id,
            "image_id": img.image_id,
            "input_tokens": resp.usage.input_tokens,
            "output_tokens": resp.usage.output_tokens,
            "extracted_text": text,
            "cached_value": cache.get(e.event_id, {}).get("amount"),
        })
        print(f"{e.event_id} ({img.image_id}): model said {text!r}, cache has {cache.get(e.event_id, {}).get('amount')}")

    usage_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vision_regeneration_usage.json")
    with open(usage_path, "w", encoding="utf-8") as f:
        json.dump(usage_log, f, indent=2)
    print(f"Wrote verification usage log to {usage_path}")
    return cache


if __name__ == "__main__":
    if "--regenerate" in sys.argv:
        regenerate()
    ok = verify()
    sys.exit(0 if ok else 1)
