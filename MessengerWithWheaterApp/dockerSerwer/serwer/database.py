from sqlalchemy import create_engine
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

USERNAME = os.getenv("DB_USER","")
PASSWORD = os.getenv("DB_PASSWORD","")
HOST = os.getenv("DB_HOST","")

SQLALCHEMY_DATABASE_URL =  f'postgresql://{USERNAME}:{PASSWORD}@{HOST}'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()