"""SQLite schema and load helpers for the Service Management process warehouse."""
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS service_requests (
    request_id INTEGER PRIMARY KEY,
    title TEXT,
    department TEXT,
    project_manager TEXT,
    procurement_officer TEXT,
    status TEXT,
    bidding_window_days INTEGER,
    created_date TEXT,
    review_days INTEGER,
    approved_date TEXT,
    bidding_start TEXT,
    bidding_end TEXT
);

CREATE TABLE IF NOT EXISTS offers (
    offer_id INTEGER PRIMARY KEY,
    request_id INTEGER,
    provider_name TEXT,
    submitted_date TEXT,
    price_eur REAL,
    FOREIGN KEY (request_id) REFERENCES service_requests(request_id)
);

CREATE TABLE IF NOT EXISTS evaluations (
    evaluation_id INTEGER PRIMARY KEY,
    offer_id INTEGER,
    request_id INTEGER,
    evaluated_date TEXT,
    score REAL,
    evaluator TEXT,
    FOREIGN KEY (offer_id) REFERENCES offers(offer_id)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    request_id INTEGER,
    offer_id INTEGER,
    resource_planner TEXT,
    status TEXT,
    order_value_eur REAL,
    man_days INTEGER,
    created_date TEXT,
    approved_date TEXT,
    FOREIGN KEY (request_id) REFERENCES service_requests(request_id)
);

CREATE TABLE IF NOT EXISTS order_changes (
    change_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    change_type TEXT,
    status TEXT,
    requested_date TEXT,
    resolved_date TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
"""

TABLE_COLUMNS = {
    "service_requests": ["request_id", "title", "department", "project_manager", "procurement_officer",
                          "status", "bidding_window_days", "created_date", "review_days",
                          "approved_date", "bidding_start", "bidding_end"],
    "offers": ["offer_id", "request_id", "provider_name", "submitted_date", "price_eur"],
    "evaluations": ["evaluation_id", "offer_id", "request_id", "evaluated_date", "score", "evaluator"],
    "orders": ["order_id", "request_id", "offer_id", "resource_planner", "status",
               "order_value_eur", "man_days", "created_date", "approved_date"],
    "order_changes": ["change_id", "order_id", "change_type", "status", "requested_date", "resolved_date"],
}

DATA_KEY_TO_TABLE = {
    "requests": "service_requests",
    "offers": "offers",
    "evaluations": "evaluations",
    "orders": "orders",
    "order_changes": "order_changes",
}


def init_db(db_path):
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def load_dataset(conn, dataset):
    cur = conn.cursor()
    for data_key, table in DATA_KEY_TO_TABLE.items():
        rows = dataset.get(data_key, [])
        if not rows:
            continue
        cols = TABLE_COLUMNS[table]
        placeholders = ",".join(["?"] * len(cols))
        cur.executemany(
            f"INSERT OR REPLACE INTO {table} ({','.join(cols)}) VALUES ({placeholders})",
            [tuple(row.get(c) for c in cols) for row in rows],
        )
    conn.commit()
