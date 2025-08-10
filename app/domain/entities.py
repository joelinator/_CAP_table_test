# app/domain/entities.py
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class Role(Enum):
    ADMIN = "admin"
    SHAREHOLDER = "shareholder"

class User(BaseModel):
    id: Optional[int] = None
    username: str
    password_hash: str  # In real app, hash properly
    role: Role

class Shareholder(BaseModel):
    id: Optional[int] = None
    user_id: int
    name: str
    email: str

class ShareIssuance(BaseModel):
    id: Optional[int] = None
    shareholder_id: int
    number_of_shares: int
    price: float
    date: datetime = datetime.now(timezone.utc)

class AuditEvent(BaseModel):
    id: Optional[int] = None
    action: str
    timestamp: datetime = datetime.now(timezone.utc)
    user_id: int
    details: Optional[str] = None
