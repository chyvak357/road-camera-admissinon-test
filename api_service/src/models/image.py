
from sqlalchemy import UUID, VARCHAR, BigInteger, Column, DateTime, LargeBinary
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ImageModel(Base):
    __tablename__ = "images"

    id = Column(BigInteger, primary_key=True, index=True)
    external_id = Column(UUID, unique=True, nullable=False)
    
    description = Column(VARCHAR(200), nullable=False) 
    received_at = Column(DateTime, nullable=False)
    
    data = Column(LargeBinary, nullable=False)
    
