
import sys
try:
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
    from PyQt4 import QtGui, QtCore, QtSql
    from PyQt4.uic import loadUiType
except ImportError:
    from PySide import QtGui, QtCore, QtSql
    from loadui import loadUiType

# from sqlpy_main import Ui_MainWindow
from widgets.databasewidget import DatabaseWidet
from widgets.scriptdialog import ScriptDialog

import commands

form_class, base_class = loadUiType('./widgets/sqlpy.ui')


class Window(base_class):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        
        self._ui = form_class()
        self._ui.setupUi(self)
        
        self.bindEvents()
    
    def closeEvent(self, event):
        self.removeAllDatabases()
        return super(Window, self).closeEvent(event)
    
    def bindEvents(self):
        self._ui.actionOpen.triggered.connect(self.addDatabase)
        self._ui.actionExecute_All_Queries.triggered.connect(self.executeQuery)
        self._ui.tbDatabases.tabCloseRequested.connect(self.removeDataBase)
        self._ui.tbDatabases.currentChanged.connect(self.tabChangeHandler)
        self._ui.actionTruncate_Table.triggered.connect(self.truncateTable)
        self._ui.actionNew_Query_Editor.triggered.connect(self.newQueryEditor)
        self._ui.actionHistory.triggered.connect(self.addHistory)
        self._ui.actionRefresh.triggered.connect(self.reloadDatabase)
        self._ui.actionClose.triggered.connect(self.removeDataBase)
        self._ui.actionClose_All.triggered.connect(self.removeAllDatabases)
        self._ui.actionNew.triggered.connect(self.newDatabase)
        self._ui.actionNew_Memory_Database.triggered.connect(self.newMemoryDatabase)
        self._ui.actionQuit.triggered.connect(self.close)
        self._ui.actionDrop_Table.triggered.connect(self.dropTableHander)
        self._ui.actionEmpty_Database.triggered.connect(self.emptyDatabaseHandler)
        self._ui.actionTruncate_Table.triggered.connect(self.truncateTableHandler)
        self._ui.actionRename_Table.triggered.connect(self.renameTableHandler)
        self._ui.actionExecute_Script.triggered.connect(self.executeScriptHandler)
        self._ui.actionAbout.triggered.connect(self.aboutHandler)
    
    def tabChangeHandler(self, index):
        widget = self._ui.tbDatabases.widget(index)
        if widget:
            self.setTableActionsEnabled(bool(widget.table()))
        else:
            self.setTableActionsEnabled(False)
    
    def addDatabase(self, dbfile=None):
        if not dbfile:
            dbfile = QtGui.QFileDialog.getOpenFileName(self, 'Pick a SQLite DB file')
            if isinstance(dbfile, (list, tuple)):
                dbfile = dbfile[0]
        
        if dbfile:
            if self.hasDatabase(dbfile) == -1:
                name = dbfile.replace('\\', '/').split('/')[-1]
                dbicon = QtGui.QIcon(QtGui.QPixmap(":/icons/database.png"))
                widget = DatabaseWidet(dbfile, self._ui.menuTable, self)
                index = self._ui.tbDatabases.addTab(widget, dbicon, name)
            else:
                index = self.hasDatabase(dbfile)
            
            self._ui.tbDatabases.setCurrentIndex(index)
            self.setDatabaseActionsEnabled(True)
    
    def removeDataBase(self, index):
        if index is False:
            index = self._ui.tbDatabases.currentIndex()
        widget = self._ui.tbDatabases.widget(index)
        widget.close()
        self._ui.tbDatabases.removeTab(index)
        
        if self._ui.tbDatabases.count() == 0:
            self.setDatabaseActionsEnabled(False)
    
    def removeAllDatabases(self):
        for i in xrange(self._ui.tbDatabases.count()):
            self.removeDataBase(0)
        
        self.setDatabaseActionsEnabled(False)
    
    def hasDatabase(self, name):
        for i in xrange(self._ui.tbDatabases.count()):
            widget = self._ui.tbDatabases.widget(i)
            if widget.database().databaseName() == name:
                return i
        
        return -1
    
    def executeQuery(self):
        widget = self._ui.tbDatabases.currentWidget()
        if widget:
            widget.executeQuery()
    
    def reloadDatabase(self):
        widget = self._ui.tbDatabases.currentWidget()
        if widget:
            widget.reload()
    
    def truncateTable(self):
        widget = self._ui.tbDatabases.currentWidget()
        if widget:
            widget.truncateTable()
    
    def newQueryEditor(self):
        widget = self._ui.tbDatabases.currentWidget()
        if widget:
            widget.addQueryEditor()
    
    def addHistory(self):
        widget = self._ui.tbDatabases.currentWidget()
        if widget:
            widget.addHistory()
    
    def newDatabase(self):
        dbfile = QtGui.QFileDialog.getSaveFileName(
            self,
            'Choose database file',
        )
        if isinstance(dbfile, (list, tuple)):
            dbfile = dbfile[0]
        
        if dbfile:
            if commands.newDatabase(dbfile):
                self.addDatabase(dbfile)
    
    def newMemoryDatabase(self):
        self.addDatabase(':memory:')
    
    def setTableActionsEnabled(self, enabled=True):
        actions = [
            self._ui.actionDrop_Table,
            self._ui.actionRename_Table,
            self._ui.actionTruncate_Table,
        ]
        
        for action in actions:
            action.setEnabled(enabled)
    
    def setDatabaseActionsEnabled(self, enabled=True):
        actions = [
            self._ui.actionClose,
            self._ui.actionClose_All,
            self._ui.actionCreate_Table,
            self._ui.actionEmpty_Database,
            self._ui.actionExecute_All_Queries,
            self._ui.actionExecute_Script,
            self._ui.actionHistory,
            self._ui.actionInfo,
            self._ui.actionRefresh,
            self._ui.actionNew_Query_Editor,
        ]
        
        for action in actions:
            action.setEnabled(enabled)
    
    def emptyDatabaseHandler(self):
        widget = self._ui.tbDatabases.currentWidget()
        if widget:
            widget.emptyDatabase()
            widget.reload()
    
    def dropTableHander(self):
        widget = self._ui.tbDatabases.currentWidget()
        if widget:
            widget.dropTable()
            widget.reload()
    
    def truncateTableHandler(self):
        widget = self._ui.tbDatabases.currentWidget()
        if widget:
            widget.truncateTable()
            widget.reload()
    
    def renameTableHandler(self):
        widget = self._ui.tbDatabases.currentWidget()
        if widget:
            widget.renameCurrentTable()
    
    def executeScriptHandler(self):
        widget = self._ui.tbDatabases.currentWidget()
        db = widget.database() if widget else None
        dlg = ScriptDialog(db, self)
        dlg.exec_()
        
        self.reloadDatabase()
    
    def aboutHandler(self):
        QtGui.QMessageBox.about(
            self,
            'PySQLite Browser',
            'some text here'
        )
    


def main():
    app = QtGui.QApplication(sys.argv)
    
    win = Window()
    win.show()
    
    sys.exit(app.exec_())

    
if __name__ == '__main__':
    main()