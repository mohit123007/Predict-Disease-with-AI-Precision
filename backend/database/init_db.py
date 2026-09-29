import os
import sqlite3

DB_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(DB_DIR, 'app.db')

SCHEMA_PATH = os.path.join(DB_DIR, 'schema.sql')


def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            sql = f.read()
        conn.executescript(sql)
        conn.commit()
        conn.close()
        print('Initialized database at', DB_PATH)
    else:
        print('Database already exists at', DB_PATH)


if __name__ == '__main__':
    init_db()
