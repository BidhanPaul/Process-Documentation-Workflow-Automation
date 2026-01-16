"""
IT Process Analytics — orchestrator.

Pipeline:
  1. Ingest data (live REST API if reachable, else synthetic generator matching
     the same schema as BidhanPaul/ServiceManagementSystem)
  2. Load into SQLite
  3. Compute process KPIs with Pandas/SQL
  4. Build an Excel stakeholder report with live formulas
  5. Generate a plain-language stakeholder summary

Usage:
  python main.py [--api-url https://your-deployment] [--n-requests 180]
"""
import argparse
import os
from datetime import datetime

from ingestion import load_data
from database import init_db, load_dataset
from analytics import (
    load_frames, request_status_breakdown, approval_rate,
    cycle_times, provider_performance, order_change_summary, sla_breaches,
    monthly_volume, department_breakdown,
)
from excel_report import build_workbook, add_provider_sheet
from summary_generator import generate_summary

OUTPUT_DIR = "output"


def run(api_url=None, n_requests=180):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    db_path = os.path.join(OUTPUT_DIR, "process.db")
    xlsx_path = os.path.join(OUTPUT_DIR, "IT_Process_KPI_Report.xlsx")
    summary_path = os.path.join(OUTPUT_DIR, "stakeholder_summary.md")

    print("[1/5] Ingesting data...")
    dataset = load_data(base_url=api_url, n_requests=n_requests)

    print("[2/5] Loading into SQLite...")
    conn = init_db(db_path)
    load_dataset(conn, dataset)

    print("[3/5] Computing KPIs...")
    frames = load_frames(conn)
    status_df = request_status_breakdown(conn)
    approval_df = approval_rate(conn)
    cycle_df, req_with_times, orders_with_times = cycle_times(frames)
    provider_df = provider_performance(frames)
    change_df = order_change_summary(frames)
    breaches_df = sla_breaches(req_with_times)
    monthly_df = monthly_volume(frames)
    dept_df = department_breakdown(conn)

    print("[4/5] Building Excel report...")
    generated_label = datetime.now().strftime("%d %b %Y, %H:%M")
    build_workbook(frames, monthly_df, dept_df, xlsx_path, generated_label=generated_label)
    add_provider_sheet(xlsx_path, provider_df)

    print("[5/5] Generating stakeholder summary...")
    generate_summary(frames, status_df, approval_df, cycle_df, provider_df,
                      change_df, breaches_df, summary_path)

    print(f"\nDone.\n  Database: {db_path}\n  Excel report: {xlsx_path}\n  Summary: {summary_path}")
    conn.close()
    return xlsx_path, summary_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IT Process Analytics pipeline")
    parser.add_argument("--api-url", default=None, help="Base URL of a live ServiceManagementSystem deployment")
    parser.add_argument("--n-requests", type=int, default=180, help="Number of synthetic requests to generate if API is unavailable")
    args = parser.parse_args()
    run(api_url=args.api_url, n_requests=args.n_requests)
