import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.auth import LoginRequest, RefreshTokenRequest, RegisterRequest, TokenResponse
from backend.services import auth_service

logger = logging.getLogger("runbanditsrun.routers.auth")

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    logger.info(f"Registration attempt for email: {body.email}")
    try:
        user = auth_service.register_user(db, body.username, body.email, body.password)
        logger.info(f"User registered successfully: {user.id}")
    except ValueError as e:
        logger.warning(f"Registration failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    return TokenResponse(
        access_token=auth_service.create_access_token(user.id),
        refresh_token=auth_service.create_refresh_token(user.id),
    )


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    logger.info(f"Login attempt for email: {body.email}")
    user = auth_service.get_user_by_email(db, body.email)
    if not user or not auth_service.verify_password(body.password, user.password_hash):
        logger.warning(f"Failed login attempt for email: {body.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    logger.info(f"User logged in successfully: {user.id}")
    return TokenResponse(
        access_token=auth_service.create_access_token(user.id),
        refresh_token=auth_service.create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(body: RefreshTokenRequest):
    logger.debug("Token refresh requested")
    try:
        payload = auth_service.decode_refresh_token(body.refresh_token)
    except Exception as e:
        logger.warning(f"Token refresh failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user_id = int(payload["sub"])
    logger.info(f"Token refreshed for user: {user_id}")
    return TokenResponse(
        access_token=auth_service.create_access_token(user_id),
        refresh_token=auth_service.create_refresh_token(user_id),
    )
