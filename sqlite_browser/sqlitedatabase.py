
import json
import time

try:
    from PyQt4 import QtGui, QtCore, QtSql
    Signal = QtCore.pyqtSignal
except ImportError:
    from PySide import QtGui, QtCore, QtSql
    Signal = QtCore.Signal


class SQLiteDatabase(QtSql.QSqlDatabase):
    queriesChanged = Signal()
    
    def __init__(self, *args):
        super(SQLiteDatabase, self).__init__(*args)
        
        self._history = []
        self._fields = {}
    
    def history(self):
        return self._history
    
    def fields(self, table):
        if table:
            return self._fields[table]
        return {}
    
    def appendQuery(self, query):
        qstring = u'<span style="font-family: Courier New;"><span style="color: #008080;">/*[{time}][{duration} ms]*/</span> {query}</span>'
        self._history.append(qstring.format(
            time=time.strftime("%I:%M:%S %p", time.gmtime()),
            duration=int(query.time() * 1000),
            query=query.lastQuery()
        ))
    
    def setFields(self, fields):
        self._fields = fields
    
    def getType(self, table, index):
        if not table:
            return 'text'
        return self._fields[table].values()[index]


class SQLiteQuery(QtSql.QSqlQuery):
    def __init__(self, *args):
        super(SQLiteQuery, self).__init__(*args)
        
        self._time = 0.0
    
    def exec_(self, query):
        now = time.clock()
        res = super(SQLiteQuery, self).exec_(query)
        self._time = time.clock() - now
        
        return res
    
    def time(self):
        return self._time