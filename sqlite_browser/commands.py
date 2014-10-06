import string
from collections import OrderedDict
import sqlite3

try:
    from PyQt4 import QtGui, QtCore, QtSql
except ImportError:
    from PySide import QtGui, QtCore, QtSql

from constants import FIELD_TYPES
from sqlitedatabase import SQLiteDatabase, SQLiteQuery

def transaction(db, table, query):
    db.transaction()
    q = SQLiteQuery(db)
    q.exec_(query)
    err = q.lastError()
    if err.isValid():
        db.rollback()
        
        return False, err.databaseText()
    
    db.appendQuery(q)
    
    return True, None

def newDatabase(name):
    sqlite3.connect(name)
    
    return True

def openDatabase(name=None):
    dbname = name if name is not None else ':memory:'
    qdb = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    db = SQLiteDatabase(qdb)
    db.setDatabaseName(dbname)
    db.open()
    
    return db

def openMemoryDatabase():
    return openDatabase()
    
def getFieldTypes(db, table):
    """ Returns a dict of field names to field types
    
    :param db: Database object to check
    :type db: QSqlDatabase
    :param table: Database table to get values for
    :type table: str
    :returns: dict
    """
    data = OrderedDict()
    q = db.exec_("PRAGMA table_info(%s)" % table)
    hasmore = q.next()
    while hasmore:
        name = q.value(1)
        type_ = q.value(2)
        data[name] = type_
        hasmore = q.next()
    
    return data

def truncateTable(db, table):
    """Drops then creates the table
    
    :param db: Database to operate on
    :type db: QSqlDatabase
    :param table: Table to truncate
    :type table: str
    """
    fields = getFieldTypes(db, table)
    fieldstr = ','.join(['%s %s' % (k, v) for k, v in fields.iteritems()])
    drop = "DROP TABLE IF EXISTS %s" % table
    create = "CREATE TABLE IF NOT EXISTS {table} ({fields})".format(
        table=table,
        fields=fieldstr
    )
    
    res, msg = transaction(db, table, drop)
    if not res:
        return res, msg
    
    res, msg = transaction(db, table, create)
    if not res:
        return res, msg
    
    db.commit()
    
    return True, None

def dropTable(db, table):
    """Drops the table from the database"""
    fields = getFieldTypes(db, table)
    query = "DROP TABLE IF EXISTS {table}".format(
        table=table
    )
    res, msg = transaction(db, table, query)
    if not res:
        db.rollback()
        
        return res, msg
    
    db.commit()
    
    return True, None    

def emptyDatabase(db):
    """Drops all tables from database"""
    tables = db.tables()
    for table in tables:
        query = "DROP TABLE IF EXISTS {table}".format(
            table=table
        )
        res, msg = transaction(db, table, query)
        if not res:
            db.rollback()
            
            return res, msg
    
    db.commit()
    
    return True, None

def renameTable(db, table , name):
    """Renames the given table to name"""
    query = "ALTER TABLE {table} RENAME TO {name}".format(
        table=table,
        name=name
    )
    res, msg = transaction(db, table, query)
    if not res:
        db.rollback()
        
        return res, msg
    
    db.commit()
    
    return True, None

def insertRow(db, table):
    """Inserts a new row into the table"""
    fields = getFieldTypes(db, table)
    query = "INSERT INTO {table} ({fields})".format(
        table=table,
        fields=','.join(fields.keys())
    )
    q = SQLiteQuery(db)
    q.exec_(query)
    db.appendQuery(q)

def tableCreateScript(db, table):
    data = []
    q = db.exec_("PRAGMA table_info(%s)" % table)
    hasmore = q.next()
    create = "CREATE TABLE `%s` (" % table
    while hasmore:
        create += '\n    `%s` %s' % (
            q.value(1),
            q.value(2),
        )
        if not q.value(3):
            create += ' NOT NULL'
        
        if not isinstance(q.value(4), QtCore.QPyNullVariant):
            create += ' DEFAULT %s' % q.value(4)
        create += ','
        hasmore = q.next()
    
    create = create[:-1]
    create += '\n);'
    
    return create
    

def deleteRows(db, table, rows):
    """Deletes rows from db.table"""
    pass

def duplicateRows(db, table, rows):
    """duplicates rows in db.table"""
    pass

text_characters = "".join(map(chr, range(32, 127)) + list("\n\r\t\b"))
_null_trans = string.maketrans("", "")
def istext(s):
    if not isinstance(s, (str, unicode)):
        return 0
    
    if "\0" in s:
        return 0
    
    if not s:  # Empty files are considered text
        return 1

    # Get the non-text characters (maps a character to itself then
    # use the 'remove' option to get rid of the text characters.)
    if isinstance(s, unicode):
        return 1

    t = s.translate(_null_trans, text_characters)

    # If more than 30% non-text characters, then
    # this is considered a binary file
    if len(t) / len(s) > 0.30:
        return 0
    return 1