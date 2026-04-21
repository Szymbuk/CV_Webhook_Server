import sqlite3
from fastapi import HTTPException
import database


def add_forms(email,cv_name,cv_file):
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute(
                    '''
                    INSERT INTO CV (email,cv_name,cv_file,status_id)
                    VALUES (?,?,?,(SELECT id FROM Statuses WHERE status = 'waiting'))
                    ''', (email,cv_name,cv_file)
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
        cursor = conn.cursor()
        cursor.execute('''
                       SELECT * FROM CV 
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


def give_waiting():
    try:
        conn = database.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
                       SELECT * FROM CV 
                        INNER JOIN statuses
                        on CV.status_id = Statuses.id
                        WHERE Statuses.status = 'waiting'
                       ''')
        data = [dict(row)  for row in cursor.fetchall()]
        cursor.execute('''
                        UPDATE CV
                        SET status_id = (SELECT id FROM Statuses WHERE status = 'sent')
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


def delete():
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
                        DELETE FROM CV
                        WHERE status_id = (SELECT id FROM Statuses WHERE status = 'sent')                    
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error{e}")
        raise HTTPException(status_code=500, detail="Database connection error")
    finally:
        if conn:
            conn.close()

