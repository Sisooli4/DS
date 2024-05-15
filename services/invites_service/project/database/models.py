from sqlalchemy import Column, Integer, String, select, ForeignKey
from sqlalchemy.orm import declarative_base


Base = declarative_base()

# This is our SQLAlchemy model used with the database
class Invite(Base):
    __tablename__ = "invites"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, nullable=False)
    username = Column(String, nullable=False)
