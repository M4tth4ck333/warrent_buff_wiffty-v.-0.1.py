from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import os
import pathlib

# Pfad zur lokalen SQLite-Datenbank
BASE_DIR = pathlib.Path(__file__).resolve().parent
DB_PATH = os.getenv("TEAS_DB_PATH", str(BASE_DIR / "teasesraect.db"))

# Engine definieren
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})

# Session-Factory
SessionLocal = scoped_session(sessionmaker(bind=engine))

def get_session():
    """Neue Session holen"""
    return SessionLocal()
