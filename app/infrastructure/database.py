# app/infrastructure/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
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
    db = SessionLocal()
    # Check if users exist
    if db.query(UserModel).filter(UserModel.username == "admin").first() is None:
        admin = UserModel(username="admin", password_hash=hashlib.sha256("adminpass".encode()).hexdigest(), role=Role.ADMIN)
        db.add(admin)
        db.commit()
        db.refresh(admin)
    
    if db.query(UserModel).filter(UserModel.username == "shareholder1").first() is None:
        sh_user = UserModel(username="shareholder1", password_hash=hashlib.sha256("shpass".encode()).hexdigest(), role=Role.SHAREHOLDER)
        db.add(sh_user)
        db.commit()
        db.refresh(sh_user)
        shareholder = ShareholderModel(user_id=sh_user.id, name="John Doe", email="john@example.com")
        db.add(shareholder)
        db.commit()

seed_data()
