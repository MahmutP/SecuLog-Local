import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# If DATABASE_URL is not provided, fallback to the local postgres docker settings
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://seculog_user:seculog_pass@localhost:5432/seculog")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
