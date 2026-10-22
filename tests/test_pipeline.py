import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from database import init_db, load_dataset
from data_generator import generate_dataset
from ingestion import load_data, validate_dataset
from analytics import data_quality_report


class PipelineContractTests(unittest.TestCase):
    def test_generated_dataset_is_complete(self):
        dataset = load_data(n_requests=2)
        self.assertEqual(
            set(dataset),
            {"requests", "offers", "evaluations", "orders", "order_changes"},
        )

    def test_invalid_dataset_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing required keys"):
            validate_dataset({"requests": []})

    def test_rerun_replaces_previous_snapshot(self):
        db_path = Path(tempfile.mktemp(suffix=".db"))
        conn = init_db(str(db_path))
        try:
            load_dataset(conn, generate_dataset(10))
            load_dataset(conn, generate_dataset(0))
            count = conn.execute("SELECT COUNT(*) FROM service_requests").fetchone()[0]
            self.assertEqual(count, 0)
        finally:
            conn.close()
            if db_path.exists():
                os.unlink(db_path)

    def test_load_data_rejects_negative_count(self):
        with self.assertRaisesRegex(ValueError, "non-negative"):
            load_data(n_requests=-1)

    def test_data_quality_report_has_no_warnings_for_generated_data(self):
        from database import load_dataset
        conn = init_db(":memory:")
        dataset = generate_dataset(5)
        load_dataset(conn, dataset)
        from analytics import load_frames
        self.assertEqual(data_quality_report(load_frames(conn))["total_warnings"], 0)
        conn.close()


if __name__ == "__main__":
    unittest.main()
