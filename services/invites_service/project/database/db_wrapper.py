from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import logging

from datetime import date

from .database import get_async_session
# Import your models here
from .models import Invite

async def add_invite(event_id: int, username: str) -> tuple:
    async with get_async_session() as session:
        try:
            # Check if the event already exists with the same constraints
            stmt = select(Invite).where(
                Invite.event_id == event_id,
                Invite.username == username
            )
            result = await session.execute(stmt)
            existing_invite = result.scalars().first()
            if existing_invite:
                return None, "invite_already_exists"

            # Add the new event
            new_invite = Invite(
                event_id=event_id,
                username=username
            )
            session.add(new_invite)
            await session.commit()

            # Refresh the new_event object to get the ID
            return True, "Event added successfully!"

        except SQLAlchemyError as e:
            await session.rollback()
            logging.error(f"Error adding invite with event id {event_id} for user {username}: {str(e)}")
            return None, "server_error"

async def get_invites(username: str) -> tuple:
    async with get_async_session() as session:
        try:
            # Check if the event already exists with the same constraints
            stmt = select(Invite).where(
                Invite.username == username
            )
            result = await session.execute(stmt)
            existing_invites = result.scalars().all()
            if existing_invites:
                event_ids = [invite.event_id for invite in existing_invites]
                return event_ids, "events_found"
            else:
                return [], "events_not_found"

        except SQLAlchemyError as e:
            await session.rollback()
            logging.error(f"Error getting invites for user {username}: {str(e)}")
            return None, "server_error"
