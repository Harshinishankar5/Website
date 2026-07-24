from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from app.core.config import ADMIN_SECRET_KEY, SUPER_ADMIN_SECRET_KEY
from app.database import get_db
from app.models.users import User, UserRole
from app.schemas.auth import LoginRequest, SignupRequest, CreateUserRequest, UserResponse

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)

from app.core.dependencies import super_admin_required, admin_required, get_current_user
import os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter(prefix="/auth", tags=["Authentication"])


SECRET_KEY_ROLES = {
    ADMIN_SECRET_KEY: UserRole.ADMIN,
    SUPER_ADMIN_SECRET_KEY: UserRole.SUPER_ADMIN,
}

if not ADMIN_SECRET_KEY or not SUPER_ADMIN_SECRET_KEY:
    raise RuntimeError("ADMIN_SECRET_KEY and SUPER_ADMIN_SECRET_KEY must be set in .env")


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(
    payload: SignupRequest,
    x_secret_key: str = Header(..., alias="x-secret-key"),
    db: Session = Depends(get_db),
):
    role = SECRET_KEY_ROLES.get(x_secret_key)
    if role is None:
        raise HTTPException(status_code=401, detail="Invalid secret key")

    conflict = (
        db.query(User)
        .filter((User.email == payload.email) | (User.username == payload.username))
        .first()
    )
    if conflict:
        field = "Email" if conflict.email == payload.email else "Username"
        raise HTTPException(status_code=400, detail=f"{field} already exists")

    new_user = User(
        username=payload.username,
        email=payload.email,
        password=hash_password(payload.password),
        role=role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login")
async def login(payload: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    access_token = create_access_token({"user_id": user.id, "role": user.role})

    return {"access_token": access_token, "token_type": "bearer", "role": user.role}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/all", response_model=list[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    return db.query(User).all()

# @router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# def create_user(
#         payload: CreateUserRequest,
#         db: Session = Depends(get_db),
#         current_user: User = Depends(admin_required),
# ):
#     """Admin (or super admin) creates a regular USER account. That user then
#     gets access to the blog endpoints once they log in."""
#     conflict = (
#         db.query(User)
#         .filter(
#             (User.email == payload.email) | (User.username == payload.username)
#         )
#         .first()
#     )
#     if conflict:
#         field = "Email" if conflict.email == payload.email else "Username"
#         raise HTTPException(status_code=400, detail=f"{field} already exists")
#
#     user = User(
#         username=payload.username,
#         email=payload.email,
#         password=hash_password(payload.password),
#         role=UserRole.USER,
#     )
#     db.add(user)
#     db.commit()
#     db.refresh(user)
#
#     return user
#
#
# @router.get("/users", response_model=list[UserResponse])
# def get_users(
#         db: Session = Depends(get_db),
#         current_user: User = Depends(admin_required),
# ):
#     return db.query(User).filter(User.role == UserRole.USER).all()
#
#
# @router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_user(
#         user_id: int,
#         db: Session = Depends(get_db),
#         current_user: User = Depends(admin_required),
# ):
#     user = db.query(User).filter(
#         User.id == user_id,
#         User.role == UserRole.USER,
#     ).first()
#
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     db.delete(user)
#     db.commit()