from pydantic import BaseModel, EmailStr, Field, field_validator


PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128


def normalize_email(value: EmailStr) -> str:
    return str(value).strip().lower()


def validate_password(value: str) -> str:
    stripped_value = value.strip()
    if stripped_value != value:
        raise ValueError("Password cannot start or end with whitespace")
    if any(character in value for character in ("\x00", "\r", "\n", "\t")):
        raise ValueError("Password contains unsupported control characters")
    return value


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)

    @field_validator("email")
    @classmethod
    def normalize_register_email(cls, value: EmailStr) -> str:
        return normalize_email(value)

    @field_validator("password")
    @classmethod
    def validate_register_password(cls, value: str) -> str:
        return validate_password(value)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)

    @field_validator("email")
    @classmethod
    def normalize_login_email(cls, value: EmailStr) -> str:
        return normalize_email(value)

    @field_validator("password")
    @classmethod
    def validate_login_password(cls, value: str) -> str:
        return validate_password(value)


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
