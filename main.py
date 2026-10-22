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
from pathlib import Path
from datetime import datetime

from ingestion import load_data
from database import init_db, load_dataset
from analytics import (
    load_frames, request_status_breakdown, approval_rate,
    cycle_times, provider_performance, order_change_summary, sla_breaches,
    monthly_volume, department_breakdown,
    data_quality_report,
)
from excel_report import build_workbook, add_provider_sheet
from summary_generator import generate_summary

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "output"


def run(api_url=None, n_requests=180, progress_callback=None, log_callback=None):
    if n_requests < 0:
        raise ValueError("n_requests must be non-negative")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    db_path = OUTPUT_DIR / "process.db"
    xlsx_path = OUTPUT_DIR / "IT_Process_KPI_Report.xlsx"
    summary_path = OUTPUT_DIR / "stakeholder_summary.md"

    def report(step, message):
        print(message)
        if log_callback:
            log_callback(message)
        if progress_callback:
            progress_callback(step)

    report(20, "[1/5] Ingesting data...")
    dataset = load_data(base_url=api_url, n_requests=n_requests)

    report(40, "[2/5] Loading into SQLite...")
    conn = init_db(db_path)
    try:
        load_dataset(conn, dataset)

        report(65, "[3/5] Computing KPIs...")
        frames = load_frames(conn)
        status_df = request_status_breakdown(conn)
        approval_df = approval_rate(conn)
        cycle_df, req_with_times, orders_with_times = cycle_times(frames)
        provider_df = provider_performance(frames)
        change_df = order_change_summary(frames)
        breaches_df = sla_breaches(req_with_times)
        monthly_df = monthly_volume(frames)
        dept_df = department_breakdown(conn)
        quality = data_quality_report(frames)

        report(85, "[4/5] Building Excel report...")
        generated_label = datetime.now().strftime("%d %b %Y, %H:%M")
        build_workbook(frames, monthly_df, dept_df, xlsx_path, generated_label=generated_label)
        add_provider_sheet(xlsx_path, provider_df)

        report(100, "[5/5] Generating stakeholder summary...")
        generate_summary(frames, status_df, approval_df, cycle_df, provider_df,
                          change_df, breaches_df, summary_path, quality)

        print(f"\nDone.\n  Database: {db_path}\n  Excel report: {xlsx_path}\n  Summary: {summary_path}")
    finally:
        conn.close()
    return xlsx_path, summary_path


def cli():
    parser = argparse.ArgumentParser(description="IT Process Analytics pipeline")
    parser.add_argument("--api-url", default=None, help="Base URL of a live ServiceManagementSystem deployment")
    parser.add_argument("--n-requests", type=int, default=180, help="Number of synthetic requests to generate if API is unavailable")
    args = parser.parse_args()
    run(api_url=args.api_url, n_requests=args.n_requests)


if __name__ == "__main__":
    cli()
