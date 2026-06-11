from pydantic import BaseModel,EmailStr, AfterValidator, AnyUrl
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


class StatusChangeList(BaseModel):
    cv_ids: List[int]|None
