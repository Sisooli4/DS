from sqlalchemy import select
import logging
import bcrypt
from icecream import ic
from datetime import date
from .models import Share, Calendar
from .database import get_async_session
from sqlalchemy.exc import SQLAlchemyError


async def get_calendar(username:str, asker:str):
    async with get_async_session() as session:
        try:
            if username != asker:
                stmt = select(Share).where(Share.owner == username, Share.shared == asker)
                result = await session.execute(stmt)
                user = result.scalars().first()
                if not user:
                    return None, 'not_permitted'

            stmt = select(Calendar).where(Calendar.username == username)
            result = await session.execute(stmt)
            events = [[event.event_id, event.title, event.date, event.organizer, event.status, event.private] for event in result.scalars().all()]
            ic(events)
            if events == []:
                return None, 'nothing_to_show'
            else:
                return events, "Got event_ids"

        except SQLAlchemyError as e:
            await session.rollback()
            logging.error(f"Error adding event to calendar: {str(e)}")
            return None, "server_error"

async def add_to_calendar(event_id: int, title:str, date:date, organizer:str, private:str, username: str, status:str):
    async with get_async_session() as session:
        try:
            stmt = select(Calendar).where(Calendar.username == username, Calendar.event_id == event_id,
                                            Calendar.title==title, Calendar.date==date, Calendar.organizer==organizer,
                                            Calendar.private==private, Calendar.status==status)
            result = await session.execute(stmt)
            user = result.scalars().first()
            if user:
                logging.warning(f"Event is already in calendar.")
                return None, "event_already_planned"

            new_event = Calendar(event_id=event_id, username=username, title=title, date=date, organizer=organizer, private=private, status=status)
            session.add(new_event)
            return event_id, f"Event successfully added to calendar!"

        except SQLAlchemyError as e:
            await session.rollback()
            logging.error(f"Error adding event to calendar: {str(e)}")
            return None, "server_error"

async def add_share(owner: str, shared: str):
    async with get_async_session() as session:
        try:
            stmt = select(Share).where(Share.owner == owner, Share.shared == shared)
            result = await session.execute(stmt)
            user = result.scalars().first()
            if user:
                logging.warning(f"Sharing with user {owner} already done.")
                return None, "share_already_exists"

            new_share = Share(owner=owner, shared=shared)
            session.add(new_share)
            return shared, f"Shared successfully with {shared} added successfully!"

        except SQLAlchemyError as e:
            await session.rollback()
            logging.error(f"Error sharing with user {shared}: {str(e)}")
            return None, "server_error"
