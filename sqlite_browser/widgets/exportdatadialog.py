try:
    from PyQt4 import QtGui, QtCore, QtSql
    from PyQt4.uic import loadUiType
except ImportError:
    from PySide import QtGui, QtCore, QtSql
    from loadui import loadUiType

import serializer
import commands

form_class, base_class = loadUiType('./widgets/exportdata.ui')


class ExportDataDialog(base_class):
    def __init__(self, db, table, parent=None):
        super(ExportDataDialog, self).__init__(parent)
        
        self._ui = form_class()
        self._ui.setupUi(self)
        
        self._db = db
        self._table = table
        self._file = None
        
        fields = commands.getFieldTypes(self._db, self._table).keys()
        model = QtGui.QStringListModel(fields)
        self._ui.lvFields.setModel(model)
        self._ui.lvFields.selectAll()
        
        self._ui.bBrowse.clicked.connect(self.setFile)
        self._ui.buttonBox.accepted.connect(self.export)
        self._ui.bSelectAll.clicked.connect(self._ui.lvFields.selectAll)
        self._ui.bDeselectAll.clicked.connect(self._ui.lvFields.clearSelection)
        self._ui.eFile.textChanged.connect(self.__enableSave)
        self.__enableSave()
    
    def setFile(self):
        index = self._ui.toolBox.currentIndex()
        filetypes = ['CSV (*.csv)', 'JSON (*.json)', 'SQL (*.sql)']
        file_ = QtGui.QFileDialog.getSaveFileName(
            self,
            'Save as',
            filter=filetypes[index]
        )
        self._file = file_
        if file_:
            self._ui.eFile.setText(file_)
    
    def export(self):
        index = self._ui.toolBox.currentIndex()
        fields = [o.data() for o in self._ui.lvFields.selectedIndexes()]
        
        if index == 0:
            writer = serializer.CSVSerializer(self._db, self._table)
            options = {
                'delimiter': self._ui.eDelimeter.text(),
                'lineterminator': self._ui.eLineTerminator.text(),
                'escapechar': self._ui.eEscapeChar.text(),
                'quotechar': self._ui.eQuoteChar.text(),
                'columns': self._ui.ckAddColumns.isChecked(),
            }
        elif index == 1:
            writer = serializer.JSONSerializer(self._db, self._table)
            options = {
                'indent': self._ui.sIndent.value(),
                'columns': self._ui.ckColumnTypes.isChecked()
            }
        else:
            writer = serializer.SQLSerializer(self._db, self._table)
            options = {
                'columns': self._ui.rbStructure.isChecked() or self._ui.rbStructureData.isChecked(),
                'data': self._ui.rbData.isChecked() or self._ui.rbStructureData.isChecked(),
            }
        
        if self._file:
            text = writer.dumps(fields, options)
            fh = open(self._file, 'wb+')
            fh.write(text)
            fh.close()
    
    def __enableSave(self, val=None):
        self._ui.buttonBox.button(QtGui.QDialogButtonBox.Save).setEnabled(bool(val))
