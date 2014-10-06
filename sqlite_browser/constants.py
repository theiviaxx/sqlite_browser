
try:
    from PyQt4 import QtGui, QtCore, QtSql
    from PyQt4.uic import loadUiType
except ImportError:
    from PySide import QtGui, QtCore, QtSql
    from loadui import loadUiType

FIELD_TYPES = {
    2: 'INTEGER',
    10: 'TEXT',
    12: 'BYTEARRAY',
}
KEYWORDS = ['ABORT','ACTION','ADD','AFTER','ALL','ALTER','ANALYZE','AND','AS','ASC','ATTACH','AUTOINCREMENT','BEFORE','BEGIN','BETWEEN',
'BY','CASCADE','CASE','CAST','CHECK','COLLATE','COLUMN','COMMIT','CONFLICT','CONSTRAINT','CREATE','CROSS','CURRENT_DATE',
'CURRENT_TIME','CURRENT_TIMESTAMP','DATABASE','DEFAULT','DEFERRABLE','DEFERRED','DELETE','DESC','DETACH','DISTINCT','DROP',
'EACH','ELSE','END','ESCAPE','EXCEPT','EXCLUSIVE','EXISTS','EXPLAIN','FAIL','FOR','FOREIGN','FROM','FULL','GLOB','GROUP',
'HAVING','IF','IGNORE','IMMEDIATE','IN','INDEX','INDEXED','INITIALLY','INNER','INSERT','INSTEAD','INTERSECT','INTO','IS',
'ISNULL','JOIN','KEY','LEFT','LIKE','LIMIT','MATCH','NATURAL','NO','NOT','NOTNULL','NULL','OF','OFFSET','ON','OR','ORDER',
'OUTER','PLAN','PRAGMA','PRIMARY','QUERY','RAISE','REFERENCES','REGEXP','REINDEX','RELEASE','RENAME','REPLACE','RESTRICT',
'RIGHT','ROLLBACK','ROW','SAVEPOINT','SELECT','SET','TABLE','TEMP','TEMPORARY','THEN','TO','TRANSACTION','TRIGGER','UNION',
'UNIQUE','UPDATE','USING','VACUUM','VALUES','VIEW','VIRTUAL','WHEN','WHERE']

PUNCTUATION = ['(', ')', ';', '+', '-', '*', '/', '[', ']', '|', '.', ',']
FUNCTIONS = ['AVG', 'COUNT', 'FIRST', 'LAST', 'MAX', 'MIN', 'SUM', 'UCASE', 'LCASE', 'MID', 'LEN', 'ROUND', 'NOW', 'FORMAT']


## -- Formats
WORD = QtGui.QTextCharFormat()
WORD.setForeground(QtGui.QColor('#5e5eff'))
WORD.setFontCapitalization(QtGui.QFont.AllUppercase)
PUNC = QtGui.QTextCharFormat()
PUNC.setForeground(QtGui.QColor('#c23a00'))
FUNC = QtGui.QTextCharFormat()
FUNC.setForeground(QtGui.QColor('#f462ee'))
STRING = QtGui.QTextCharFormat()
STRING.setForeground(QtGui.QColor('#ff0000'))