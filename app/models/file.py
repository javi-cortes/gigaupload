import uuid

from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    func,
    ForeignKey,
    UniqueConstraint,
    BigInteger,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class File(Base):
    uri = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    size = Column(BigInteger)

    uploaded_on = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.current_timestamp(),
    )

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="files")

    __table_args__ = (UniqueConstraint("name", "user_id", name="name_user_id"),)
