import sqlite3
import os
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()
DATABASE_NAME = os.getenv("DATABASE")

def get_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # creating reference table for statuses
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS Statuses
                       (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           status TEXT UNIQUE
                       )
                       ''')

        # creating main table for cv's
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS CV
                       (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           email TEXT,
                           cv_link TEXT,
                           video_link TEXT,
                           status_id INTEGER REFERENCES Statuses (id)
                        )
                        ''')

        # inserting values to satuses table
        cursor.execute('''
                       INSERT OR IGNORE INTO Statuses (status)
                       VALUES ('waiting')
                       ''')
        cursor.execute('''
                       INSERT OR IGNORE INTO Statuses (status)
                       VALUES ('pending')
                       ''')
        cursor.execute('''
                       INSERT OR IGNORE INTO Statuses (status)
                       VALUES ('finished')
                       ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error{e}")
        raise HTTPException(status_code=500, detail="Database connection error")
    finally:
        if conn:
            conn.close()
    print("database and tables created,")