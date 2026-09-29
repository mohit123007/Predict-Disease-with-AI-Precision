from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import timedelta

from backend.services.user_service import create_user, authenticate_user, init_db
from backend.utils.security import create_access_token

router = APIRouter()


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


# Initialize DB on import (idempotent)
init_db()


@router.post("/register")
async def register(payload: RegisterRequest):
    try:
        user = create_user(payload.username, payload.password)
        return {"user": user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(payload: LoginRequest):
    user = authenticate_user(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token_expires = timedelta(minutes=60)
    token = create_access_token(data={"sub": user["username"], "user_id": user["id"]}, expires_delta=access_token_expires)
    return {"access_token": token, "token_type": "bearer"}
