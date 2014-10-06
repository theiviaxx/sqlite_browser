import StringIO
import json
import csv

from sqlitedatabase import SQLiteQuery
import commands


class Serializer(object):
    OPTIONS = {}
    def __init__(self, db, table):
        self._db = db
        self._table = table
    
    def data(self, fields):
        rows = []
        fields = '*' if fields is None else ','.join(fields)
        query = "SELECT {fields} FROM {table}".format(
            table=self._table,
            fields=fields
        )
        q = SQLiteQuery(self._db)
        q.exec_(query)
        count = q.record().count()
        while q.next():
            i = 0
            val = q.value(i)
            cols = []
            while i < count:
                cols.append(val)
                i += 1
                val = q.value(i)
            rows.append(cols)
        
        return rows
    
    def loads(self, fields=None, options={}):
        pass
    
    def dumps(self, fields=None, options={}):
        pass


class CSVSerializer(Serializer):
    def dumps(self, fields=None, options={}):
        rows = self.data(fields)
        
        if options.get('columns'):
            if fields is None:
                fields = commands.getFieldTypes(self._db, self._table).keys()
            rows.insert(0, fields)
        
        delimiter = options.get('delimeter', ',')
        escapechar = options.get('escapechar', '\\\\')
        lineterminator = options.get('lineterminator', '\\r\\n')
        quotechar = options.get('quotechar', '"')
        
        s = StringIO.StringIO()
        w = csv.writer(
            s,
            delimiter=delimiter.decode('string-escape'),
            escapechar=escapechar.decode('string-escape'),
            lineterminator=lineterminator.decode('string-escape'),
            quotechar=quotechar.decode('string-escape'),
        )
        w.writerows(rows)
        s.seek(0)
        
        return s.read()


class JSONSerializer(Serializer):
    OPTIONS = {}
    def dumps(self, fields=None, options={}):
        rows = self.data(fields)
        indent = options.get('indent', 4)
        if options.get('columns'):
            if fields is None:
                fields = commands.getFieldTypes(self._db, self._table).keys()
            rows.insert(0, fields)
        
        return json.dumps(rows, indent=indent)


class TextSerializer(Serializer):
    OPTIONS = {}
    def dumps(self, fields=None, options={}):
        rows = self.data(fields)
        
        if fields is None:
            fields = commands.getFieldTypes(self._db, self._table).keys()
        
        columnwidths = [0 for i in range(len(fields))]
        
        if options.get('columns'):
            rows.insert(0, fields)
        
        for row in iter(rows):
            for i, val in enumerate(row):
                columnwidths[i] = max(len(str(val)), columnwidths[i])
        
        if options.get('columns'):
            dashes = []
            for i, header in enumerate(fields):
                dashes.append(unicode('-' * (columnwidths[i])))
            
            rows.insert(1, dashes)
        
        s = u''        
        for row in iter(rows):
            for i, val in enumerate(row):
                s += unicode(val).ljust(columnwidths[i] + 2)
            s += '\n'
        
        return s


class SQLSerializer(Serializer):
    def dumps(self, fields=None, options={}):
        rows = self.data(fields)
        queries = []
        if fields is None:
            fields = commands.getFieldTypes(self._db, self._table).keys()
        
        if options.get('columns'):
            queries.append(commands.tableCreateScript(self._db, self._table))
        
        if options.get('data'):
            for row in rows:
                for i, v in enumerate(row):
                    if isinstance(v, (str, unicode)):
                        row[i] = "'%s'" % repr(v)[2:-1]
                    else:
                        row[i] = str(v)
                
                query = "INSERT INTO {table} ({fields}) VALUES ({values});".format(
                    table=self._table,
                    fields=','.join(fields),
                    values=','.join(row)
                )
                queries.append(query)
        
        return '\n'.join(queries)