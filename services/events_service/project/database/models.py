from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base


Base = declarative_base()

# This is our SQLAlchemy model used with the database
class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    organizer = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    private = Column(String, nullable=False)
    text = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint('title', 'organizer', 'date', 'private', name='uix_title_organizer_date_private'),
    )

class Participants(Base):
    __tablename__ = "participants"
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    username = Column(String, nullable=False)
    status = Column(String, nullable=False)

