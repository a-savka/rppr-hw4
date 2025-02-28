from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

from db.models.user_model import User
from db.db_conf import PG_URL
from schemes.user import UserCreate

SECRET_KEY = "itsmykey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:

    def __init__(self, db_url=PG_URL):
        self.engine = create_async_engine(db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        async with self.Session() as session:
            result = await session.execute(select(User).where(User.username == username))
            return result.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate) -> User:
        async with self.Session() as session:
            hashed_password = pwd_context.hash(user_data.password)
            user = User(username=user_data.username, hashed_password=hashed_password)
            session.add(user)
            await session.commit()
            return user

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = await self.get_user_by_username(username)
        if not user or not pwd_context.verify(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, user_id: int) -> str:
        expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": str(user_id), "exp": expires_at}
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    async def verify_token(self, token: str) -> Optional[User]:
        """Decode the JWT token and return the user."""
        async with self.Session() as session:

            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_id = int(payload.get("sub"))
                result = await session.execute(select(User).where(User.id == user_id))
                return result.scalar_one_or_none()
            except jwt.ExpiredSignatureError:
                raise HTTPException(status_code=401, detail="Token expired")
            except jwt.InvalidTokenError:
                raise HTTPException(status_code=401, detail="Invalid token")
