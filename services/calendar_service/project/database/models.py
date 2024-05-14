from sqlalchemy import Column, Integer, String, select
from sqlalchemy.orm import declarative_base


Base = declarative_base()

# This is our SQLAlchemy model used with the database
class Thing(Base):
    __tablename__ = "thing"
    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
