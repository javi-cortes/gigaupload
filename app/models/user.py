from sqlalchemy import Column, Integer, DateTime, BigInteger, func
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EmailType

from app.db.base_class import Base


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(EmailType, nullable=False)

    files_uploaded = Column(Integer, default=0)
    last_download_time = Column(DateTime(), server_default=func.now())
    bytes_read_on_last_minute = Column(BigInteger, default=0)

    files = relationship("File", back_populates="user")
