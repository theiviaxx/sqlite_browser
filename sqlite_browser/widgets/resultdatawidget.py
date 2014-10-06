

try:
    from PyQt4 import QtGui, QtCore, QtSql
    from PyQt4.uic import loadUiType
except ImportError:
    from PySide import QtGui, QtCore, QtSql
    from loadui import loadUiType

from tabledatawidget import TableDataWidget

READ_STYLE = """
QTableView { gridline-color: #b4b4b4; }
QTableView::item { background: #f6f6f6; }
QTableView::item:alternate { background: #eaeaea; }
"""


class ResultDataWidget(TableDataWidget):
    def __init__(self, parent=None):
        super(ResultDataWidget, self).__init__(parent)
        
        self._model.setReadOnly(True)
        self._ui.twGrid.setStyleSheet(READ_STYLE)
        
        self._ui.label.setVisible(False)
        self._ui.label_4.setVisible(False)
        self._ui.lDatabase.setVisible(False)
    
    def setData(self, result):
        self._model.setRecords(result)
        record = result.record()
        headers = []
        for i in xrange(record.count()):
            headers.append(record.field(i).name())
        self._model.setHeaders(headers)
        self._proxy.invalidate()
        self._ui.lTable.setText(result.lastQuery())
    