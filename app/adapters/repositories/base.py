# app/adapters/repositories/base.py (helper, but for simplicity, define in each repo)
# Using SQLAlchemy models

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
#from ...infrastructure.database import get_db_session  # Will define later
from ...domain.entities import Role

Base = declarative_base()

class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(SQLEnum(Role))

class ShareholderModel(Base):
    __tablename__ = "shareholders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    email = Column(String, unique=True)

class ShareIssuanceModel(Base):
    __tablename__ = "share_issuances"
    id = Column(Integer, primary_key=True, index=True)
    shareholder_id = Column(Integer, ForeignKey("shareholders.id"))
    number_of_shares = Column(Integer)
    price = Column(Float)
    date = Column(DateTime)

class AuditEventModel(Base):
    __tablename__ = "audit_events"
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String)
    timestamp = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))
    details = Column(String, nullable=True)
