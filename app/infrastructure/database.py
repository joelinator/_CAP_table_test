# app/infrastructure/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from ..adapters.repositories.base import UserModel, ShareholderModel
from ..domain.entities import Role
import bcrypt
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
        DATABASE_URL, 
        pool_size=20,
        max_overflow=5,
        pool_timeout=30,
        pool_recycle=1800
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from ..adapters.repositories.base import Base
Base.metadata.create_all(bind=engine)  # Create tables

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Seed data
def seed_data():
    if os.getenv("SEED_DATA") != "true":
        return
    db = SessionLocal()
    # Check if users exist
    if db.query(UserModel).filter(UserModel.username == "admin").first() is None:
        admin_hash = bcrypt.hashpw("adminpass".encode(), bcrypt.gensalt()).decode()
        admin = UserModel(username="admin", password_hash=admin_hash, role=Role.ADMIN)
        db.add(admin)
        db.commit()
        db.refresh(admin)
    
    if db.query(UserModel).filter(UserModel.username == "shareholder1").first() is None:
        sh_hash = bcrypt.hashpw("shpass".encode(), bcrypt.gensalt()).decode()
        sh_user = UserModel(username="shareholder1", password_hash=sh_hash, role=Role.SHAREHOLDER)
        db.add(sh_user)
        db.commit()
        db.refresh(sh_user)
        shareholder = ShareholderModel(user_id=sh_user.id, name="John Doe", email="john@example.com")
        db.add(shareholder)
        db.commit()

seed_data()
