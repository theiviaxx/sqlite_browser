from collections import OrderedDict

try:
    from PyQt4 import QtGui, QtCore, QtSql
    from PyQt4.uic import loadUiType
except ImportError:
    from PySide import QtGui, QtCore, QtSql
    from loadui import loadUiType

from constants import FIELD_TYPES
from querywidget import QueryWidget
import commands


HISTORY = u'History'
QUERY = u'Query'

form_class, base_class = loadUiType('./widgets/database.ui')


class DatabaseWidet(base_class):
    def __init__(self, database, menu, parent=None):
        super(DatabaseWidet, self).__init__(parent)
        
        self._table = ''
        self._tableicon = QtGui.QIcon(QtGui.QPixmap(":/icons/table.png"))
        self._columnicon = QtGui.QIcon(QtGui.QPixmap(":/icons/table_column.png"))
        self.queryicon = QtGui.QIcon(QtGui.QPixmap(":/icons/script.png"))
        self.histicon = QtGui.QIcon(QtGui.QPixmap(":/icons/calendar_view_day.png"))
        self._menu = menu
        
        self._ui = form_class()
        self._ui.setupUi(self)
        self._ui.splitter.setStretchFactor(1, 1)
        
        self._db = commands.openDatabase(database)
        
        self._model = QtGui.QStandardItemModel()
        self.reload()
        self._ui.tvTables.setModel(self._model)
        
        ## -- add history
        self.addHistory()
        ## -- add a query
        self.addQueryEditor()
        
        self.bindEvents()
        self.setTable(self._model.index(0, 0, QtCore.QModelIndex()))
    
    def bindEvents(self):
        self._ui.tvTables.clicked.connect(self.setTable)
        self._ui.tbTabs.tabCloseRequested.connect(self.removeTab)
        self._ui.tbTabs.currentChanged.connect(self.updateHistory)
        self._model.itemChanged.connect(self.renameTable)
    
    def contextMenuEvent(self, event):
        pos = event.globalPos()
        index = self._ui.tvTables.indexAt(event.pos())
        if index.isValid():
            self._menu.exec_(pos)
            event.accept()
    
    def setTable(self, index):
        self._table = self.__getParentTableIndex(index).data()
        for i in xrange(self._ui.tbTabs.count()):
            widget = self._ui.tbTabs.widget(i)
            if isinstance(widget, QueryWidget):
                widget.setTable(self._table)
    
    def table(self):
        return self._table
    
    def database(self):
        return self._db
    
    def close(self):
        self._db.close()
    
    def renameCurrentTable(self):
        index = self.__getParentTableIndex(self._ui.tvTables.currentIndex())
        self._ui.tvTables.edit(index)
    
    def renameTable(self, item):
        if item.parent():
            ## -- Not a table
            return False
        
        if self._table:
            res, msg = commands.renameTable(self._db, self._table, item.text())
            if res:
                self.reload()
            else:
                QtGui.QMessageBox.critical(
                    self,
                    'Table Error',
                    'Failed to rename table:\n\n%s' % msg
                )
    
    def reload(self):
        self._model.clear()
        dbfields = OrderedDict()
        for table in self._db.tables():
            item = QtGui.QStandardItem(self._tableicon, table)
            self._model.appendRow(item)
            fields = commands.getFieldTypes(self._db, table)
            columns = QtGui.QStandardItem('Columns')
            item.appendRow(columns)
            for field, type_ in fields.iteritems():
                fielditem = QtGui.QStandardItem(self._columnicon, '%s (%s)' % (field, type_))
                columns.appendRow(fielditem)
            
            columns.setText('Columns (%i)' % len(fields.keys()))
            dbfields[table] = fields
        
        self._db.setFields(dbfields)
    
    def addQueryEditor(self):
        qwidget = QueryWidget(self._db, self)
        index = self._ui.tbTabs.addTab(qwidget, self.queryicon, QUERY)
        self._ui.tbTabs.setCurrentIndex(index)
        self.setTable(self._ui.tvTables.currentIndex())
    
    def addHistory(self):
        index = -1
        for i in xrange(self._ui.tbTabs.count()):
            widget = self._ui.tbTabs.widget(i)
            if self._ui.tbTabs.tabText(i) == HISTORY:
                index = i
        
        if index < 0:
            hwidget = QtGui.QTextEdit(self)
            hwidget.setReadOnly(True)
            hwidget.setFontFamily('Courier New')
            index = self._ui.tbTabs.addTab(hwidget, self.histicon, HISTORY)
        
        self._ui.tbTabs.setCurrentIndex(index)
    
    def removeTab(self, index):
        self._ui.tbTabs.removeTab(index)
    
    def updateHistory(self):
        for i in xrange(self._ui.tbTabs.count()):
            if self._ui.tbTabs.tabText(i) == HISTORY:
                widget = self._ui.tbTabs.widget(i)
                widget.clear()
                for line in self._db.history():
                    widget.insertHtml('%s<br />' % line)
    
    def executeQuery(self):
        if self._ui.tbTabs.tabText(self._ui.tbTabs.currentIndex()) == 'Query':
            widget = self._ui.tbTabs.currentWidget()
            widget.executeInput()
    
    def emptyDatabase(self):
        dlg = QtGui.QMessageBox.question(
            self,
            'Empty Database',
            'Are you sure you wish to clear the contents of the database "%s"?' % self._db.databaseName(),
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
        )
        if dlg == QtGui.QMessageBox.Yes:
            res, msg = commands.emptyDatabase(self._db)
            if not res:
                QtGui.QMessageBox.critical(
                    self,
                    'Database Error',
                    'Failed to empty database:\n\n%s' % msg
                )
    
    def truncateTable(self):
        dlg = QtGui.QMessageBox.question(
            self,
            'Truncate Table',
            'Are you sure you wish to clear the contents of the table "%s"?' % self._table,
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
        )
        if dlg == QtGui.QMessageBox.Yes:
            res, msg = commands.truncateTable(self._db, self._table)
            if not res:
                QtGui.QMessageBox.critical(
                    self,
                    'Table Error',
                    'Failed to truncate table:\n\n%s' % msg
                )
    
    def dropTable(self):
        dlg = QtGui.QMessageBox.question(
            self,
            'Drop Table',
            'Are you sure you wish to remove the table "%s" from the database?' % self._table,
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
        )
        if dlg == QtGui.QMessageBox.Yes:
            res, msg = commands.dropTable(self._db, self._table)
            if not res:
                QtGui.QMessageBox.critical(
                    self,
                    'Table Error',
                    'Failed to drop table:\n\n%s' % msg
                )
    
    def __getParentTableIndex(self, index):
        parent = index.parent()
        while parent.isValid():
            index = parent
            parent = index.parent()
        
        return index
