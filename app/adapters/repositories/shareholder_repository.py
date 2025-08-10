# app/adapters/repositories/shareholder_repository.py
from ...domain.entities import Shareholder
from .base import ShareholderModel
from sqlalchemy.orm import Session

from typing import List, Optional

class ShareholderRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Shareholder]:
        models = self.session.query(ShareholderModel).all()
        return [Shareholder(id=m.id, user_id=m.user_id, name=m.name, email=m.email) for m in models]

    def get_by_id(self, sh_id: int) -> Optional[Shareholder]:
        model = self.session.query(ShareholderModel).filter(ShareholderModel.id == sh_id).first()
        if model:
            return Shareholder(id=model.id, user_id=model.user_id, name=model.name, email=model.email)
        return None

    def get_by_user_id(self, user_id: int) -> Optional[Shareholder]:
        model = self.session.query(ShareholderModel).filter(ShareholderModel.user_id == user_id).first()
        if model:
            return Shareholder(id=model.id, user_id=model.user_id, name=model.name, email=model.email)
        return None

    def get_by_email(self, email: str) -> Optional[Shareholder]:
        model = self.session.query(ShareholderModel).filter(ShareholderModel.email == email).first()
        if model:
            return Shareholder(id=model.id, user_id=m.user_id, name=m.name, email=m.email)
        return None

    def create(self, shareholder: Shareholder) -> Shareholder:
        model = ShareholderModel(user_id=shareholder.user_id, name=shareholder.name, email=shareholder.email)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        shareholder.id = model.id
        return shareholder
