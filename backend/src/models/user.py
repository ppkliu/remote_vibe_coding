from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid
import bcrypt
import logging
from .base import Base

logger = logging.getLogger(__name__)

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    sessions: Mapped[list["Session"]] = relationship("Session", back_populates="user", cascade="all, delete-orphan")

    def verify_password(self, password: str) -> bool:
        """
        Verify password against hashed password using bcrypt.

        Args:
            password: Plain text password to verify

        Returns:
            True if password matches, False otherwise
        """
        try:
            # Truncate password to 72 bytes if needed (bcrypt limit)
            password_bytes = password.encode('utf-8')
            if len(password_bytes) > 72:
                logger.warning(f"Password truncated to 72 bytes for verification")
                password_bytes = password_bytes[:72]

            return bcrypt.checkpw(password_bytes, self.hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"❌ Password verification failed: {e}")
            return False

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt with 12 rounds.

        bcrypt has a 72-byte limit for passwords. Passwords longer than this
        will be truncated with a warning.

        Args:
            password: Plain text password to hash

        Returns:
            Bcrypt hashed password string
        """
        try:
            # Truncate password to 72 bytes if needed (bcrypt limit)
            password_bytes = password.encode('utf-8')
            if len(password_bytes) > 72:
                logger.warning(f"Password exceeds 72 bytes, truncating for hashing")
                password_bytes = password_bytes[:72]

            # Generate salt with 12 rounds (default)
            salt = bcrypt.gensalt(rounds=12)
            # Hash password with salt
            hashed = bcrypt.hashpw(password_bytes, salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"❌ Password hashing failed: {e}")
            raise
