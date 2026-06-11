from pydantic import BaseModel,EmailStr, AfterValidator, AnyUrl
from typing import Annotated, TypeAlias,List
from sqlmodel import SQLModel, Field,Relationship


def check_specific_hosts(url: AnyUrl) -> AnyUrl | None:
    valid_hosts = {"www.github.com", "github.com","https://github.com"}
    if url.host in valid_hosts:
        return url
    return None

AcceptedUrl: TypeAlias = Annotated[AnyUrl, AfterValidator(check_specific_hosts)]


class Statuses(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    status: str


    cvs: List["DatabaseCV"] = Relationship(back_populates="statuses")


class BaseCV(SQLModel):
    email: str
    cv_name: str
    cv: str
    position_name: str | None = None
    github_link: str | None = None


class DatabaseCV(BaseCV, table=True):
    id: int | None = Field(default=None,primary_key=True)
    status: int| None = Field(default=None,foreign_key="statuses.id")

    statuses: Statuses = Relationship(back_populates="cvs")


class FormsCV(BaseCV):
    email: EmailStr
    github_link: AcceptedUrl | None = None
