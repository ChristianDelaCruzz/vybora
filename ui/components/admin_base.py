"""Shared admin table page."""
from typing import Callable, Optional
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (QAbstractItemView, QComboBox, QHBoxLayout, QHeaderView, QLineEdit, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, QWidget)

from ui.components.widgets import EmptyState, FlowLayout, GradientButton, page_title, secondary_button
from ui.pages.base import BasePage


def make_table(headers: list[str]) -> QTableWidget:
    t = QTableWidget(0, len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setAlternatingRowColors(True)
    t.verticalHeader().setVisible(False)
    t.setShowGrid(False)
    t.setMinimumHeight(300)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    t.horizontalHeader().setStretchLastSection(True)
    t.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    return t


def fill_table(table: QTableWidget, rows: list[list]) -> None:
    table.setRowCount(len(rows))
    for r, values in enumerate(values):
        for c, v in enumerate(values):
            item = QTableWidgetItem("" if v is None else str(v))
            item.setToolTip(item.text())
            table.setItem(r, c, item)


def yes_no(v) -> str:
    return "Yes" if v else "No"


class ManagementPage(BasePage):
    """Search + filter + table + action buttons. Subclasses implement ``fetch`` and ``row_values``."""

    headers: list[str] = []
    title_text = ""
    subtitle = ""
    search_placeholder = "Search..."

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        self.rows: list[dict] = []
        self.body.addWidget(page_title(self.title_text, self.subtitle))
        
        self.search = QLineEdit()
        self.search.setPlaceholderText(self.search_placeholder)
        self.search.setClearButtonEnabled(True)
        self.search.setAccessibleName("Search records")
        self.body.addWidget(self.search)
        
        self.buttons = FlowLayout(spacing=8) # filters + action buttons
        self.filter_box = self.buttons
        self.body.addLayout(self.buttons)
        
        self.table = make_table(self.headers)
        self.body.addWidget(self.table)
        
        self.empty = EmptyState("system/database", "No records", "Nothing matches yet.")
        self.body.addWidget(self.empty)
        self.count = None
        self.body.addStretch(1)
        
        self._needs_selection: list[QWidget] = []
        self._debounce = QTimer(self, singleShot=True, interval=350)
        self._debounce.timeout.connect(self.reload)
        self.search.textChanged.connect(lambda _t: self._debounce.start())
        self.table.itemSelectionChanged.connect(self._selection_changed)
        self.table.itemDoubleClicked.connect(lambda _i: self.on_double_click())

    # ---- subclass hooks ----------------------------------------------------------------
    def fetch(self) -> list[dict]:
        raise NotImplementedError

    def row_values(self, row: dict) -> list:
        raise NotImplementedError

    def on_double_click(self) -> None:
        pass

    # ---- helpers --------------------------------------------------------------------------
    def add_button(self, text: str, icon: str, handler: Callable, *, primary: bool = False, danger: bool = False,
                   needs_selection: bool = True) -> QWidget:
        btn = GradientButton(text, icon, height=38) if primary else secondary_button(text, icon, danger)
        btn.clicked.connect(lambda _c=False: handler())
        self.buttons.addWidget(btn)
        if needs_selection:
            self._needs_selection.append(btn)
            btn.setEnabled(False)
        return btn

    def add_filter(self, combo: QComboBox) -> None:
        combo.currentIndexChanged.connect(lambda _i: self.reload())
        combo.setMinimumWidth(150)
        self.filter_box.addWidget(combo)

    def selected(self) -> Optional[dict]:
        r = self.table.currentRow()
        return self.rows[r] if 0 <= r < len(self.rows) else None

    def _selection_changed(self) -> None:
        has = self.selected() is not None
        for b in self._needs_selection:
            b.setEnabled(has)
        self.selection_changed()

    def selection_changed(self) -> None:
        pass

    def on_show(self, **_kw) -> None:
        self.reload()

    def reload(self) -> None:
        keep = self.selected()
        try:
            self.rows = self.fetch()
        except Exception as exc:
            self.ctx.handle_error(exc, "Could not load records")
            self.rows = []
        fill_table(self.table, [self.row_values(r) for r in self.rows])
        self.empty.setVisible(not self.rows)
        self.table.setVisible(bool(self.rows))
        if keep and self.rows:
            key = next(iter(keep))
            for i, r in enumerate(self.rows):
                if r.get(key) == keep.get(key):
                    self.table.selectRow(i)
                    break
        self._selection_changed()

    def guard(self, func: Callable, success: str = "", error_title: str = "Action failed") -> bool:
        """Run an action; toast on success/failure; refresh the table."""
        try:
            func()
        except Exception as exc:
            self.ctx.handle_error(exc, error_title)
            return False
        if success:
            self.ctx.success(success)
        self.reload()
        return True