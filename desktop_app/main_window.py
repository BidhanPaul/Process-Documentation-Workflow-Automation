import os
import subprocess
import sys
import platform

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QStackedWidget, QFrame, QTableView, QLineEdit, QSizePolicy, QProgressBar,
    QPlainTextEdit, QSpacerItem, QHeaderView, QMessageBox, QGridLayout,
)

from theme import STYLESHEET, BLUE, TEAL, AMBER, PURPLE, GREEN, NAVY
from pandas_model import PandasTableModel
from data_service import load_state, XLSX_PATH, SUMMARY_PATH
from pipeline_worker import PipelineWorker

TILE_COLORS = [BLUE, TEAL, AMBER, PURPLE, GREEN]

NAV_ITEMS = [
    ("dashboard", "🏠  Dashboard"),
    ("requests", "📋  Service Requests"),
    ("orders", "📦  Orders"),
    ("providers", "🤝  Providers"),
    ("changes", "🔁  Change Requests"),
    ("reports", "📊  Reports"),
]


def _open_file(path):
    if not os.path.exists(path):
        return False
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(path)
        elif system == "Darwin":
            subprocess.call(["open", path])
        else:
            subprocess.call(["xdg-open", path])
        return True
    except Exception:
        return False


class KpiTile(QFrame):
    def __init__(self, label, value, subtitle, color):
        super().__init__()
        self.setObjectName("Tile")
        self.setStyleSheet(f"#Tile {{ background: {color}; }}")
        self.setMinimumHeight(92)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        lbl = QLabel(label.upper())
        lbl.setObjectName("TileLabel")
        val = QLabel(value)
        val.setObjectName("TileValue")
        sub = QLabel(subtitle)
        sub.setObjectName("TileSub")

        layout.addWidget(lbl)
        layout.addWidget(val)
        layout.addStretch()
        layout.addWidget(sub)
        self.value_label = val


class TablePage(QWidget):
    def __init__(self, title, subtitle=""):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        header_row = QHBoxLayout()
        title_box = QVBoxLayout()
        t = QLabel(title)
        t.setObjectName("PageTitle")
        title_box.addWidget(t)
        if subtitle:
            s = QLabel(subtitle)
            s.setObjectName("StatusLabel")
            title_box.addWidget(s)
        header_row.addLayout(title_box)
        header_row.addStretch()

        self.search = QLineEdit()
        self.search.setObjectName("SearchBox")
        self.search.setPlaceholderText("Filter...")
        self.search.setFixedWidth(220)
        header_row.addWidget(self.search)
        layout.addLayout(header_row)

        self.table = QTableView()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)

        self.model = PandasTableModel()
        self.table.setModel(self.model)

        from PySide6.QtCore import QSortFilterProxyModel
        self.proxy = QSortFilterProxyModel()
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.table.setModel(self.proxy)
        self.search.textChanged.connect(self.proxy.setFilterFixedString)

    def set_dataframe(self, df):
        self.model.set_dataframe(df)
        self.table.resizeColumnsToContents()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ITSM Process Cockpit")
        self.resize(1280, 820)
        self.setStyleSheet(STYLESHEET)

        self.state = load_state()
        self.worker = None

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())

        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)
        right.addWidget(self._build_topbar())

        self.stack = QStackedWidget()
        self.pages = {}
        self._build_pages()
        right.addWidget(self.stack)

        right_container = QWidget()
        right_container.setLayout(right)
        root.addWidget(right_container, 1)

        self._select_nav("dashboard")
        self._refresh_all()

    # ---------------- Sidebar ----------------
    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(230)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title = QLabel("ITSM Cockpit")
        title.setObjectName("SidebarTitle")
        subtitle = QLabel("Process Governance & Analytics")
        subtitle.setObjectName("SidebarSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        self.nav_buttons = {}
        for key, label in NAV_ITEMS:
            btn = QPushButton(label)
            btn.setObjectName("NavButton")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, k=key: self._select_nav(k))
            layout.addWidget(btn)
            self.nav_buttons[key] = btn

        layout.addStretch()
        return sidebar

    def _select_nav(self, key):
        for k, btn in self.nav_buttons.items():
            btn.setChecked(k == key)
        if key in self.pages:
            self.stack.setCurrentWidget(self.pages[key])

    # ---------------- Top bar ----------------
    def _build_topbar(self):
        bar = QFrame()
        bar.setObjectName("TopBar")
        bar.setFixedHeight(64)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(24, 8, 24, 8)

        self.top_title = QLabel("Process KPI Dashboard")
        self.top_title.setObjectName("PageTitle")
        layout.addWidget(self.top_title)

        layout.addStretch()

        self.status_label = QLabel(f"Last run: {self.state.last_run}")
        self.status_label.setObjectName("StatusLabel")
        layout.addWidget(self.status_label)

        self.progress = QProgressBar()
        self.progress.setFixedWidth(140)
        self.progress.setValue(0)
        self.progress.setVisible(False)
        layout.addSpacing(12)
        layout.addWidget(self.progress)

        self.run_btn = QPushButton("▶  Run Pipeline")
        self.run_btn.setObjectName("PrimaryButton")
        self.run_btn.setCursor(Qt.PointingHandCursor)
        self.run_btn.clicked.connect(self._run_pipeline)
        layout.addSpacing(12)
        layout.addWidget(self.run_btn)

        return bar

    # ---------------- Pages ----------------
    def _build_pages(self):
        self.pages["dashboard"] = self._build_dashboard_page()
        self.stack.addWidget(self.pages["dashboard"])

        self.pages["requests"] = TablePage("Service Requests", "Full request lifecycle log")
        self.stack.addWidget(self.pages["requests"])

        self.pages["orders"] = TablePage("Orders", "Placed orders and approval status")
        self.stack.addWidget(self.pages["orders"])

        self.pages["providers"] = self._build_providers_page()
        self.stack.addWidget(self.pages["providers"])

        self.pages["changes"] = TablePage("Change Requests", "Substitutions & extensions on active orders")
        self.stack.addWidget(self.pages["changes"])

        self.pages["reports"] = self._build_reports_page()
        self.stack.addWidget(self.pages["reports"])

    def _build_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        t = QLabel("Process KPI Dashboard")
        t.setObjectName("PageTitle")
        layout.addWidget(t)

        self.tile_grid = QGridLayout()
        self.tile_grid.setSpacing(14)
        layout.addLayout(self.tile_grid)

        section = QLabel("Requests by Status")
        section.setObjectName("SectionLabel")
        layout.addWidget(section)

        self.status_card = QFrame()
        self.status_card.setObjectName("Card")
        self.status_layout = QVBoxLayout(self.status_card)
        self.status_layout.setContentsMargins(16, 12, 16, 12)
        layout.addWidget(self.status_card)

        layout.addStretch()
        return page

    def _build_providers_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        t = QLabel("Provider Performance")
        t.setObjectName("PageTitle")
        layout.addWidget(t)

        self.provider_card = QFrame()
        self.provider_card.setObjectName("Card")
        self.provider_layout = QVBoxLayout(self.provider_card)
        self.provider_layout.setContentsMargins(16, 16, 16, 16)
        self.provider_layout.setSpacing(10)
        layout.addWidget(self.provider_card)
        layout.addStretch()
        return page

    def _build_reports_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        t = QLabel("Reports & Pipeline Log")
        t.setObjectName("PageTitle")
        layout.addWidget(t)

        row = QHBoxLayout()
        open_xlsx = QPushButton("📊  Open Excel Report")
        open_xlsx.setObjectName("SecondaryButton")
        open_xlsx.setCursor(Qt.PointingHandCursor)
        open_xlsx.clicked.connect(lambda: self._open_or_warn(XLSX_PATH))

        open_summary = QPushButton("📝  Open Stakeholder Summary")
        open_summary.setObjectName("SecondaryButton")
        open_summary.setCursor(Qt.PointingHandCursor)
        open_summary.clicked.connect(lambda: self._open_or_warn(SUMMARY_PATH))

        open_folder = QPushButton("📁  Open Output Folder")
        open_folder.setObjectName("SecondaryButton")
        open_folder.setCursor(Qt.PointingHandCursor)
        open_folder.clicked.connect(lambda: self._open_or_warn(os.path.dirname(XLSX_PATH)))

        row.addWidget(open_xlsx)
        row.addWidget(open_summary)
        row.addWidget(open_folder)
        row.addStretch()
        layout.addLayout(row)

        section = QLabel("Pipeline Log")
        section.setObjectName("SectionLabel")
        layout.addWidget(section)

        self.log_box = QPlainTextEdit()
        self.log_box.setObjectName("LogBox")
        self.log_box.setReadOnly(True)
        self.log_box.setPlaceholderText("Run the pipeline to see log output here...")
        layout.addWidget(self.log_box, 1)

        return page

    def _open_or_warn(self, path):
        if not _open_file(path):
            QMessageBox.warning(self, "Not found", f"File not found yet:\n{path}\n\nRun the pipeline first.")

    # ---------------- Data refresh ----------------
    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _refresh_all(self):
        state = self.state
        self.status_label.setText(f"Last run: {state.last_run}")

        self._clear_layout(self.tile_grid)
        if state.loaded:
            n_req = len(state.frames["requests"])
            n_ord = len(state.frames["orders"])
            approval_pct = state.approval_df["approval_rate_pct"].iloc[0]
            total_value = state.frames["orders"]["order_value_eur"].sum()
            avg_man_days = state.frames["orders"]["man_days"].mean() if n_ord else 0

            tiles = [
                ("Total Requests", str(n_req), "Service requests logged"),
                ("Approval Rate", f"{approval_pct:.1f}%", "Procurement approval"),
                ("Total Orders", str(n_ord), "Orders placed"),
                ("Order Value", f"€{total_value:,.0f}", "Total contracted value"),
                ("Avg Man-Days", f"{avg_man_days:.1f}", "Per order"),
            ]
            for i, (label, val, sub) in enumerate(tiles):
                tile = KpiTile(label, val, sub, TILE_COLORS[i % len(TILE_COLORS)])
                self.tile_grid.addWidget(tile, 0, i)
        else:
            placeholder = QLabel("No data yet — click \"Run Pipeline\" to generate the first report.")
            placeholder.setObjectName("StatusLabel")
            self.tile_grid.addWidget(placeholder, 0, 0)

        self._clear_layout(self.status_layout)
        if state.loaded:
            max_count = state.status_df["request_count"].max()
            for _, row in state.status_df.iterrows():
                bar_row = QHBoxLayout()
                lbl = QLabel(row["status"])
                lbl.setFixedWidth(170)
                lbl.setStyleSheet("color:#22313F; font-size:12px;")
                bar_row.addWidget(lbl)

                bar_bg = QFrame()
                bar_bg.setFixedHeight(16)
                bar_bg.setStyleSheet("background:#EEF2F7; border-radius:3px;")
                bar_bg_layout = QHBoxLayout(bar_bg)
                bar_bg_layout.setContentsMargins(0, 0, 0, 0)
                width_ratio = row["request_count"] / max_count if max_count else 0
                fill = QFrame()
                fill.setStyleSheet(f"background:{NAVY}; border-radius:3px;")
                bar_bg_layout.addWidget(fill, int(width_ratio * 100))
                bar_bg_layout.addStretch(int((1 - width_ratio) * 100) + 1)
                bar_row.addWidget(bar_bg, 1)

                count_lbl = QLabel(f'{row["request_count"]}  ({row["pct_of_total"]}%)')
                count_lbl.setFixedWidth(90)
                count_lbl.setStyleSheet("color:#5B6B7C; font-size:11px;")
                bar_row.addWidget(count_lbl)

                self.status_layout.addLayout(bar_row)

        if state.loaded:
            self.pages["requests"].set_dataframe(state.frames["requests"])
            self.pages["orders"].set_dataframe(state.frames["orders"])
            self.pages["changes"].set_dataframe(state.frames["order_changes"])

        self._clear_layout(self.provider_layout)
        if state.loaded and not state.provider_df.empty:
            max_win = state.provider_df["win_rate_pct"].max()
            for _, row in state.provider_df.iterrows():
                r = QHBoxLayout()
                name = QLabel(row["provider_name"])
                name.setFixedWidth(160)
                name.setStyleSheet("font-weight:600; color:#22313F; font-size:12px;")
                r.addWidget(name)

                bar_bg = QFrame()
                bar_bg.setFixedHeight(18)
                bar_bg.setStyleSheet("background:#EEF2F7; border-radius:3px;")
                bar_bg_layout = QHBoxLayout(bar_bg)
                bar_bg_layout.setContentsMargins(0, 0, 0, 0)
                ratio = row["win_rate_pct"] / max_win if max_win else 0
                fill = QFrame()
                fill.setStyleSheet(f"background:{BLUE}; border-radius:3px;")
                bar_bg_layout.addWidget(fill, int(ratio * 100))
                bar_bg_layout.addStretch(int((1 - ratio) * 100) + 1)
                r.addWidget(bar_bg, 1)

                stat = QLabel(f'{row["win_rate_pct"]}% win · {int(row["orders_won"])}/{int(row["offers_submitted"])} · avg score {row["avg_score"]}')
                stat.setFixedWidth(260)
                stat.setStyleSheet("color:#5B6B7C; font-size:11px;")
                r.addWidget(stat)

                self.provider_layout.addLayout(r)
        elif state.loaded:
            self.provider_layout.addWidget(QLabel("No provider data available."))

    # ---------------- Pipeline execution ----------------
    def _run_pipeline(self):
        self.run_btn.setEnabled(False)
        self.run_btn.setText("Running...")
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.log_box.clear()
        self._select_nav("reports")

        self.worker = PipelineWorker(n_requests=180)
        self.worker.log.connect(self.log_box.appendPlainText)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished_ok.connect(self._on_pipeline_done)
        self.worker.failed.connect(self._on_pipeline_failed)
        self.worker.start()

    def _on_pipeline_done(self):
        self.run_btn.setEnabled(True)
        self.run_btn.setText("▶  Run Pipeline")
        self.progress.setVisible(False)
        self.state = load_state()
        self._refresh_all()

    def _on_pipeline_failed(self, msg):
        self.run_btn.setEnabled(True)
        self.run_btn.setText("▶  Run Pipeline")
        self.progress.setVisible(False)
        QMessageBox.critical(self, "Pipeline failed", msg)
