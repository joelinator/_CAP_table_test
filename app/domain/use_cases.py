# app/domain/use_cases.py
from .entities import User, Shareholder, ShareIssuance, AuditEvent, Role
from typing import List, Optional
from ..infrastructure.cache import set_cache, get_cache , delete_cache
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

        # Check for existing username
        if self.user_repo.get_by_username(username):
            raise ValueError(f"Username '{username}' is already taken")

        # Check for existing email
        if self.shareholder_repo.get_by_email(email):
            raise ValueError(f"Email '{email}' is already in use")


        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()) 
        user = User(username=username, password_hash=hashed.decode(), role=Role.SHAREHOLDER)
        user = self.user_repo.create(user)
        shareholder = Shareholder(user_id=user.id, name=name, email=email)
        shareholder = self.shareholder_repo.create(shareholder)
        self.audit_repo.create(AuditEvent(action="create_shareholder", user_id=current_user.id, details=f"Created shareholder {shareholder.id}"))

        #invalidate cache
        delete_cache("shareholders_list")
        return shareholder

class ListIssuances:
    def __init__(self, issuance_repo, shareholder_repo):
        self.issuance_repo = issuance_repo
        self.shareholder_repo = shareholder_repo

    def execute(self, current_user: User) -> List[dict]:
        # Use distinct cache keys for admin and shareholders
        cache_key = f"issuances_list_{'admin' if current_user.role == Role.ADMIN else current_user.id}"
        cached = get_cache(cache_key)
        if cached:
            return cached

        if current_user.role == Role.ADMIN:
            # Admin sees all issuances with shareholder details
            issuances = self.issuance_repo.get_all()
            result = []
            for issuance in issuances:
                shareholder = self.shareholder_repo.get_by_id(issuance.shareholder_id)
                result.append({
                    "issuance_id": issuance.id,
                    "date": issuance.date.isoformat(),
                    "price": issuance.price,
                    "number_of_shares": issuance.number_of_shares,
                    "shareholder_id": shareholder.id if shareholder else None,
                    "shareholder_name": shareholder.name if shareholder else "Unknown",
                    "shareholder_email": shareholder.email if shareholder else "Unknown"
                })
        else:
            # Shareholder sees only their own issuances
            shareholder = self.shareholder_repo.get_by_user_id(current_user.id)
            if not shareholder:
                raise ValueError("No shareholder profile")
            issuances = self.issuance_repo.get_by_shareholder(shareholder.id)
            result = [
                {
                    "issuance_id": iss.id,
                    "date": iss.date.isoformat(),
                    "price": iss.price,
                    "number_of_shares": iss.number_of_shares,
                    "shareholder_id": shareholder.id,
                    "shareholder_name": shareholder.name,
                    "shareholder_email": shareholder.email
                } for iss in issuances
            ]
        
        # Cache the result for 5 minutes
        set_cache(cache_key, result, ttl=300)
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

        #invalidate cache
        delete_cache("shareholders_list")  # Total shares changed
        delete_cache("issuances_list_admin")  # Admin issuances list
        delete_cache(f"issuances_list_{shareholder.user_id}")  # Specific shareholder's issuances list
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
