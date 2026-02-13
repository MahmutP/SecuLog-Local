import sqlite3
import os
from datetime import datetime

DB_NAME = "vulnerabilities.db"

def connect_db():
    """
    Establish a connection to the SQLite database.
    """
    conn = sqlite3.connect(DB_NAME)
    # Enable foreign key support
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize_tables():
    """
    Creates the necessary tables if they do not exist.
    Tables: targets, vulnerabilities
    """
    conn = connect_db()
    cursor = conn.cursor()

    # Targets Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            target_url TEXT UNIQUE,
            target_type TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Vulnerabilities Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vulnerabilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_id INTEGER,
            title TEXT NOT NULL,
            severity TEXT NOT NULL,
            cvss_score REAL,
            vuln_type TEXT,
            description TEXT,
            poc_steps TEXT,
            status TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (target_id) REFERENCES targets(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database initialized: {os.path.abspath(DB_NAME)}")

if __name__ == "__main__":
    initialize_tables()
