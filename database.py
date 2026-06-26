import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

load_dotenv()

URL = os.getenv("DATABASE_URL")

if not URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

if URL.startswith("postgres://"):
    URL = URL.replace("postgres://", "postgresql://", 1)

connect_args = {}
parsed_url = make_url(URL)
db_sslmode = os.getenv("DB_SSLMODE")

if db_sslmode:
    connect_args["sslmode"] = db_sslmode
elif "sslmode" not in parsed_url.query and parsed_url.host not in {
    "localhost",
    "127.0.0.1",
    "::1",
}:
    connect_args["sslmode"] = "require"

engine = create_engine(
    url=URL,
    connect_args=connect_args,
    poolclass=NullPool,
    pool_pre_ping=True,
)

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
