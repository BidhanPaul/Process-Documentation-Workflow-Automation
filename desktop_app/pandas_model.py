from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QColor


class PandasTableModel(QAbstractTableModel):
    """Read-only Qt model backed by a pandas DataFrame, with light banded-row styling."""

    def __init__(self, df=None, parent=None):
        super().__init__(parent)
        self._df = df

    def set_dataframe(self, df):
        self.beginResetModel()
        self._df = df
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return 0 if self._df is None else len(self._df)

    def columnCount(self, parent=QModelIndex()):
        return 0 if self._df is None else len(self._df.columns)

    def data(self, index, role=Qt.DisplayRole):
        if self._df is None or not index.isValid():
            return None
        if role == Qt.DisplayRole:
            val = self._df.iat[index.row(), index.column()]
            if val is None:
                return ""
            return str(val)
        if role == Qt.BackgroundRole:
            return QColor("#F4F7FB") if index.row() % 2 == 0 else QColor("#FFFFFF")
        if role == Qt.ForegroundRole:
            return QColor("#1A3B5D")
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole or self._df is None:
            return None
        if orientation == Qt.Horizontal:
            return str(self._df.columns[section])
        return str(section + 1)
