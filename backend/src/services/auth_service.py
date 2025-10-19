import logging
from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.user import User
from ..schemas.auth import TokenResponse
from ..config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    def create_access_token(user_id: str) -> str:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"sub": str(user_id), "exp": expire, "type": "access"}
        return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode = {"sub": str(user_id), "exp": expire, "type": "refresh"}
        return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def create_tokens(user_id: str) -> TokenResponse:
        access_token = AuthService.create_access_token(user_id)
        refresh_token = AuthService.create_refresh_token(user_id)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> str | None:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            user_id: str = payload.get("sub")
            token_t: str = payload.get("type")
            if user_id is None or token_t != token_type:
                return None
            return user_id
        except JWTError:
            return None

    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
        result = await db.execute(select(User).filter(User.username == username, User.is_active == True))
        user = result.scalar_one_or_none()
        if not user:
            # T124: Security logging for failed auth attempts
            logger.warning(f"Failed login attempt: user not found - username={username}")
            return None
        if not user.verify_password(password):
            # T124: Security logging for failed auth attempts
            logger.warning(f"Failed login attempt: invalid password - username={username}, user_id={user.id}")
            return None
        user.last_login = datetime.utcnow()
        await db.commit()
        logger.info(f"Successful login - username={username}, user_id={user.id}")
        return user

    @staticmethod
    async def register_user(db: AsyncSession, username: str, email: str, password: str) -> User:
        user = User(
            username=username,
            email=email,
            hashed_password=User.hash_password(password)
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
