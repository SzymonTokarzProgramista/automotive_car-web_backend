from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db
from app.email_verification import (
    create_verification_token,
    hash_verification_token,
    send_verification_email,
    verification_expiration,
)
from app.models import User
from app.rate_limit import rate_limit_auth
from app.schemas import EmailVerificationResponse, TokenResponse, UserLogin, UserRead, UserRegister
from app.security import create_access_token, get_current_user, hash_password, verify_password
from app.services import (
    create_user,
    get_user_by_email,
    get_user_by_verification_token_hash,
    is_verification_token_expired,
    verify_user_email,
)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit_auth)],
)
def register_user(
    user_data: UserRegister,
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> UserRead:
    if get_user_by_email(db, user_data.email) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    verification_token = create_verification_token()
    user = create_user(
        db,
        user_data,
        hash_password(user_data.password),
        email_verified=not settings.email_verification_required,
        verification_token_hash=None
        if not settings.email_verification_required
        else hash_verification_token(verification_token),
        verification_expires_at=None if not settings.email_verification_required else verification_expiration(settings),
    )
    if settings.email_verification_required:
        send_verification_email(settings, user.email, verification_token)
    return UserRead(id=user.id, email=user.email, email_verified=user.email_verified)


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(rate_limit_auth)])
def login_user(
    login_data: UserLogin,
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> TokenResponse:
    user = get_user_by_email(db, login_data.email)
    if user is None or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if settings.email_verification_required and not user.email_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email address is not verified")

    return TokenResponse(
        access_token=create_access_token(settings, user.id),
        expires_in=settings.jwt_expires_minutes * 60,
    )


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead(id=current_user.id, email=current_user.email, email_verified=current_user.email_verified)


@router.get("/verify-email", response_model=EmailVerificationResponse)
def verify_email(token: str, db: Session = Depends(get_db)) -> EmailVerificationResponse:
    user = get_user_by_verification_token_hash(db, hash_verification_token(token))
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token")
    if is_verification_token_expired(user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification token expired")

    verify_user_email(db, user)
    return EmailVerificationResponse(email_verified=True, message="Email address verified")
