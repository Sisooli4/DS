from sqlalchemy import Column, Integer, String, select, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import declarative_base


Base = declarative_base()

# This is our SQLAlchemy model used with the database
class Calendar(Base):
    __tablename__ = 'calendars'
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    organizer = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    private = Column(String, nullable=False)
    username = Column(String, nullable=False)
    status = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint('username', 'event_id', name='uix_user_event'),
    )

class Share(Base):
    __tablename__ = "share"
    id = Column(Integer, primary_key=True)
    owner = Column(String, nullable=False)
    shared = Column(String, nullable=False)
