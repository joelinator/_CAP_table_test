# app/adapters/controllers/api.py
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
from ...domain.use_cases import AuthenticateUser, ListShareholders, CreateShareholder, ListIssuances, CreateIssuance, GenerateCertificate
from ...adapters.repositories.user_repository import UserRepository
from ...adapters.repositories.shareholder_repository import ShareholderRepository
from ...adapters.repositories.issuance_repository import IssuanceRepository
from ...adapters.repositories.audit_repository import AuditRepository
from ...infrastructure.database import get_db_session
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta
from ...domain.entities import User, Role

app = FastAPI()

SECRET_KEY = "your_secret_key"  # Change in production
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

class Login(BaseModel):
    username: str
    password: str

class ShareholderCreate(BaseModel):
    name: str
    email: str
    username: str
    password: str

class IssuanceCreate(BaseModel):
    shareholder_id: int
    number_of_shares: int
    price: float

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db_session)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_repo = UserRepository(db)
    user = user_repo.get_by_username(username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/api/token/", response_model=Token)
def login(login: Login, db: Session = Depends(get_db_session)):
    user_repo = UserRepository(db)
    auth_use_case = AuthenticateUser(user_repo)
    user = auth_use_case.execute(login.username, login.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Log audit
    audit_repo = AuditRepository(db)
    audit_repo.create(AuditEvent(action="login", user_id=user.id))
    access_token_expires = timedelta(minutes=30)
    access_token = jwt.encode(
        {"sub": user.username, "exp": datetime.utcnow() + access_token_expires},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/shareholders/")
def list_shareholders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db_session)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")
    sh_repo = ShareholderRepository(db)
    iss_repo = IssuanceRepository(db)
    use_case = ListShareholders(sh_repo, iss_repo)
    return use_case.execute()

@app.post("/api/shareholders/")
def create_shareholder(data: ShareholderCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db_session)):
    user_repo = UserRepository(db)
    sh_repo = ShareholderRepository(db)
    audit_repo = AuditRepository(db)
    use_case = CreateShareholder(user_repo, sh_repo, audit_repo)
    return use_case.execute(data.name, data.email, data.username, data.password, current_user)

@app.get("/api/issuances/")
def list_issuances(current_user: User = Depends(get_current_user), db: Session = Depends(get_db_session)):
    iss_repo = IssuanceRepository(db)
    sh_repo = ShareholderRepository(db)
    use_case = ListIssuances(iss_repo, sh_repo)
    return use_case.execute(current_user)

@app.post("/api/issuances/")
def create_issuance(data: IssuanceCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db_session)):
    iss_repo = IssuanceRepository(db)
    sh_repo = ShareholderRepository(db)
    audit_repo = AuditRepository(db)
    use_case = CreateIssuance(iss_repo, sh_repo, audit_repo)
    return use_case.execute(data.shareholder_id, data.number_of_shares, data.price, current_user)

@app.get("/api/issuances/{issuance_id}/certificate/", response_class=Response)
def get_certificate(issuance_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db_session)):
    iss_repo = IssuanceRepository(db)
    sh_repo = ShareholderRepository(db)
    use_case = GenerateCertificate(iss_repo, sh_repo)
    pdf_bytes = use_case.execute(issuance_id, current_user)
    return Response(content=pdf_bytes, media_type="application/pdf")

# Bonus: Audit log endpoint
@app.get("/api/audits/")
def list_audits(current_user: User = Depends(get_current_user), db: Session = Depends(get_db_session)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")
    audit_repo = AuditRepository(db)
    return audit_repo.get_all()
