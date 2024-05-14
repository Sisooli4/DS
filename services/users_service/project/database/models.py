from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import declarative_base


Base = declarative_base()

# This is our SQLAlchemy model used with the database
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint('username', name='uix_title'),
    )
