import sqlite3
from typing import Any, Generator

from fastapi import HTTPException
from fastapi.params import Depends

import database


def add_forms(email,cv_name,cv_file,position,github):
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
                       SELECT CV.id, email, cv_name, status FROM CV 
                        INNER JOIN Statuses
                        on CV.status_id = Statuses.id
                       ''')
        data = [dict(row)  for row in cursor.fetchall()]
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
    return data


def delete_sent():
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


def change_to_waiting():
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
                        UPDATE CV
                        SET status_id = (SELECT id FROM Statuses WHERE status = 'waiting')
                        where status_id = (SELECT id FROM Statuses WHERE status = 'set')
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error{e}")
        raise HTTPException(status_code=500, detail="Database connection error")
    finally:
        if conn:
            conn.close()






from sqlmodel import Session, create_engine, SQLModel,select,col,update,delete
import os
from dotenv import load_dotenv
from schemas import BaseCV,Statuses,DatabaseCV

load_dotenv()
DATABASE_NAME = os.getenv("DATABASE")
sqlite_url = f"sqlite:///{DATABASE_NAME}_test"
engine = create_engine(sqlite_url)


def create_tables():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        existing_status = session.exec(select(Statuses)).first()
        if not existing_status:
            s1 = Statuses(status='waiting')
            s2 = Statuses(status='sent')
            s3 = Statuses(status='pending')
            s4 = Statuses(status='finished')
            session.add_all([s1,s2,s3,s4])
            session.commit()
        return "Successfully created tables"


def add_forms_new(cv: BaseCV) -> DatabaseCV:
    with Session(engine) as session:
        waiting_statement = select(Statuses).where(Statuses.status=='waiting')
        waiting_id = session.exec(waiting_statement).first().id

        db_cv = DatabaseCV.model_validate(cv)
        db_cv.status= waiting_id
        session.add(db_cv)
        session.commit()
        session.refresh(db_cv)
        return db_cv


def change_from_to(current_status: str, desired_status: str):
    with Session(engine, expire_on_commit=False) as session:
        current_status_statement = select(Statuses).where(Statuses.status == current_status)
        current_status_id = session.exec(current_status_statement).first().id

        desired_status_statement = select(Statuses).where(Statuses.status == desired_status)
        desired_status_id = session.exec(desired_status_statement).first().id

        statement = select(DatabaseCV).join(Statuses).where(Statuses.id == current_status_id)
        data = session.exec(statement).all()
        data_before_update = [cv.model_copy() for cv in data]

        statement_changing = update(DatabaseCV).where(DatabaseCV.status == current_status_id).values(status = desired_status_id)
        session.exec(statement_changing)

        session.commit()
        return data_before_update


def delete_finished():
    with Session(engine) as session:
        finished_status_statement = select(Statuses).where(Statuses.status == "finished")
        finished_status_id = session.exec(finished_status_statement).first().id


        statement_changing = delete(DatabaseCV).where(DatabaseCV.status == finished_status_id)
        session.exec(statement_changing)
        session.commit()


def read_database_new():
    with Session(engine) as session:
        statement = select(DatabaseCV,Statuses).join(Statuses)
        data = session.exec(statement).all()
        formatted_data = [{"cv": cv, "status": status} for cv, status in data]

        return formatted_data



if __name__ == "__main__":
    # create_tables()
    # print(read_database_new())
    # cv = BaseCV(email="alamakota@gmail.com",cv_name="jakaś_nazwa",cv="jakiś content", position_name = "software engineer")
    #
    # add_forms_new(cv)
    # print("Po")
    # print(read_database_new())

    print("przed")
    print(read_database_new())
    data = change_from_to("sent","finished")
    print("po")
    print(read_database_new())
    print("\n\n")
    for cv in data:
        print(cv.model_dump())
    delete_finished()
    print(read_database_new())






# def change_to_pending_new():
#     with Session(engine) as session:
#
#
#         sent_statement = select(Statuses).where(Statuses.status == 'sent')
#         sent_id = session.exec(sent_statement).first().id
#
#         pending_statement = select(Statuses).where(Statuses.status == 'pending')
#         pending_id = session.exec(pending_statement).first().id
#
#         statement_change = update(DatabaseCV).where(DatabaseCV.status == sent_id).values(status=pending_id)
#         session.exec(statement_change)
#
#         session.commit()
#
#
# def change_to_waiting_new():
#     with Session(engine) as session:
#         waiting_statement = select(Statuses).where(Statuses.status=='waiting')
#         waiting_id = session.exec(waiting_statement).first().id
#
#         pending_statement = select(Statuses).where(Statuses.status == 'pending')
#         pending_id = session.exec(pending_statement).first().id
#
#         statement_change = update(DatabaseCV).where(DatabaseCV.status == pending_id).values(status=waiting_id)
#         session.exec(statement_change)
#
#         session.commit()
#
#
# def change_to_finished_new():
#     with Session(engine) as session:
#         waiting_statement = select(Statuses).where(Statuses.status=='waiting')
#         waiting_id = session.exec(waiting_statement).first().id
#
#         pending_statement = select(Statuses).where(Statuses.status == 'pending')
#         pending_id = session.exec(pending_statement).first().id
#
#         statement_change = update(DatabaseCV).where(DatabaseCV.status == pending_id).values(status=waiting_id)
#         session.exec(statement_change)
#
#         session.commit()
