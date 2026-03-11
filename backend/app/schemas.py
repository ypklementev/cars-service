from pydantic import BaseModel


class CarOut(BaseModel):
    brand: str
    model: str
    year: int
    price: int
    color: str
    url: str

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: str
    password: str