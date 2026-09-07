"""
User Schemas
用户API数据验证模型
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    email: Optional[str] = None


class UserCreate(UserBase):
    """创建用户请求模型"""
    password: str


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    role: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserInDB(UserBase):
    """数据库用户模型"""
    id: int
    password_hash: str
    role: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
