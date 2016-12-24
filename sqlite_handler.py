import sqlite3 as sq

class database:
    """docstring for database."""
    def __init__(self, path):
        self.path = path
        self.conn = sq.connect(path, check_same_thread=False)

    def insert(self, table, values):
        def str_values(values):
            def mystr(x):
                if isinstance(x, str):
                    return '"{}"'.format(x)
                else:
                    return str(x)

            return ','.join(map(mystr, values))

        query = "insert into {table_} values ({values_})".format(table_=table, values_=str_values(values))

        self.conn.execute(query)
        self.conn.commit()

    def select_all(self, table):
        return self.conn.execute('select * from {}'.format(table))

    def close(self):
        self.conn.close()
