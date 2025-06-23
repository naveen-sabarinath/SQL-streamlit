import sqlite3


def get_connection(db_name = "students.db"):
    return sqlite3.connect(db_name)

def execute_query(connection,query,value = None):
    cursor = connection.cursor()
    if value:
        cursor.execute(query, value)
    else:
        cursor.execute(query)
    connection.commit()
    return cursor
