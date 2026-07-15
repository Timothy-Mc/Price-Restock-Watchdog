from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from config import Config
from storage.models import Base

engine = create_engine(Config.DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

def create_tables():
    Base.metadata.create_all(bind=engine)