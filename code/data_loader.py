"""Load every dataset CSV from dataset/ and index rows for fast lookup.

Never reads or references anything outside dataset/. Stdlib-only (csv module)
so the solution has zero third-party dependencies and is trivially reproducible.
"""
from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")


def _read_csv(name: str) -> List[dict]:
    path = os.path.join(DATASET_DIR, name)
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _num(value: str, default=None):
    if value is None or value == "":
        return default
    return float(value)


@dataclass
class Profile:
    user_id: str
    home_currency: str
    current_available_balance: float
    minimum_balance_to_keep: float
    financial_priorities: List[str]
    expense_categories_to_protect: set
    expense_categories_user_is_willing_to_reduce: set
    expense_categories_user_is_willing_to_stop: set
    payment_methods_user_will_consider: set
    max_installment_months: Optional[int]


@dataclass
class Event:
    event_id: str
    user_id: str
    event_type: str
    description: str
    category: str
    direction: str
    amount: Optional[float]
    currency: str
    event_date: str
    settlement_date: str
    status: str
    linked_event_id: str
    flexibility: str
    minimum_allowed_amount: Optional[float]


@dataclass
class Request:
    request_id: str
    user_id: str
    request_date: str
    request_type: str
    requested_amount: float
    desired_completion_date: str
    allows_partial_payment: bool
    request_text: str


@dataclass
class PaymentOption:
    payment_option_id: str
    request_id: str
    payment_method: str
    payment_amount: float
    number_of_payments: int
    first_payment_date: Optional[str]
    payment_frequency_days: Optional[int]
    financing_fee: float
    total_payable_amount: float


@dataclass
class Message:
    message_id: str
    user_id: str
    request_id: str
    related_event_id: str
    sent_at: str
    source_type: str
    message_text: str


@dataclass
class ImageRef:
    image_id: str
    user_id: str
    request_id: str
    related_event_id: str


def _split_pipe(value: str) -> List[str]:
    return [v for v in (value or "").split("|") if v]


class Dataset:
    def __init__(self):
        self.profiles: Dict[str, Profile] = {}
        self.events: Dict[str, Event] = {}
        self.events_by_user: Dict[str, List[Event]] = {}
        self.requests: Dict[str, Request] = {}
        self.requests_in_order: List[Request] = []
        self.payment_options_by_request: Dict[str, List[PaymentOption]] = {}
        self.messages: List[Message] = []
        self.messages_by_related_event: Dict[str, List[Message]] = {}
        self.messages_by_user: Dict[str, List[Message]] = {}
        self.messages_by_request: Dict[str, List[Message]] = {}
        self.images: List[ImageRef] = []
        self.images_by_event: Dict[str, ImageRef] = {}
        self._load()

    def _load(self):
        for row in _read_csv("financial_profiles.csv"):
            p = Profile(
                user_id=row["user_id"],
                home_currency=row["home_currency"],
                current_available_balance=_num(row["current_available_balance"]),
                minimum_balance_to_keep=_num(row["minimum_balance_to_keep"]),
                financial_priorities=_split_pipe(row["financial_priorities"]),
                expense_categories_to_protect=set(_split_pipe(row["expense_categories_to_protect"])),
                expense_categories_user_is_willing_to_reduce=set(_split_pipe(row["expense_categories_user_is_willing_to_reduce"])),
                expense_categories_user_is_willing_to_stop=set(_split_pipe(row["expense_categories_user_is_willing_to_stop"])),
                payment_methods_user_will_consider=set(_split_pipe(row["payment_methods_user_will_consider"])),
                max_installment_months=int(row["max_installment_months"]) if row["max_installment_months"] else None,
            )
            self.profiles[p.user_id] = p

        for row in _read_csv("financial_events.csv"):
            e = Event(
                event_id=row["event_id"],
                user_id=row["user_id"],
                event_type=row["event_type"],
                description=row["description"],
                category=row["category"],
                direction=row["direction"],
                amount=_num(row["amount"], default=None),
                currency=row["currency"],
                event_date=row["event_date"],
                settlement_date=row["settlement_date"] or row["event_date"],
                status=row["status"],
                linked_event_id=row["linked_event_id"],
                flexibility=row["flexibility"],
                minimum_allowed_amount=_num(row["minimum_allowed_amount"], default=None),
            )
            self.events[e.event_id] = e
            self.events_by_user.setdefault(e.user_id, []).append(e)

        for row in _read_csv("requests.csv"):
            r = Request(
                request_id=row["request_id"],
                user_id=row["user_id"],
                request_date=row["request_date"],
                request_type=row["request_type"],
                requested_amount=_num(row["requested_amount"]),
                desired_completion_date=row["desired_completion_date"],
                allows_partial_payment=row["allows_partial_payment"].strip().lower() == "true",
                request_text=row["request_text"],
            )
            self.requests[r.request_id] = r
            self.requests_in_order.append(r)

        for row in _read_csv("request_payment_options.csv"):
            po = PaymentOption(
                payment_option_id=row["payment_option_id"],
                request_id=row["request_id"],
                payment_method=row["payment_method"],
                payment_amount=_num(row["payment_amount"]),
                number_of_payments=int(row["number_of_payments"]),
                first_payment_date=row["first_payment_date"] or None,
                payment_frequency_days=int(row["payment_frequency_days"]) if row["payment_frequency_days"] else None,
                financing_fee=_num(row["financing_fee"], default=0.0),
                total_payable_amount=_num(row["total_payable_amount"]),
            )
            self.payment_options_by_request.setdefault(po.request_id, []).append(po)

        for row in _read_csv("messages.csv"):
            m = Message(
                message_id=row["message_id"],
                user_id=row["user_id"],
                request_id=row["request_id"],
                related_event_id=row["related_event_id"],
                sent_at=row["sent_at"],
                source_type=row["source_type"],
                message_text=row["message_text"],
            )
            self.messages.append(m)
            if m.related_event_id:
                self.messages_by_related_event.setdefault(m.related_event_id, []).append(m)
            if m.user_id:
                self.messages_by_user.setdefault(m.user_id, []).append(m)
            if m.request_id:
                self.messages_by_request.setdefault(m.request_id, []).append(m)

        for row in _read_csv("images.csv"):
            img = ImageRef(
                image_id=row["image_id"],
                user_id=row["user_id"],
                request_id=row["request_id"],
                related_event_id=row["related_event_id"],
            )
            self.images.append(img)
            if img.related_event_id:
                self.images_by_event[img.related_event_id] = img

    def image_path(self, image_id: str) -> str:
        return os.path.join(DATASET_DIR, "media", "images", f"{image_id}.png")


_dataset_singleton: Optional[Dataset] = None


def load_dataset() -> Dataset:
    global _dataset_singleton
    if _dataset_singleton is None:
        _dataset_singleton = Dataset()
    return _dataset_singleton
