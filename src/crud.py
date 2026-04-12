import os
import sqlite3
from dotenv import load_dotenv
from fastapi import HTTPException
import database


def add_forms(email,cv_link= None,video_link= None):
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute(
                    '''
                    INSERT INTO CV (email,cv_link,video_link,status_id)
                    VALUES (?,?,?,(SELECT id FROM Statuses WHERE status = 'waiting'))
                    ''', (email,cv_link,video_link)
                       )
        conn.commit()

    except sqlite3.Error as e:
        print(f"Database error {e}")
        HTTPException(status_code=500, detail="Database connection error")

    finally:
        if conn:
            conn.close()


def read_database():
    try:
        conn = database.get_connection()
        conn.row_factory = sqlite3.Row  # powoduje zwracanie danych wraz z nazwą kolumny
        cursor = conn.cursor()
        cursor.execute('''
                       SELECT email,cv_link,video_link,Statuses.status FROM CV 
                        INNER JOIN Statuses
                        on CV.status_id = Statuses.id
                       ''')
        data = [dict(row)  for row in cursor.fetchall()]
        print(f"Database records:\n {data}")
    except sqlite3.Error as e:
        print(f"Database error {e}")
        HTTPException(status_code=500, detail="Database connection error")
    finally:
        if conn:
            conn.close()
    return data


def give_waiting_change_to_pending():
    try:
        conn = database.get_connection()
        conn.row_factory = sqlite3.Row  # powoduje zwracanie danych wraz z nazwą kolumny
        cursor = conn.cursor()

        # searching for waiting in table
        cursor.execute('''SELECT id FROM Statuses
                          WHERE status = 'waiting' ''')
        waiting_id = cursor.fetchall()

        cursor.execute('''
                       SELECT email,cv_link,video_link,Statuses.status FROM CV 
                        INNER JOIN statuses
                        on CV.status_id = Statuses.id
                        WHERE Statuses.status = 'waiting'
                       ''')
        data = [dict(row)  for row in cursor.fetchall()]
        cursor.execute('''
                        UPDATE CV
                        SET status_id = (SELECT id FROM Statuses WHERE status = 'pending')
                        where status_id = (SELECT id FROM Statuses WHERE status = 'waiting')
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error{e}")
        raise HTTPException(status_code=500, detail="Database connection error")
    finally:
        if conn:
            conn.close()
    print(data)
    return data



