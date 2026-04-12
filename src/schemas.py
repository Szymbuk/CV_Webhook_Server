from pydantic import BaseModel,EmailStr

class FormsCV(BaseModel):
    email: EmailStr
    cv_link: str
    video_link: str