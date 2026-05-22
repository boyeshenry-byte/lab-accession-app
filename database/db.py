import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()
db_path = os.getenv('DB_PATH', r"R:\Labs\ImmunomonitoringLaboratory\Patient Sample Log\lab_accession.db")
schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')

def get_db_connection(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_db_schema(schema_path):
    with open(schema_path, 'r') as f:
        return f.read()

def init_db(db_path):
    conn = get_db_connection(db_path)
    with conn:
        schema = get_db_schema(schema_path)
        conn.executescript(schema)
    conn.close()

if __name__ == '__main__':
    init_db(db_path)
    print(f"Database initialized at {db_path}") 