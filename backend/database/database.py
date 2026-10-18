from sqlalchemy import create_engine
from config.settings import get_settings
from sqlalchemy.orm import DeclarativeBase, sessionmaker


engine = create_engine(get_settings().DB_LINK)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()