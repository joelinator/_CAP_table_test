# app/adapters/repositories/user_repository.py
from ...domain.entities import User
from .base import UserModel, Base
from sqlalchemy.orm import Session

from typing import Optional

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_username(self, username: str) -> Optional[User]:
        model = self.session.query(UserModel).filter(UserModel.username == username).first()
        if model:
            return User(id=model.id, username=model.username, password_hash=model.password_hash, role=model.role)
        return None

    def get_by_id(self, user_id: int) -> Optional[User]:
        model = self.session.query(UserModel).filter(UserModel.id == user_id).first()
        if model:
            return User(id=model.id, username=model.username, password_hash=model.password_hash, role=model.role)
        return None

    def create(self, user: User) -> User:
        model = UserModel(username=user.username, password_hash=user.password_hash, role=user.role)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        user.id = model.id
        return user
