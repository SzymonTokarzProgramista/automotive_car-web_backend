from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class EmailVerificationResponse(BaseModel):
    email_verified: bool
    message: str


class TokenPayload(BaseModel):
    sub: str
    exp: int


class UserRead(BaseModel):
    id: int
    email: EmailStr
    email_verified: bool
