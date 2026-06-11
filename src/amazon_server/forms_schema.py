from pydantic import BaseModel, EmailStr, AfterValidator, AnyUrl, field_validator
from typing import Annotated, TypeAlias,List
from shared.base_schemas import BaseCV


def check_specific_hosts(url: AnyUrl) -> AnyUrl | None:
    valid_hosts = {"www.github.com", "github.com","https://github.com"}
    if url.host in valid_hosts:
        return url
    return None

AcceptedUrl: TypeAlias = Annotated[AnyUrl, AfterValidator(check_specific_hosts)]


class FormsCV(BaseCV):
    email: EmailStr
    github_link: AcceptedUrl | None = None

    @field_validator('github_link', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        # Jeśli przyjdzie pusty tekst (lub same spacje), zamieniamy na True None
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


class StatusChangeList(BaseModel):
    cv_ids: List[int]|None
