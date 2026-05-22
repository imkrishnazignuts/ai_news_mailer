import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

URL = os.getenv("DATABASE_URL")

engine = create_engine(url=URL)

Session_local = sessionmaker(
    bind=engine,
    autoflush=True
)

def get_db():
    db = Session_local()
    try:
        yield db
    finally:
        db.close()
