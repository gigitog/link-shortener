"""HTTP-роуты для регистрации и авторизации."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserResponse
from app.services import user as user_service
from app.services.auth import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(body: UserCreate, db: AsyncSession = Depends(get_db)):
    """Регистрация нового пользователя."""
    try:
        user = await user_service.create_user(db, body.email, body.password)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from None

    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Логин — возвращает JWT-токен.

    Принимает OAuth2PasswordRequestForm — это стандартная форма OAuth2
    с полями username и password (не JSON!). Поле называется username,
    а не email — это требование спецификации OAuth2, Swagger UI
    отправляет данные именно в таком формате.
    """
    user = await user_service.authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # sub (subject) — стандартное поле JWT, идентифицирующее пользователя.
    token = create_access_token(data={"sub": user.email})
    return Token(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """Возвращает данные текущего пользователя. Полезно для проверки токена."""
    return user
