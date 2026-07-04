"""FastAPI-зависимости (Depends), переиспользуемые в разных роутерах."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.services.auth import decode_access_token
from app.services.user import get_user_by_email

# OAuth2PasswordBearer делает две вещи:
# 1) В Swagger UI появляется кнопка «Authorize» — можно вставить токен
# 2) При вызове эндпоинта автоматически извлекает токен из заголовка
#    Authorization: Bearer <token>
# tokenUrl — адрес, куда Swagger отправит логин/пароль для получения токена.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Зависимость, которая превращает JWT-токен в объект User.

    Как это работает в цепочке:
    1. Клиент шлёт заголовок Authorization: Bearer <token>
    2. OAuth2PasswordBearer извлекает <token>
    3. Эта функция декодирует токен → достаёт email → находит пользователя в БД
    4. Роутер получает готовый объект User

    Если на любом шаге что-то не так → 401 Unauthorized.

    Использование в роутере:
        @router.post("/links")
        async def create(user: User = Depends(get_current_user)):
            ...
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="невалидный или просроченный токен",
        # WWW-Authenticate — стандартный заголовок, который сообщает клиенту
        # какой тип аутентификации использовать (Bearer = JWT-токен).
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception from None

    user = await get_user_by_email(db, email)
    if user is None:
        raise credentials_exception

    return user
