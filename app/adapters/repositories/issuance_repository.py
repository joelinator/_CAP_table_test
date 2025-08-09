# app/adapters/repositories/issuance_repository.py
from ...domain.entities import ShareIssuance
from .base import ShareIssuanceModel
from sqlalchemy.orm import Session
from datetime import datetime

class IssuanceRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[ShareIssuance]:
        models = self.session.query(ShareIssuanceModel).all()
        return [ShareIssuance(id=m.id, shareholder_id=m.shareholder_id, number_of_shares=m.number_of_shares, price=m.price, date=m.date) for m in models]

    def get_by_id(self, iss_id: int) -> Optional[ShareIssuance]:
        model = self.session.query(ShareIssuanceModel).filter(ShareIssuanceModel.id == iss_id).first()
        if model:
            return ShareIssuance(id=model.id, shareholder_id=model.shareholder_id, number_of_shares=m.number_of_shares, price=m.price, date=m.date)
        return None

    def get_by_shareholder(self, sh_id: int) -> List[ShareIssuance]:
        models = self.session.query(ShareIssuanceModel).filter(ShareIssuanceModel.shareholder_id == sh_id).all()
        return [ShareIssuance(id=m.id, shareholder_id=m.shareholder_id, number_of_shares=m.number_of_shares, price=m.price, date=m.date) for m in models]

    def create(self, issuance: ShareIssuance) -> ShareIssuance:
        model = ShareIssuanceModel(shareholder_id=issuance.shareholder_id, number_of_shares=issuance.number_of_shares, price=issuance.price, date=issuance.date or datetime.utcnow())
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        issuance.id = model.id
        return issuance
