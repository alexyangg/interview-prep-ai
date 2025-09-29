# ensure 'backend/' is on sys.path when running pytest from repo root
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Adjust imports to your project structure:
# - Base should be your SQLAlchemy Base (models metadata)
# - get_db is your FastAPI dependency to be overridden
# - app is your FastAPI instance
from app.db import models  # Import models to register table definitions  
from app.db.base import Base   # you mentioned base.py exists
from app.db.session import get_db
from app.main import app

@pytest.fixture(scope="session")
def db_file():
    # temp sqlite file for the whole test session
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        yield path
    finally:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass

@pytest.fixture(scope="session")
def engine(db_file):
    engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()

@pytest.fixture(scope="session")
def TestingSessionLocal(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True, scope="function")
def _clean_tables(engine):
    """Clean all tables before each test to ensure isolation"""
    # Clear all data from tables before each test
    with engine.connect() as conn:
        # Delete in reverse dependency order (interviews first, then users)
        conn.execute(Base.metadata.tables['interviews'].delete())
        conn.execute(Base.metadata.tables['users'].delete())
        conn.commit()
    
    yield  # Run the test
    
    # Clean after test too (though before should be sufficient)
    with engine.connect() as conn:
        conn.execute(Base.metadata.tables['interviews'].delete())
        conn.execute(Base.metadata.tables['users'].delete())
        conn.commit()

@pytest.fixture(scope="function")
def client(TestingSessionLocal):
    # dependency override for get_db
    def _override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
