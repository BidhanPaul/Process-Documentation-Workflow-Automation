"""
Generates synthetic but realistic process data shaped exactly like the
BidhanPaul/ServiceManagementSystem API responses (service requests, offers,
evaluations, orders, order changes). Used as a stand-in data source so the
analytics pipeline can run end-to-end without a live backend deployment,
while still exercising the same ingestion/storage/analytics code path that
would run against the real REST API.
"""
import random
from datetime import datetime, timedelta

random.seed(42)

DEPARTMENTS = ["Engineering", "HR", "Finance", "Facilities", "IT Operations"]
PROJECT_MANAGERS = ["A. Weber", "S. Fischer", "L. Becker", "M. Hoffmann", "J. Klein"]
PROCUREMENT_OFFICERS = ["R. Schmidt", "T. Wagner"]
RESOURCE_PLANNERS = ["N. Braun", "K. Zimmermann"]
PROVIDERS = ["Delta Consulting", "Nexora GmbH", "Provantis", "BlueField Services", "Orbis Tech"]
REQUEST_TITLES = [
    "Cloud migration support", "Network security audit", "Payroll system upgrade",
    "Facility maintenance contract", "Data center relocation", "Helpdesk staffing",
    "ERP integration", "Onsite IT support", "Disaster recovery drill", "Software licensing review",
]
BIDDING_WINDOWS = [3, 7, 14]

REQUEST_STATUSES = ["APPROVED_FOR_BIDDING", "BIDDING", "EVALUATION", "ORDERED", "COMPLETED", "REJECTED", "EXPIRED"]
STATUS_WEIGHTS =    [0.05,                  0.08,      0.10,        0.30,      0.32,        0.08,       0.07]

ORDER_STATUSES = ["PENDING_RP_APPROVAL", "SUBMITTED_TO_PROVIDER", "APPROVED", "REJECTED"]
ORDER_WEIGHTS = [0.10, 0.15, 0.65, 0.10]

CHANGE_TYPES = ["SUBSTITUTION", "EXTENSION"]
CHANGE_STATUSES = ["APPROVED", "REJECTED", "PENDING"]
CHANGE_WEIGHTS = [0.70, 0.15, 0.15]


def _rand_date(start, end):
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def generate_dataset(n_requests=180, start_date=None, end_date=None):
    start_date = start_date or datetime(2025, 7, 1)
    end_date = end_date or datetime(2026, 7, 1)

    requests, offers, evaluations, orders, order_changes = [], [], [], [], []
    offer_id, eval_id, order_id, change_id = 1, 1, 1, 1

    for req_id in range(1, n_requests + 1):
        created = _rand_date(start_date, end_date - timedelta(days=30))
        review_days = max(1, round(random.gauss(2.5, 1.2)))
        status = random.choices(REQUEST_STATUSES, weights=STATUS_WEIGHTS)[0]
        bidding_window = random.choice(BIDDING_WINDOWS)

        approved = created + timedelta(days=review_days) if status != "REJECTED" else None
        bidding_start = approved
        bidding_end = bidding_start + timedelta(days=bidding_window) if bidding_start else None

        requests.append({
            "request_id": req_id,
            "title": random.choice(REQUEST_TITLES),
            "department": random.choice(DEPARTMENTS),
            "project_manager": random.choice(PROJECT_MANAGERS),
            "procurement_officer": random.choice(PROCUREMENT_OFFICERS),
            "status": status,
            "bidding_window_days": bidding_window,
            "created_date": created.isoformat(),
            "review_days": review_days,
            "approved_date": approved.isoformat() if approved else None,
            "bidding_start": bidding_start.isoformat() if bidding_start else None,
            "bidding_end": bidding_end.isoformat() if bidding_end else None,
        })

        if status == "REJECTED" or bidding_end is None:
            continue

        # Offers submitted during the bidding window
        n_offers = 0 if status == "EXPIRED" else random.randint(1, 5)
        req_offer_rows = []
        for _ in range(n_offers):
            submitted = _rand_date(bidding_start, bidding_end)
            price = round(random.uniform(4000, 45000), 2)
            row = {
                "offer_id": offer_id,
                "request_id": req_id,
                "provider_name": random.choice(PROVIDERS),
                "submitted_date": submitted.isoformat(),
                "price_eur": price,
            }
            offers.append(row)
            req_offer_rows.append(row)
            offer_id += 1

        if status in ("EXPIRED",) or not req_offer_rows:
            continue

        # Evaluations (only if we've moved past bidding)
        if status in ("EVALUATION", "ORDERED", "COMPLETED"):
            eval_date = bidding_end + timedelta(days=random.randint(1, 4))
            for row in req_offer_rows:
                evaluations.append({
                    "evaluation_id": eval_id,
                    "offer_id": row["offer_id"],
                    "request_id": req_id,
                    "evaluated_date": eval_date.isoformat(),
                    "score": round(random.uniform(55, 98), 1),
                    "evaluator": random.choice(RESOURCE_PLANNERS),
                })
                eval_id += 1

        # Orders (only if we've moved to ordered/completed)
        if status in ("ORDERED", "COMPLETED"):
            winning_offer = max(
                (e for e in evaluations if e["request_id"] == req_id),
                key=lambda e: e["score"],
            )
            order_created = bidding_end + timedelta(days=random.randint(2, 6))
            order_status = random.choices(ORDER_STATUSES, weights=ORDER_WEIGHTS)[0]
            if status == "COMPLETED":
                order_status = "APPROVED"
            approved_date = order_created + timedelta(days=random.randint(1, 5)) if order_status == "APPROVED" else None

            orders.append({
                "order_id": order_id,
                "request_id": req_id,
                "offer_id": winning_offer["offer_id"],
                "resource_planner": random.choice(RESOURCE_PLANNERS),
                "status": order_status,
                "order_value_eur": round(random.uniform(5000, 60000), 2),
                "man_days": random.randint(5, 120),
                "created_date": order_created.isoformat(),
                "approved_date": approved_date.isoformat() if approved_date else None,
            })

            # Order changes (substitution / extension) on ~25% of orders
            if order_status == "APPROVED" and random.random() < 0.25:
                requested = approved_date + timedelta(days=random.randint(5, 40))
                c_status = random.choices(CHANGE_STATUSES, weights=CHANGE_WEIGHTS)[0]
                resolved = requested + timedelta(days=random.randint(1, 6)) if c_status != "PENDING" else None
                order_changes.append({
                    "change_id": change_id,
                    "order_id": order_id,
                    "change_type": random.choice(CHANGE_TYPES),
                    "status": c_status,
                    "requested_date": requested.isoformat(),
                    "resolved_date": resolved.isoformat() if resolved else None,
                })
                change_id += 1

            order_id += 1

    return {
        "requests": requests,
        "offers": offers,
        "evaluations": evaluations,
        "orders": orders,
        "order_changes": order_changes,
    }


if __name__ == "__main__":
    data = generate_dataset()
    for k, v in data.items():
        print(f"{k}: {len(v)} rows")
