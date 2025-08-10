# app/adapters/controllers/api.py

from fastapi import FastAPI,Request, Depends, HTTPException, Header, Response
from fastapi.security import OAuth2PasswordBearer
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
from jose import JWTError, jwt, ExpiredSignatureError  # Use python-jose for better handling

from pydantic import BaseModel
from typing import Optional
from ...domain.use_cases import AuthenticateUser, ListShareholders, CreateShareholder, ListIssuances, CreateIssuance, GenerateCertificate

from ...domain.entities import AuditEvent
from ...adapters.repositories.user_repository import UserRepository
from ...adapters.repositories.shareholder_repository import ShareholderRepository
from ...adapters.repositories.issuance_repository import IssuanceRepository
from ...adapters.repositories.audit_repository import AuditRepository

from ...infrastructure.database import get_db_session

from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ...domain.entities import User, Role


app = FastAPI()

# CORS
origins_env = os.environ.get("ALLOWED_ORIGINS", "").split(",")
origins = [origin.strip() for origin in origins_env if origin.strip()]
if not origins:
    origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Adjust for frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


SECRET_KEY = os.getenv("JWT_SECRET", "8x9SAXTJOd0Rf/Ti6uovOf9UUV+4CvJVgjN4SPWDsGY=")  # Load from env
ALGORITHM = "HS256"
ISSUER = "captable-app"
AUDIENCE = "api-users"

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

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire, "iss": ISSUER, "aud": AUDIENCE})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db_session)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_aud": True}, audience=AUDIENCE, issuer=ISSUER)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing subject claim")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError as e:
        # Handle audience errors or other JWT issues
        error_msg = str(e).lower()
        if "audience" in error_msg:
            raise HTTPException(status_code=401, detail="Invalid audience in token")
        raise HTTPException(status_code=401, detail=f"Could not validate credentials: {str(e)}")
    user_repo = UserRepository(db)
    user = user_repo.get_by_username(username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@app.post("/api/token/", response_model=Token)
@limiter.limit("5/minutes") # 5 logins per minute per IP
def login(login: Login,request: Request, db: Session = Depends(get_db_session)):
    
    user_repo = UserRepository(db)
    auth_use_case = AuthenticateUser(user_repo)
    user = auth_use_case.execute(login.username, login.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Log audit
    audit_repo = AuditRepository(db)
    audit_repo.create(AuditEvent(action="login", user_id=user.id))
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/shareholders/")
@limiter.limit("10/minute")
def list_shareholders(request:Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db_session)):

    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")
    sh_repo = ShareholderRepository(db)
    iss_repo = IssuanceRepository(db)
    use_case = ListShareholders(sh_repo, iss_repo)
    return use_case.execute()


@app.post("/api/shareholders/")
@limiter.limit("10/minute")
def create_shareholder(request: Request, data: ShareholderCreate, current_user: User = Depends(get_current_user),  db: Session = Depends(get_db_session)):
    user_repo = UserRepository(db)
    sh_repo = ShareholderRepository(db)
    audit_repo = AuditRepository(db)
    use_case = CreateShareholder(user_repo, sh_repo, audit_repo)
    try:
        return use_case.execute(data.name, data.email, data.username, data.password, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))



@app.get("/api/issuances/")
@limiter.limit("10/minute")
def list_issuances(request: Request, current_user: User = Depends(get_current_user),   db: Session = Depends(get_db_session)):
    iss_repo = IssuanceRepository(db)
    sh_repo = ShareholderRepository(db)
    use_case = ListIssuances(iss_repo, sh_repo)
    return use_case.execute(current_user)


@app.post("/api/issuances/")
@limiter.limit("10/minute")
def create_issuance(request: Request, data: IssuanceCreate, current_user: User = Depends(get_current_user),  db: Session = Depends(get_db_session)):

    iss_repo = IssuanceRepository(db)
    sh_repo = ShareholderRepository(db)
    audit_repo = AuditRepository(db)
    use_case = CreateIssuance(iss_repo, sh_repo, audit_repo)
    return use_case.execute(data.shareholder_id, data.number_of_shares, data.price, current_user)


@app.get("/api/issuances/{issuance_id}/certificate/", response_class=Response)
@limiter.limit("10/minute")
def get_certificate(request: Request, issuance_id: int, current_user: User = Depends(get_current_user),  db: Session = Depends(get_db_session)):

    iss_repo = IssuanceRepository(db)
    sh_repo = ShareholderRepository(db)
    use_case = GenerateCertificate(iss_repo, sh_repo)
    pdf_bytes = use_case.execute(issuance_id, current_user)
    return Response(content=pdf_bytes, media_type="application/pdf")


# Bonus: Audit log endpoint
@app.get("/api/audits/")
@limiter.limit("10/minute")
def list_audits(request: Request, current_user: User = Depends(get_current_user),  db: Session = Depends(get_db_session)):

    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")
    audit_repo = AuditRepository(db)
    return audit_repo.get_all()
