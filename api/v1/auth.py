from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.auth_service import AuthService
from schemes.user import UserCreate, UserLogin, UserResponse

auth_router = APIRouter(prefix="/auth", tags=["auth"])
auth_service = AuthService()

@auth_router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    existing_user = await auth_service.get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    new_user = await auth_service.create_user(user_data)
    return new_user

@auth_router.post("/login")
async def login(user_data: UserLogin):
    user = await auth_service.authenticate_user(user_data.username, user_data.password)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    token = auth_service.create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}
