import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL, echo=False, future=True, connect_args=connect_args
)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()