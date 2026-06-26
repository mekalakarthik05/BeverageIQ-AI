import pytest
import sqlite3
from config import DATABASE_PATH

def test_database_exists():
    assert DATABASE_PATH.exists(), f"Database not found at {DATABASE_PATH}"

def test_database_tables():
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    conn.close()
    
    assert "products" in tables
    assert "stores" in tables
    assert "sales" in tables
    assert "inventory" in tables
