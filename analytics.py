"""
Computes IT process governance KPIs from the SQLite warehouse using a mix of
SQL (for relational aggregation) and Pandas (for derived/time-based metrics).
"""
import pandas as pd


def _read(conn, table):
    return pd.read_sql_query(f"SELECT * FROM {table}", conn, parse_dates=None)


def load_frames(conn):
    return {
        "requests": _read(conn, "service_requests"),
        "offers": _read(conn, "offers"),
        "evaluations": _read(conn, "evaluations"),
        "orders": _read(conn, "orders"),
        "order_changes": _read(conn, "order_changes"),
    }


def request_status_breakdown(conn):
    """% of requests in each lifecycle status (SQL aggregation)."""
    return pd.read_sql_query("""
        SELECT status,
               COUNT(*) AS request_count,
               ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM service_requests), 1) AS pct_of_total
        FROM service_requests
        GROUP BY status
        ORDER BY request_count DESC
    """, conn)


def approval_rate(conn):
    """Procurement approval vs rejection rate."""
    df = pd.read_sql_query("""
        SELECT
            SUM(CASE WHEN status != 'REJECTED' THEN 1 ELSE 0 END) AS approved,
            SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END) AS rejected,
            COUNT(*) AS total
        FROM service_requests
    """, conn)
    df["approval_rate_pct"] = (df["approved"] / df["total"] * 100).round(1)
    return df


def cycle_times(frames):
    """Stage-by-stage cycle time in days (Pandas datetime arithmetic)."""
    req = frames["requests"].copy()
    for col in ["created_date", "approved_date", "bidding_start", "bidding_end"]:
        req[col] = pd.to_datetime(req[col], errors="coerce")

    req["review_to_approval_days"] = (req["approved_date"] - req["created_date"]).dt.total_seconds() / 86400
    req["bidding_duration_days"] = (req["bidding_end"] - req["bidding_start"]).dt.total_seconds() / 86400

    orders = frames["orders"].copy()
    orders["created_date"] = pd.to_datetime(orders["created_date"], errors="coerce")
    orders["approved_date"] = pd.to_datetime(orders["approved_date"], errors="coerce")
    orders["order_approval_days"] = (orders["approved_date"] - orders["created_date"]).dt.total_seconds() / 86400

    merged = orders.merge(req[["request_id", "bidding_end"]], on="request_id", how="left")
    merged["evaluation_to_order_days"] = (merged["created_date"] - merged["bidding_end"]).dt.total_seconds() / 86400

    summary = pd.DataFrame({
        "stage": [
            "Request review -> approval",
            "Bidding window (actual duration)",
            "Bidding close -> order created",
            "Order created -> order approved",
        ],
        "avg_days": [
            req["review_to_approval_days"].mean(),
            req["bidding_duration_days"].mean(),
            merged["evaluation_to_order_days"].mean(),
            orders["order_approval_days"].mean(),
        ],
        "max_days": [
            req["review_to_approval_days"].max(),
            req["bidding_duration_days"].max(),
            merged["evaluation_to_order_days"].max(),
            orders["order_approval_days"].max(),
        ],
    })
    summary[["avg_days", "max_days"]] = summary[["avg_days", "max_days"]].round(2)
    return summary, req, orders


def provider_performance(frames):
    """Win rate and avg evaluation score per provider (Pandas groupby)."""
    offers = frames["offers"]
    evals = frames["evaluations"]
    orders = frames["orders"]

    merged = offers.merge(evals[["offer_id", "score"]], on="offer_id", how="left")
    won_offer_ids = set(orders["offer_id"].dropna())
    merged["won"] = merged["offer_id"].isin(won_offer_ids)

    perf = merged.groupby("provider_name").agg(
        offers_submitted=("offer_id", "count"),
        avg_score=("score", "mean"),
        orders_won=("won", "sum"),
    ).reset_index()
    perf["win_rate_pct"] = (perf["orders_won"] / perf["offers_submitted"] * 100).round(1)
    perf["avg_score"] = perf["avg_score"].round(1)
    return perf.sort_values("win_rate_pct", ascending=False)


def order_change_summary(frames):
    """Substitution/extension frequency and resolution time."""
    changes = frames["order_changes"].copy()
    if changes.empty:
        return pd.DataFrame(columns=["change_type", "count", "approval_rate_pct", "avg_resolution_days"])
    changes["requested_date"] = pd.to_datetime(changes["requested_date"], errors="coerce")
    changes["resolved_date"] = pd.to_datetime(changes["resolved_date"], errors="coerce")
    changes["resolution_days"] = (changes["resolved_date"] - changes["requested_date"]).dt.total_seconds() / 86400

    grouped = changes.groupby("change_type").apply(
        lambda g: pd.Series({
            "count": len(g),
            "approval_rate_pct": round(100 * (g["status"] == "APPROVED").sum() / len(g), 1),
            "avg_resolution_days": round(g["resolution_days"].mean(), 2),
        })
    ).reset_index()
    return grouped


def sla_breaches(req, sla_days=7):
    """Requests where review-to-approval exceeded the SLA target."""
    breaches = req[req["review_to_approval_days"] > sla_days][
        ["request_id", "title", "department", "project_manager", "review_to_approval_days"]
    ].sort_values("review_to_approval_days", ascending=False)
    return breaches


def monthly_volume(frames):
    """Requests created and orders placed per month (Pandas time resampling)."""
    req = frames["requests"].copy()
    req["created_date"] = pd.to_datetime(req["created_date"], errors="coerce")
    req["month"] = req["created_date"].dt.to_period("M").astype(str)
    req_monthly = req.groupby("month").size().rename("requests_created")

    orders = frames["orders"].copy()
    orders["created_date"] = pd.to_datetime(orders["created_date"], errors="coerce")
    orders["month"] = orders["created_date"].dt.to_period("M").astype(str)
    ord_monthly = orders.groupby("month").size().rename("orders_placed")

    merged = pd.concat([req_monthly, ord_monthly], axis=1).fillna(0).reset_index()
    merged = merged.sort_values("month")
    merged[["requests_created", "orders_placed"]] = merged[["requests_created", "orders_placed"]].astype(int)
    return merged


def department_breakdown(conn):
    """Request volume and value by department (SQL join/aggregation)."""
    return pd.read_sql_query("""
        SELECT r.department,
               COUNT(DISTINCT r.request_id) AS requests,
               COUNT(DISTINCT o.order_id) AS orders,
               ROUND(COALESCE(SUM(o.order_value_eur), 0), 2) AS total_order_value
        FROM service_requests r
        LEFT JOIN orders o ON o.request_id = r.request_id
        GROUP BY r.department
        ORDER BY total_order_value DESC
    """, conn)
