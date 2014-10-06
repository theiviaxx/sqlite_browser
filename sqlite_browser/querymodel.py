
import time
import re

try:
    from PyQt4 import QtGui, QtCore, QtSql
    Signal = QtCore.pyqtSignal
    Null = QtCore.QPyNullVariant
except ImportError:
    from PySide import QtGui, QtCore, QtSql
    Signal = QtCore.Signal
    Null = None

from sqlitedatabase import SQLiteQuery
import commands


class QueryModel(QtCore.QAbstractTableModel):
    dataCommitted = Signal()
    
    def __init__(self, parent=None):
        super(QueryModel, self).__init__(parent)
        
        self._query = ''
        self._db = None
        self._history = []
        self._data = [[]]
        self._headers = []
        self._table = ''
        self._updates = []
        self._inserts = []
        self._queue = []
        self._rowid = 0
        self._readonly = False
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._data)
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._headers)
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        fieldtype = self._db.getType(self._table, index.column())
        if role == QtCore.Qt.DisplayRole:
            if fieldtype == 'real':
                return str(self._data[index.row()][index.column()])
            elif fieldtype == 'text':
                value = self._data[index.row()][index.column()]
                if value is None:
                    return '(NULL)'
                
                if isinstance(value, (str, unicode)):
                    value = repr(value)[2:-1]
                else:
                    value = str(value)
                              
                return value
            elif fieldtype == 'blob':
                return '(Binary/Image)'
            
            return self._data[index.row()][index.column()]
        elif role == QtCore.Qt.EditRole:
            return self._data[index.row()][index.column()]
        
        return None
    
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        self._data[index.row()][index.column()] = value
        self._rowid = self.rowid(index)
        quoted = self._db.getType(self._table, index.column()) == 'text' or \
               not commands.istext(value)
        if quoted:
            value = "'%s'" % value
        
        self._updates.append((self._headers[index.column()], value))

        self.dataChanged.emit(index, index)
        return True
    
    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._headers[section]
    
    def flags(self, index):
        flags = super(QueryModel, self).flags(index)
        if not self._readonly:
            flags |= QtCore.Qt.ItemIsEditable
        
        return flags
    
    def insertRows(self, row, count, parent, data):
        self._data = [[]]
        self.beginInsertRows(parent, row, row + count - 2)
        self._data = data
        self.endInsertRows()

    def appendRow(self, row):
        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())
        self._data.append(row)
        self._inserts.append(row)
        self.endInsertRows()

        self.dataChanged.emit(self.index(self.rowCount(), 0), self.index(self.rowCount(), len(self._headers)))
    
    def appendInsertRow(self):
        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), 1)
        self._data.append(self._db.fields(self._table).keys())
        self.endInsertRows()
    
    def removeRows(self, row, count, parent):
        self.beginInsertRows(parent, row, row + count)
        self._data = self._data[row:row + count]
        self.endInsertRows()
    
    def reset(self):
        self.beginResetModel()
        self._data = [[]]
        self.endResetModel()
    
    ## -- new methods
    def rowid(self, index):
        return index.row() + 1 ## -- 1 based row IDs
    
    def setDatabase(self, db):
        self._db = db
    
    def setQuery(self, query):
        self._query = query
        self.query()
    
    def setTable(self, table):
        self._table = table
        self.setHeaders()
    
    def setHeaders(self, headers=None):
        self._headers = []
        if headers is None:
            for f in self._db.fields(self._table).iterkeys():
                self._headers.append(f)
        else:
            self._headers = headers
    
    def setReadOnly(self, val):
        self._readonly = val
    
    def query(self):
        q = SQLiteQuery()
        q.exec_(self._query)
        self._db.appendQuery(q)
        self.setRecords(q)
    
    def setRecords(self, result):
        self.reset()
        
        ids = []
        count = result.record().count()
        while result.next():
            i = 0
            val = result.value(i)
            fields = []
            while i < count:
                try:
                    if isinstance(val, QtCore.QPyNullVariant):
                        val = None
                except AttributeError:
                    ## -- PySide should handle this correctly
                    pass
                fields.append(val)
                i += 1
                val = result.value(i)
            ids.append(fields)
        
        self.insertRows(0, len(ids), QtCore.QModelIndex(), ids)
    
    def commitQueue(self):
        self._db.transaction()
        success = True
        changed = False
        if self._updates:
            q = SQLiteQuery()
            query = u"UPDATE {table} SET {sets} WHERE rowid = {rowid}"
            sets = ','.join(['%s = %s' % (str(x), y) for x, y in self._updates])
            query = query.format(table=self._table, sets=sets, rowid=self._rowid)
            q.exec_(query)
            err = q.lastError()
            if err.isValid():
                self._db.rollback()
                success = False
            else:
                self._db.commit()
                self._db.appendQuery(q)
            
            self._updates = []
            changed = True

        for insert in self._inserts:
            q = SQLiteQuery()
            for i, v in enumerate(insert):
                if isinstance(v, (str, unicode)):
                    insert[i] = "'%s'" % v
                else:
                    insert[i] = str(v)
            
            query = u"INSERT INTO {table} ({fields}) VALUES ({values})".format(
                table=self._table,
                fields=','.join(self._headers),
                values=','.join(insert)
            )
            q.exec_(query)
            err = q.lastError()
            if err.isValid():
                self._db.rollback()
                success = False
            else:
                self._db.commit()
                self._db.appendQuery(q)

            self._inserts = []
        
        if changed:
            self.dataCommitted.emit()
        
        return success
    
    def flushQueue(self):
        self._updates = []
        self._inserts = []
        self.query()
        self.dataCommitted.emit()



class QuerySortModel(QtGui.QSortFilterProxyModel):
    def lessThan(self, left, right):
        l = self.sourceModel().data(left)
        r = self.sourceModel().data(right)
        
        return l > r
