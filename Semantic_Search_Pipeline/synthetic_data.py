"""
Synthetic support-ticket dataset for the demo pipeline.

Generates realistic-looking customer support tickets across categories so
semantic search results are interpretable. Each record matches the schema
the pipeline expects: id, description, category, created_date.
"""
from __future__ import annotations

import random
from datetime import date, timedelta

_TEMPLATES: dict[str, list[str]] = {
    "billing": [
        "I was charged twice for my subscription this month and need a refund.",
        "My credit card was billed an incorrect amount — expected £9.99, charged £19.99.",
        "I cancelled my plan but the charge still appeared on my statement.",
        "Please update my billing address to the new office location.",
        "How do I switch from monthly to annual billing?",
        "I need an itemised invoice for my company's expense report.",
        "The discount code I applied at checkout was not reflected in the charge.",
        "My payment failed even though my card details are correct.",
    ],
    "technical": [
        "The application crashes every time I try to export a report to PDF.",
        "I cannot log in — the two-factor authentication code is not arriving by SMS.",
        "The dashboard is loading very slowly, taking more than 30 seconds.",
        "My data import failed with error code 500 and no further details.",
        "The mobile app freezes when I switch between tabs.",
        "API calls return 401 Unauthorized even with a valid token.",
        "I am unable to connect the integration with our Slack workspace.",
        "Search results are returning records that do not match the query.",
    ],
    "account": [
        "I need to transfer ownership of the account to a new administrator.",
        "Please delete my account and all associated data under GDPR.",
        "I forgot my password and the reset email is not arriving.",
        "I want to add three more users to our team plan.",
        "How do I change the primary email address on my account?",
        "My account was locked after too many failed login attempts.",
        "Can I merge two separate accounts under one subscription?",
        "I need to download a copy of all data stored in my account.",
    ],
    "feature_request": [
        "It would be very helpful to have a dark mode option in the interface.",
        "Could you add the ability to schedule automated weekly reports?",
        "We need bulk import support for CSV files larger than 100 MB.",
        "Please add keyboard shortcuts for the most common actions.",
        "A Zapier integration would save our team hours of manual work each week.",
        "We would like to filter search results by date range.",
        "Can you support SSO login via Azure Active Directory?",
        "An audit log showing who changed what and when would be invaluable.",
    ],
    "shipping": [
        "My order has not arrived and tracking shows it has been stuck for five days.",
        "I received the wrong item — I ordered the blue version but got red.",
        "The package arrived damaged and I need a replacement sent urgently.",
        "Can I change the delivery address after placing the order?",
        "My order was marked as delivered but nothing was left at my door.",
        "How long does standard shipping take to international addresses?",
        "I need to return an item — what is the process for getting a refund?",
        "The tracking number provided does not return any results.",
    ],
}


def generate_tickets(
    n: int = 200,
    start_date: date = date(2024, 1, 1),
    end_date: date = date(2024, 3, 31),
    seed: int = 42,
) -> list[dict]:
    """
    Return *n* synthetic support tickets spread uniformly across [start_date, end_date].
    """
    rng = random.Random(seed)
    categories = list(_TEMPLATES.keys())
    total_days = (end_date - start_date).days

    records = []
    for i in range(n):
        category = rng.choice(categories)
        description = rng.choice(_TEMPLATES[category])
        ticket_date = start_date + timedelta(days=rng.randint(0, total_days))
        records.append(
            {
                "id": f"TICKET-{i + 1:04d}",
                "description": description,
                "category": category,
                "created_date": ticket_date,
                "priority": rng.choice(["low", "medium", "high"]),
            }
        )

    # Sort by date so chunking is deterministic
    records.sort(key=lambda r: r["created_date"])
    return records
