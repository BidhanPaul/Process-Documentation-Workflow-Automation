import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtCore import QThread, Signal


class PipelineWorker(QThread):
    log = Signal(str)
    progress = Signal(int)
    finished_ok = Signal()
    failed = Signal(str)

    def __init__(self, api_url=None, n_requests=180, parent=None):
        super().__init__(parent)
        self.api_url = api_url
        self.n_requests = n_requests

    def run(self):
        try:
            import main as pipeline

            steps = [
                (20, "Ingesting service request, offer, and evaluation data..."),
                (40, "Loading into SQLite warehouse..."),
                (65, "Computing process KPIs (Pandas / SQL)..."),
                (85, "Building Excel dashboard with live formulas..."),
                (100, "Generating stakeholder summary..."),
            ]
            self.log.emit(f"Starting pipeline run (n_requests={self.n_requests})")
            self.progress.emit(5)

            # main.run() executes the full pipeline synchronously; we surface
            # coarse progress markers around it for a responsive feel.
            for pct, msg in steps[:2]:
                self.log.emit(msg)
                self.progress.emit(pct)

            pipeline.run(api_url=self.api_url, n_requests=self.n_requests)

            for pct, msg in steps[2:]:
                self.log.emit(msg)
                self.progress.emit(pct)

            self.log.emit("Pipeline completed successfully.")
            self.finished_ok.emit()
        except Exception as exc:
            self.log.emit(f"ERROR: {exc}")
            self.failed.emit(str(exc))
