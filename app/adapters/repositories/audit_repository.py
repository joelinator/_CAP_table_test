# app/adapters/repositories/audit_repository.py
from ...domain.entities import AuditEvent
from .base import AuditEventModel
from sqlalchemy.orm import Session

class AuditRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, event: AuditEvent) -> AuditEvent:
        model = AuditEventModel(action=event.action, timestamp=event.timestamp, user_id=event.user_id, details=event.details)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        event.id = model.id
        return event

    def get_all(self) -> List[AuditEvent]:
        models = self.session.query(AuditEventModel).all()
        return [AuditEvent(id=m.id, action=m.action, timestamp=m.timestamp, user_id=m.user_id, details=m.details) for m in models]
