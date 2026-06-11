from typing import List

from sqlmodel import Session, create_engine, SQLModel,select,col,update,delete
import os
from dotenv import load_dotenv
from shared.base_schemas import BaseCV
from shared.base_schemas import Statuses,DatabaseCV

load_dotenv()
DATABASE_NAME = os.getenv("DATABASE")
sqlite_url = f"sqlite:///{DATABASE_NAME}"
engine = create_engine(sqlite_url)


def create_tables():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        existing_status = session.exec(select(Statuses)).first()
        if not existing_status:
            s1 = Statuses(status='waiting')
            s3 = Statuses(status='pending')
            s4 = Statuses(status='finished')
            session.add_all([s1,s2,s3,s4])
            session.commit()
        return "Successfully created tables"


def add_forms(cv: BaseCV) -> DatabaseCV:
    with Session(engine) as session:
        waiting_statement = select(Statuses).where(Statuses.status=='waiting')
        waiting_id = session.exec(waiting_statement).first().id
        cv_data = cv.model_dump()

        if cv.github_link:
            cv_data["github_link"] = str(cv.github_link)

        db_cv = DatabaseCV.model_validate(cv_data)
        db_cv.status= waiting_id
        session.add(db_cv)
        session.commit()
        session.refresh(db_cv)
        return db_cv


def change_from_to(current_status: str, desired_status: str,cv_ids: List[int] | None = None):
    with Session(engine, expire_on_commit=False) as session:
        current_status_statement = select(Statuses).where(Statuses.status == current_status)
        current_status_id = session.exec(current_status_statement).first().id

        desired_status_statement = select(Statuses).where(Statuses.status == desired_status)
        desired_status_id = session.exec(desired_status_statement).first().id

        statement = select(DatabaseCV).join(Statuses).where(Statuses.id == current_status_id)
        if cv_ids:
            statement = statement.where(DatabaseCV.id.in_(cv_ids))

        data = session.exec(statement).all()

        response_data = []
        for cv in data:
            cv_dict = cv.model_dump()
            response_data.append(cv_dict)

        statement_changing = update(DatabaseCV).where(DatabaseCV.status == current_status_id).values(status = desired_status_id)
        if cv_ids:
            statement_changing = statement_changing.where(DatabaseCV.id.in_(cv_ids))

        session.exec(statement_changing)
        session.commit()
        return response_data


def delete_finished():
    with Session(engine) as session:
        finished_status_statement = select(Statuses).where(Statuses.status == "finished")
        finished_status_id = session.exec(finished_status_statement).first().id


        statement_changing = delete(DatabaseCV).where(DatabaseCV.status == finished_status_id)
        session.exec(statement_changing)
        session.commit()


def read_database():
    with Session(engine) as session:
        statement = select(DatabaseCV,Statuses).join(Statuses)
        data = session.exec(statement).all()
        formatted_data = [{"cv": cv, "status": status} for cv, status in data]

        return formatted_data