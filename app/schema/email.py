from pydantic import BaseModel

class Email(BaseModel):
    email: str
    category: str

    class Config:
        from_attribute = True