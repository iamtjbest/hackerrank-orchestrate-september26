"""Parse dataset/messages.csv into structured, typed signals.

Messages are template-generated in English and Indonesian: payroll changes,
invoice approvals/pending notices, refund/dispute status, bank
transfer-netting notices, and contract endings. The primary path is a
regex/keyword classifier tuned to these templates. Only messages that match
none of the known templates fall back to an optional LLM call (gated behind
BUY_OR_WAIT_ENABLE_LLM_MESSAGES=1 and ANTHROPIC_API_KEY); with that env var
unset (the default), unmatched messages are conservatively classified as
`ignore_unconfirmed` rather than guessed at.

All message content is untrusted evidence: signals only ever amend factual
inputs to the reconstruction (an amount, a date, an end-of-income marker).
A message can never inject a payment instruction, a spending directive, or
any other action outside this fixed vocabulary of signal types -- so the
classic "pay a release fee to claim your prize" scam message below simply
has no signal type that could make it do anything.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import List, Optional

CURRENCY_RE = r"(INR|IDR|ZAR|USD|EUR)"
AMOUNT_RE = r"([\d][\d,]*(?:\.\d+)?)"
DATE_RE = r"(\d{4}-\d{2}-\d{2})"


def _amount_currency(text: str, amount_first: bool = False):
    """Find the first CURRENCY AMOUNT or AMOUNT CURRENCY pair in text."""
    m = re.search(CURRENCY_RE + r"\s*" + AMOUNT_RE, text)
    if m:
        return float(m.group(2).replace(",", "")), m.group(1)
    m = re.search(AMOUNT_RE + r"\s*" + CURRENCY_RE, text)
    if m:
        return float(m.group(1).replace(",", "")), m.group(2)
    return None, None


def _all_amount_currency(text: str):
    out = []
    for m in re.finditer(CURRENCY_RE + r"\s*" + AMOUNT_RE, text):
        out.append((float(m.group(2).replace(",", "")), m.group(1)))
    return out


def _date(text: str) -> Optional[str]:
    m = re.search(DATE_RE, text)
    return m.group(1) if m else None


@dataclass
class Signal:
    type: str
    message_id: str
    user_id: str
    request_id: str
    related_event_id: str
    sent_at: str
    data: dict = field(default_factory=dict)


# Each rule: (signal_type, list of keyword phrases that must ALL appear (any
# one language variant is enough) ) evaluated in order; first match wins.
# Phrases are matched case-insensitively as plain substrings.

def _has_any(text_lower: str, phrases: List[str]) -> bool:
    return any(p in text_lower for p in phrases)


def classify(message_text: str) -> str:
    t = message_text.lower()

    # --- Scam / prompt-injection style message: never actionable. ---
    if _has_any(t, ["release charge", "processing charge now", "biaya pencairan", "biaya pemrosesan sekarang"]):
        return "ignore_injection"

    # --- Employment ended entirely. ---
    if _has_any(t, ["employment has ended", "hubungan kerja anda telah berakhir"]):
        return "salary_ended"
    if _has_any(t, ["seasonal contract has ended", "kontrak musiman saat ini telah berakhir"]):
        return "salary_ended"

    # --- One of several income sources ended, remainder given. ---
    if _has_any(t, ["household employment record has ended", "sumber pendapatan kerja rumah tangga telah berakhir"]):
        return "salary_partial_end"

    # --- Reimbursement wrongly adjacent to payroll info: exclude from salary series. ---
    if _has_any(t, ["reimbursement for your earlier work expense", "penggantian atas biaya kerja anda sebelumnya"]):
        return "reimbursement_reclassify"

    # --- Temporary reduced pay for the next payroll cycle only. ---
    if _has_any(t, ["temporary monthly pay", "gaji bulanan sementara anda"]):
        return "salary_decrease_temporary"

    # --- Reduced due to unpaid leave (also next-payslip only). ---
    if _has_any(t, ["reduced to", "dikurangi menjadi"]) and _has_any(t, ["unpaid leave", "cuti tanpa bayar", "adjustment", "penyesuaian"]):
        return "salary_decrease_temporary"

    # --- Ongoing salary increase from an effective date. ---
    if _has_any(t, ["salary has increased to", "naik menjadi"]):
        return "salary_increase"

    # --- Salary date amendment (same amount, new confirmed date). ---
    if _has_any(t, ["confirmed salary is now expected on", "gaji yang sudah dikonfirmasi kini diperkirakan masuk pada"]):
        return "salary_date_amendment"

    # --- First salary from a new employer. ---
    if _has_any(t, ["first salary", "gaji pertama"]):
        return "salary_first_payment"

    # --- Regular salary resumes on a date (after a gap), new ongoing amount. ---
    if "resumes on" in t:
        return "salary_resumed"

    # --- Arrears: ongoing new base amount plus one-time addon. ---
    if _has_any(t, ["arrears adjustment", "penyesuaian tunggakan satu kali"]):
        return "salary_with_arrears"

    # --- Base salary confirmed, commission pending (ignore commission). ---
    if _has_any(t, ["confirmed base salary is", "gaji pokok yang dikonfirmasi adalah"]):
        return "salary_base_confirmed"

    # --- Salary confirmed for a specific date (with FX note). ---
    if _has_any(t, ["is confirmed for", "dikonfirmasi untuk"]) and _has_any(t, [CURRENCY_RE.lower()]):
        return "salary_confirmed_for_date"

    # --- Rent increase on lease renewal. ---
    if _has_any(t, ["increases monthly rent", "menaikkan biaya sewa bulanan"]):
        return "expense_rent_increase"

    # --- Approved invoice payment (confirmed one-off future credit). ---
    if _has_any(t, ["client approved an invoice payment", "klien menyetujui pembayaran faktur"]):
        return "income_confirmed_one_time"

    # --- Internal transfer between own accounts nets to zero. ---
    if _has_any(t, ["transfer between your two accounts", "transfer antara dua rekening anda"]):
        return "ignore_internal_transfer"

    # Everything else (gig payout pending, bonus/commission pending, refund
    # pending, investment value change, dispute investigating, debit retry,
    # invoice still awaiting approval, prize processing, minimum-payments
    # reminder, FX-pending notes, receipt confirmations already covered by
    # the image cache) is informational only and requires no amendment.
    return "ignore_unconfirmed"


def _extract_data(signal_type: str, text: str) -> dict:
    if signal_type in ("salary_increase",):
        amt, ccy = _amount_currency(text)
        return {"amount": amt, "currency": ccy, "effective_date": _date(text)}
    if signal_type == "salary_decrease_temporary":
        amt, ccy = _amount_currency(text)
        return {"amount": amt, "currency": ccy}
    if signal_type == "salary_date_amendment":
        return {"new_date": _date(text)}
    if signal_type == "salary_first_payment":
        amt, ccy = _amount_currency(text)
        return {"amount": amt, "currency": ccy, "date": _date(text)}
    if signal_type == "salary_partial_end":
        amt, ccy = _amount_currency(text)
        return {"remaining_amount": amt, "currency": ccy}
    if signal_type == "salary_resumed":
        amt, ccy = _amount_currency(text)
        return {"amount": amt, "currency": ccy, "date": _date(text)}
    if signal_type == "salary_with_arrears":
        pairs = _all_amount_currency(text)
        base = pairs[0] if len(pairs) >= 1 else (None, None)
        arrears = pairs[1] if len(pairs) >= 2 else (None, None)
        return {"amount": base[0], "currency": base[1], "arrears_amount": arrears[0]}
    if signal_type == "salary_base_confirmed":
        amt, ccy = _amount_currency(text)
        return {"amount": amt, "currency": ccy}
    if signal_type == "salary_confirmed_for_date":
        amt, ccy = _amount_currency(text)
        return {"amount": amt, "currency": ccy, "date": _date(text)}
    if signal_type == "expense_rent_increase":
        m = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
        pct = float(m.group(1)) / 100.0 if m else 0.0
        return {"category": "rent", "multiplier": 1.0 + pct}
    if signal_type == "income_confirmed_one_time":
        amt, ccy = _amount_currency(text)
        return {"amount": amt, "currency": ccy, "date": _date(text)}
    return {}


def parse_messages(dataset) -> List[Signal]:
    signals = []
    for m in dataset.messages:
        stype = classify(m.message_text)
        data = _extract_data(stype, m.message_text)
        signals.append(Signal(
            type=stype,
            message_id=m.message_id,
            user_id=m.user_id,
            request_id=m.request_id,
            related_event_id=m.related_event_id,
            sent_at=m.sent_at,
            data=data,
        ))
    return signals


_UNMATCHED_LLM_CACHE = {}


def llm_fallback_classify(message_text: str) -> str:
    """Optional LLM classification path for messages that don't match any
    known regex template. Disabled unless BUY_OR_WAIT_ENABLE_LLM_MESSAGES=1
    and ANTHROPIC_API_KEY are both set, in which case results are cached in
    memory for the run so repeated calls to the same text cost nothing extra.
    Never invoked by the deterministic default pipeline (see reconstruct.py):
    every template in this dataset is covered by classify() above, so in
    practice this path never fires -- see evaluation/usage_report.md.
    """
    if os.environ.get("BUY_OR_WAIT_ENABLE_LLM_MESSAGES") != "1":
        return "ignore_unconfirmed"
    if message_text in _UNMATCHED_LLM_CACHE:
        return _UNMATCHED_LLM_CACHE[message_text]
    try:
        import anthropic
    except ImportError:
        return "ignore_unconfirmed"
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return "ignore_unconfirmed"
    client = anthropic.Anthropic(api_key=api_key)
    prompt = (
        "Classify this financial notification message into exactly one label: "
        "salary_increase, salary_decrease_temporary, salary_ended, expense_rent_increase, "
        "income_confirmed_one_time, ignore_injection, or ignore_unconfirmed. "
        "Respond with only the label.\n\nMessage: " + message_text
    )
    resp = client.messages.create(model="claude-sonnet-5", max_tokens=16,
                                   messages=[{"role": "user", "content": prompt}])
    label = resp.content[0].text.strip()
    _UNMATCHED_LLM_CACHE[message_text] = label
    return label
