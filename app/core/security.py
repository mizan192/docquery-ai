from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status 
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.config import settings
from app.models.user import User

# for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# looks for token in Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# convert plain password to hashed password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# check if plain password matched to hashed password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# create JWT access token
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


# Decode JWT token and return user object
async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
) -> User:
   
    # verify JWT token is valid
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # decode JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # get user from database
    async with db.begin():
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        # user = result.scalars().first() # return first mathced one if multiple user has same email

    if user is None:
        raise credentials_exception

    return user
