import sqlite3
import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import DATABASE_PATH

def get_connection():
    """Returns a connection to the SQLite database."""
    return sqlite3.connect(DATABASE_PATH)

def execute_query_to_df(query: str, params: tuple = ()) -> pd.DataFrame:
    """
    Executes a SQL query and returns the results as a Pandas DataFrame.
    Returns an empty DataFrame if query fails or returns no results.
    """
    try:
        conn = get_connection()
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        print(f"Database query error: {e}")
        return pd.DataFrame()
