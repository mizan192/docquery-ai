from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    # what user sends to register
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    # what user sends to login
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    # what API returns after register
    id: int
    email: str
    username: str

    # allows pydantic to read from SQLAlchemy model
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    # what API returns after login
    access_token: str
    token_type: str = "bearer"
    