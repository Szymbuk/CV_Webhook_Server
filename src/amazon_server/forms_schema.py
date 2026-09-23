from pydantic import BaseModel, EmailStr, AnyUrl, field_validator, TypeAdapter
from typing import List
from shared.base_schemas import BaseCV


def check_specific_hosts(value: str) -> str:
    url = TypeAdapter(AnyUrl).validate_python(value)
    valid_hosts = {"www.github.com", "github.com","https://github.com"}
    if url.host not in valid_hosts:
        raise ValueError("GitHub URL must point to github.com")
    return value

class FormsCV(BaseCV):
    model_config = {"str_strip_whitespace": True}

    email: EmailStr
    github_link: str | None = None

    @field_validator('github_link', mode='before')
    @classmethod
    def validate_github_link(cls, value: object) -> str | None:
        # Jeśli przyjdzie pusty tekst (lub same spacje), zamieniamy na True None
        if isinstance(value, str) and value.strip() == "":
            return None
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("GitHub URL must be a string")
        return check_specific_hosts(value)


class StatusChangeList(BaseModel):
    cv_ids: List[int]|None
