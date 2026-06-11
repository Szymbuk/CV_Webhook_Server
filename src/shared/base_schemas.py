from sqlmodel import SQLModel, Field,Relationship
from typing import List

class BaseCV(SQLModel):
    cv_name: str
    cv: str
    position_name: str | None = None
    email: str
    github_link: str | None = None


class Statuses(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    status: str


    cvs: List["DatabaseCV"] = Relationship(back_populates="statuses")


class DatabaseCV(BaseCV, table=True):
    id: int | None = Field(default=None, primary_key=True)
    status: int | None = Field(default=None, foreign_key="statuses.id")

    statuses: Statuses = Relationship(back_populates="cvs")