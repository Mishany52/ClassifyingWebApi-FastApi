import psycopg
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session
from ..config import settings

engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


