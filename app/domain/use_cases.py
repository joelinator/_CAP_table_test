# app/domain/use_cases.py
from .entities import User, Shareholder, ShareIssuance, AuditEvent, Role
from typing import List, Optional
from .cache import *
#import hashlib  # For simple hashing, replace with bcrypt in production
import bcrypt

class AuthenticateUser:
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def execute(self, username: str, password: str) -> Optional[User]:
        user = self.user_repo.get_by_username(username)
        if user and bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            return user
        return None

class ListShareholders:
    def __init__(self, shareholder_repo, issuance_repo):
        self.shareholder_repo = shareholder_repo
        self.issuance_repo = issuance_repo

    def execute(self) -> List[dict]:
        cache_key = "shareholders_list"
        cached = get_cache(cache_key)
        if cached:
            return cached

        shareholders = self.shareholder_repo.get_all()
        result = [
            {
                "id": sh.id,
                "name": sh.name,
                "email": sh.email,
                "total_shares": sum(iss.number_of_shares for iss in self.issuance_repo.get_by_shareholder(sh.id))
            }
            for sh in shareholders
        ]
        set_cache(cache_key, result)
        return result

class CreateShareholder:
    def __init__(self, user_repo, shareholder_repo, audit_repo):
        self.user_repo = user_repo
        self.shareholder_repo = shareholder_repo
        self.audit_repo = audit_repo

    def execute(self, name: str, email: str, username: str, password: str, current_user: User) -> Shareholder:
        if current_user.role != Role.ADMIN:
            raise PermissionError("Only admin can create shareholders")
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()) 
        user = User(username=username, password_hash=hashed.decode(), role=Role.SHAREHOLDER)
        user = self.user_repo.create(user)
        shareholder = Shareholder(user_id=user.id, name=name, email=email)
        shareholder = self.shareholder_repo.create(shareholder)
        self.audit_repo.create(AuditEvent(action="create_shareholder", user_id=current_user.id, details=f"Created shareholder {shareholder.id}"))
        return shareholder

class ListIssuances:
    def __init__(self, issuance_repo, shareholder_repo):
        self.issuance_repo = issuance_repo
        self.shareholder_repo = shareholder_repo

    def execute(self, current_user: User) -> List[ShareIssuance]:
        cache_key = "issuances_list"
        cached = get_cache(cache_key)
        if cached:
            return cached
        if current_user.role == Role.ADMIN:
            result =  self.issuance_repo.get_all()
        else:
            shareholder = self.shareholder_repo.get_by_user_id(current_user.id)
            if not shareholder:
                raise ValueError("No shareholder profile")
            result =  self.issuance_repo.get_by_shareholder(shareholder.id)
        set_cache(cache_key, result)
        return result

class CreateIssuance:
    def __init__(self, issuance_repo, shareholder_repo, audit_repo):
        self.issuance_repo = issuance_repo
        self.shareholder_repo = shareholder_repo
        self.audit_repo = audit_repo

    def execute(self, shareholder_id: int, number_of_shares: int, price: float, current_user: User) -> ShareIssuance:
        if current_user.role != Role.ADMIN:
            raise PermissionError("Only admin can issue shares")
        if number_of_shares <= 0:
            raise ValueError("Number of shares must be positive")
        shareholder = self.shareholder_repo.get_by_id(shareholder_id)
        if not shareholder:
            raise ValueError("Shareholder not found")
        issuance = ShareIssuance(shareholder_id=shareholder_id, number_of_shares=number_of_shares, price=price)
        issuance = self.issuance_repo.create(issuance)
        self.audit_repo.create(AuditEvent(action="issue_shares", user_id=current_user.id, details=f"Issued {number_of_shares} shares to {shareholder_id}"))
        # Simulate email
        print(f"Simulating email to {shareholder.email}: Shares issued!")
        return issuance

class GenerateCertificate:
    def __init__(self, issuance_repo, shareholder_repo):
        self.issuance_repo = issuance_repo
        self.shareholder_repo = shareholder_repo

    def execute(self, issuance_id: int, current_user: User) -> bytes:
        issuance = self.issuance_repo.get_by_id(issuance_id)
        if not issuance:
            raise ValueError("Issuance not found")
        shareholder = self.shareholder_repo.get_by_id(issuance.shareholder_id)
        if current_user.role != Role.ADMIN:
            user_shareholder = self.shareholder_repo.get_by_user_id(current_user.id)
            if user_shareholder.id != shareholder.id:
                raise PermissionError("Cannot access this certificate")
        # Generate PDF, will call infrastructure
        from ..infrastructure.pdf_generator import generate_pdf_certificate
        return generate_pdf_certificate(shareholder, issuance)
