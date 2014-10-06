import time
import re

try:
    from PyQt4 import QtGui, QtCore, QtSql
    from PyQt4.uic import loadUiType
except ImportError:
    from PySide import QtGui, QtCore, QtSql
    from loadui import loadUiType

from tabledatawidget import TableDataWidget
from resultdatawidget import ResultDataWidget
from sqlitedatabase import SQLiteQuery
from constants import KEYWORDS, PUNCTUATION, FUNCTIONS
from constants import WORD, PUNC, FUNC, STRING

QUERY = u"SELECT * FROM {table} WHERE rowid > {first} ORDER BY {column} {order} LIMIT {limit}"
MESSAGE_HEAD = u"{queries} queries executed, {success} success, {errors} errors\n"
MESSAGE_SELECT = """
Query: {query}

{numrows} row(s) returned

Time: {time}
--------------------------------------------------

"""

MESSAGE_UPDATE = """
Query: {query}

{numrows} row(s) affected

Time: {time}
--------------------------------------------------

"""
MESSAGE_ERROR = """
Query: {query}

{error}

Time: {time}
--------------------------------------------------

"""

form_class, base_class = loadUiType('./widgets/query.ui')


class SQLHighlighter(QtGui.QSyntaxHighlighter):
    def highlightBlock(self, text):
        for keyword in iter(KEYWORDS):
            expr = QtCore.QRegExp("\\b%s\\b" % keyword.lower())
            index = expr.indexIn(text.lower())
            while index >= 0:
                length = expr.matchedLength()
                self.setFormat(index, length, WORD)
                index = expr.indexIn(text.lower(), index + length)
        
        for keyword in iter(FUNCTIONS):
            expr = QtCore.QRegExp("\\b%s\\b" % keyword.lower())
            index = expr.indexIn(text.lower())
            while index >= 0:
                length = expr.matchedLength()
                self.setFormat(index, length, FUNC)
                index = expr.indexIn(text.lower(), index + length)
        
        for keyword in iter(PUNCTUATION):
            expr = QtCore.QRegExp('\%s' % keyword)
            index = expr.indexIn(text)
            while index >= 0:
                length = expr.matchedLength()
                self.setFormat(index, length, PUNC)
                index = expr.indexIn(text.lower(), index + length)
        
        startstring = QtCore.QRegExp("\\'")
        endstring = QtCore.QRegExp("\\'")
        self.setCurrentBlockState(0)
        
        startindex = 0
        if self.previousBlockState() != 1:
            startindex = startstring.indexIn(text)
        
        while startindex >= 0:
            endindex = endstring.indexIn(text, startindex + 1)
            if endindex == -1:
                self.setCurrentBlockState(1)
                stringlength = len(text) - startindex
            else:
                stringlength = endindex - startindex + endstring.matchedLength()
            
            print startindex, endindex
            
            self.setFormat(startindex, stringlength, STRING)
            startindex = startstring.indexIn(text, startindex + stringlength)


class QueryWidget(base_class):
    def __init__(self, db, parent=None):
        super(QueryWidget, self).__init__(parent)
        
        self._table = ''
        self._db = db
        self._resulticon = QtGui.QIcon(QtGui.QPixmap(":/icons/table_lightning.png"))
        
        self._ui = form_class()
        self._ui.setupUi(self)
        self._ui.tdTable.setDatabase(db)
        self._ui.tdTable.setQuery(self)
        highlighter = SQLHighlighter(self._ui.tQuery.document())

        self.bindEvents()

    def bindEvents(self):
        shortcut = QtGui.QShortcut(QtGui.QKeySequence(self.tr("F9", "Execute Query")), self)
        shortcut.activated.connect(self.executeInput)
    
    def table(self):
        return self._table
    
    def setTable(self, table):
        self._table = table
        self._ui.tdTable.setTable(table)
    
    def executeInput(self):
        queries = filter(None, self._ui.tQuery.toPlainText().split(';'))
        self.execute(queries)
    
    def execute(self, queries):
        errors = 0
        success = 0
        text = ''
        self._ui.tMessages.clear()
        self.__clearQueryTabs()
        for query in queries:
            q = SQLiteQuery()
            res = q.exec_(query)
            if res:
                success += 1
            else:
                errors += 1
            self._db.appendQuery(q)
            err = q.lastError()
            if err.isValid():
                text += MESSAGE_ERROR.format(
                    query=q.lastQuery(),
                    error=err.databaseText(),
                    time=q.time(),
                )
            else:
                if q.isSelect():
                    i = 0
                    while q.next():
                        i += 1
                    q.seek(-1)
                    widget = ResultDataWidget()
                    widget.setDatabase(self._db)
                    widget.setData(q)
                    self._ui.twTabs.insertTab(0, widget, self._resulticon, 'Results')
                    text += MESSAGE_SELECT.format(
                        query=q.lastQuery(),
                        numrows=i,
                        time=q.time(),
                    )
                else:
                    text += MESSAGE_UPDATE.format(
                        query=q.lastQuery(),
                        numrows=q.numRowsAffected(),
                        time=q.time(),
                    )
        
        self._ui.tMessages.insertPlainText(
            MESSAGE_HEAD.format(queries=len(queries), success=success, errors=errors)
        )
        self._ui.tMessages.insertPlainText(text)
        
        self._ui.twTabs.setCurrentWidget(self._ui.tabMessages)
    
    def __clearQueryTabs(self):
        widget = self._ui.twTabs.widget(0)
        while isinstance(widget, ResultDataWidget):
            widget.deleteLater()
            self._ui.twTabs.removeTab(0)
            widget = self._ui.twTabs.widget(0)
