from sqlalchemy import (
    MetaData,
    create_engine,
)
from sqlalchemy.orm import sessionmaker

from config import AppSettings
from models import Base

configs = AppSettings()

DATABASE_URL = configs.DATABASE_PATH_SYNC

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)
