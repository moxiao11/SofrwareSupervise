"""
User Service
用户服务API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserCreate

router = APIRouter(prefix="/api/users", tags=["用户服务"])


@router.get("/{user_id}", response_model=UserResponse, summary="获取用户信息")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    根据用户ID获取用户信息
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户 {user_id} 不存在"
        )
    return user


@router.get("/", response_model=List[UserResponse], summary="获取用户列表")
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取用户列表
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="创建用户")
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    创建新用户
    """
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"用户名 {user_data.username} 已存在"
        )

    # 创建用户（实际应用中应该对密码进行哈希处理）
    user = User(
        username=user_data.username,
        password_hash=f"hash_{user_data.password}",  # 简化处理
        email=user_data.email,
        role='user'
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
