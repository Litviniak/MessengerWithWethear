from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime

from .database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String,nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"),nullable=False)
    reciver_id = Column(Integer, ForeignKey("users.id"),nullable=False)
    is_recived = Column(Boolean, default=False)
    date = Column(DateTime, nullable=False)

