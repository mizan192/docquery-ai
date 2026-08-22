from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.schemas.user import TokenResponse, UserResponse, UserRegister, UserLogin
from app.core.security import create_access_token, hash_password, verify_password
from app.core.logging import logger
from app.core.exceptions import AuthError

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


# Register new user
@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegister,   
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise AuthError("Email already registered")
    
    # check if username already exists 
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    existing_username = result.scalar_one_or_none()
    if existing_username:
        raise AuthError("Username already exists")

    # create new user with hashed password
    hashed_password = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )
    # save new user to DB
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    logger.info(f"User registered successfully: {new_user.email}")
    return new_user 


@router.post("/login", response_model=TokenResponse)
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    # get user from database
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    user = result.scalar_one_or_none()

    # if no user found
    if not user or not verify_password(user_data.password, user.hashed_password):
        logger.warning(f"Invalid credentials for user: {user_data.email}")
        raise AuthError("Invalid credentials")
    
    # generate JWT token
    access_token = create_access_token(data={"sub": user.email})

    logger.info(f"User logged in successfully: {user.email}")
    return TokenResponse(access_token=access_token)
