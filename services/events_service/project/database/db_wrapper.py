from datetime import date
from sqlalchemy import select
import logging
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from .models import Event, Participants
from .database import get_async_session


async def add_event(title: str, organizer: str, date: date, private: str, text: str) -> tuple:
    async with get_async_session() as session:
        try:
            # Check if the event already exists with the same constraints
            stmt = select(Event).where(
                Event.title == title,
                Event.organizer == organizer,
                Event.date == date,
                Event.private == private
            )
            result = await session.execute(stmt)
            existing_event = result.scalars().first()
            if existing_event:
                return None, "event_already_exists"

            # Add the new event
            new_event = Event(
                title=title,
                organizer=organizer,
                date=date,
                private=private,
                text=text
            )
            session.add(new_event)
            await session.commit()

            # Refresh the new_event object to get the ID
            await session.refresh(new_event)
            return new_event.id, "Event added successfully!"

        except SQLAlchemyError as e:
            await session.rollback()
            logging.error(f"Error adding event {title} by {organizer} on {date}: {str(e)}")
            return None, "server_error"

async def get_event(event_id: int, username: str) -> tuple:
    async with get_async_session() as session:
        try:
            stmt = select(Event).where(Event.id == event_id)
            result = await session.execute(stmt)
            existing_event = result.scalars().first()

            if existing_event:
                participants_stmt = select(Participants).where(
                    Participants.event_id == event_id and Participants.username == username)
                participants_result = await session.execute(participants_stmt)
                participants = [[participant.username, participant.status] for participant in
                                participants_result.scalars().all()]

                # Check if the event is public or if the username matches the organizer
                if existing_event.private == 'Public' or existing_event.organizer == username or username in [participant[0] for participant in participants]:
                    # Check if the username is among the participants

                    return [existing_event.title, existing_event.date, existing_event.organizer, existing_event.private, existing_event.text, participants], "event_found"

                else:
                    return None, "access_denied"

            else:
                return None, "event_not_found"

        except SQLAlchemyError as e:
            await session.rollback()
            logging.error(f"Error loading event with id {event_id}: {str(e)}")
            return None, "server_error"


async def get_public():
    async with get_async_session() as session:
        try:
            stmt = select(Event).where(Event.private == 'Public')
            result = await session.execute(stmt)
            events = result.scalars().all()
            if events:
                public_events = [(event.title, event.date, event.organizer, event.id) for event in events]
                return public_events, "events_found"
            else:
                return [], "events_not_found"

        except SQLAlchemyError as e:
            await session.rollback()
            logging.error(f"Error loading public events: {str(e)}")
            return None, "server_error"

async def add_participant(event_id: int, username: str, status:str) -> tuple:
    async with get_async_session() as session:
        try:
            # Check if the event already exists with the same constraints
            stmt = select(Participants).where(
                Participants.event_id == event_id,
                Participants.username == username,
                Participants.status == status
            )
            result = await session.execute(stmt)
            existing_event = result.scalars().first()
            if existing_event:
                return None, "participant_already_exists"

            # Add the new event
            new_participant = Participants(
                event_id=event_id,
                username=username,
                status=status
            )
            session.add(new_participant)
            await session.commit()
            return True, "Participant added successfully!"

        except SQLAlchemyError as e:
            await session.rollback()
            logging.error(f"Error adding participant {new_participant}: {str(e)}")
            return None, "server_error"
