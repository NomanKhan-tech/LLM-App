from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth import RegisterRequest, LoginRequest


def register_user(
    db: Session,
    user_data: RegisterRequest,
) -> User:

    existing_user = db.query(User).filter(User.email == user_data.email).first()

    if existing_user:
        raise ValueError("Email already registered")

    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def login_user(
    db: Session,
    login_data: LoginRequest,
) -> str:
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user:
        raise ValueError("Invalid email or password")

    if not verify_password(
        login_data.password,
        user.password_hash,
    ):
        raise ValueError("Invalid email or password")

    access_token = create_access_token(user.id)

    return access_token
