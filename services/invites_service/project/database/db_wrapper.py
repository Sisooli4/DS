from sqlalchemy import delete, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import logging

from datetime import date

from .database import get_async_session
# Import your models here
from .models import Invite

async def add_invite(event_id: int, title:str, date:date, organizer:str, private:str, username: str) -> tuple:
    async with get_async_session() as session:
        try:
            # Check if the event already exists with the same constraints
            stmt = select(Invite).where(
                Invite.event_id == event_id, Invite.title == title,
                Invite.username == username, Invite.date == date, Invite.organizer == organizer,
                Invite.private == private,
            )
            result = await session.execute(stmt)
            existing_invite = result.scalars().first()
            if existing_invite:
                return None, "invite_already_exists"

            # Add the new event
            new_invite = Invite(
                event_id=event_id, title=title, date=date, organizer=organizer, private=private,
                username=username
            )
            session.add(new_invite)
            await session.commit()

            # Refresh the new_event object to get the ID
            return True, "Event added successfully!"

        except SQLAlchemyError as e:
            await session.rollback()
            logging.error(f"Error adding invite for user {username}: {str(e)}")
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
                invites = [[invite.event_id, invite.title, invite.date, invite.organizer, invite.private] for invite in existing_invites]
                return invites, "events_found"
            else:
                return [], "events_not_found"

        except SQLAlchemyError as e:
            await session.rollback()
            logging.error(f"Error getting invites for user {username}: {str(e)}")
            return None, "server_error"

async def delete_invite(event_id: int, username: str) -> str:
    async with get_async_session() as session:
        try:
            stmt = select(Invite).where(
                Invite.event_id == event_id,
                Invite.username == username
            )
            result = await session.execute(stmt)
            existing_invite = result.scalars().first()
            if not existing_invite:
                return "invite_not_found"
            # Find the invite to delete
            stmt = delete(Invite).where(
                and_(Invite.event_id == event_id, Invite.username == username)
            )
            await session.execute(stmt)

            # Commit the transaction
            await session.commit()

            return "invite_deleted"

        except SQLAlchemyError as e:
            await session.rollback()
            logging.error(f"Error deleting invite for user {username} and event {event_id}: {str(e)}")
            return "server_error"

