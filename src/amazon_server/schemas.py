from pydantic import BaseModel,EmailStr

class FormsCV(BaseModel):
    email: EmailStr
    cv_name: str
    cv_content: str