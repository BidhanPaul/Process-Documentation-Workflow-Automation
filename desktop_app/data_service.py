"""Bridges the existing analytics pipeline (database.py / analytics.py) into
a single state object the desktop UI can bind to."""
import os
import sqlite3
import sys
from dataclasses import dataclass, field
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analytics import (
    load_frames, request_status_breakdown, approval_rate, cycle_times,
    provider_performance, order_change_summary, sla_breaches,
    monthly_volume, department_breakdown,
)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "process.db")
XLSX_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "IT_Process_KPI_Report.xlsx")
SUMMARY_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "stakeholder_summary.md")


@dataclass
class AppState:
    loaded: bool = False
    last_run: str = "—"
    frames: dict = field(default_factory=dict)
    status_df: object = None
    approval_df: object = None
    cycle_df: object = None
    req_with_times: object = None
    provider_df: object = None
    change_df: object = None
    breaches_df: object = None
    monthly_df: object = None
    dept_df: object = None


def load_state() -> AppState:
    state = AppState()
    if not os.path.exists(DB_PATH):
        return state

    conn = sqlite3.connect(DB_PATH)
    try:
        frames = load_frames(conn)
        state.frames = frames
        state.status_df = request_status_breakdown(conn)
        state.approval_df = approval_rate(conn)
        cycle_df, req_with_times, orders_with_times = cycle_times(frames)
        state.cycle_df = cycle_df
        state.req_with_times = req_with_times
        state.provider_df = provider_performance(frames)
        state.change_df = order_change_summary(frames)
        state.breaches_df = sla_breaches(req_with_times)
        state.monthly_df = monthly_volume(frames)
        state.dept_df = department_breakdown(conn)
        state.loaded = True
        mtime = os.path.getmtime(DB_PATH)
        state.last_run = datetime.fromtimestamp(mtime).strftime("%d %b %Y, %H:%M")
    finally:
        conn.close()
    return state
