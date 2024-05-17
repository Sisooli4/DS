import httpx
from fastapi import APIRouter, Form, HTTPException
from datetime import date
from pydantic import BaseModel
from typing import List
from ..database.db_wrapper import add_event, get_event, get_public, add_participant

router = APIRouter()

class Event(BaseModel):
    id: int
    title: str
    organizer: str
    date: date
    private: str
    text: str
    participants: List[List[str]]

class HTTPError(BaseModel):
    detail: str

@router.post("",
    responses={
        200: {"description": "Event created successfully", "content": {"application/json": {"example": {"event_id": 1}}}},
        409: {"description": "Conflict - Event already exists", "model": HTTPError},
        500: {"description": "Internal Server Error", "model": HTTPError}
    }
)
async def create_an_event(title: str = Form(...), organizer: str = Form(...), date: date = Form(...), private: str = Form(...), text: str = Form(...)):
    """
    Create a new event.

    Args:
        title (str): The title of the event.
        organizer (str): The organizer of the event.
        date (date): The date of the event.
        private (str): The privacy status of the event.
        text (str): The description of the event.

    Returns:
        dict: A dictionary containing the event ID if successful.

    Raises:
        HTTPException: 409 if the event already exists.
        HTTPException: 500 if there is a server error or an unknown error occurs.
    """
    event_id, error_code = await add_event(title, organizer, date, private.capitalize(), text)
    if event_id:
        return {"event_id": event_id}
    elif error_code == 'event_already_exists':
        raise HTTPException(status_code=409, detail="Event already exists! Please choose a different title or date.")
    elif error_code == 'server_error':
        raise HTTPException(status_code=500, detail="An error occurred while adding the event! Please try again later.")
    else:
        raise HTTPException(status_code=500, detail="An unknown error occurred.")

@router.get("/event/{id}",
    responses={
        200: {"description": "Event retrieved successfully", "content": {"application/json": {"example": {"event": {}}}}},
        401: {"description": "Unauthorized - Access denied", "model": HTTPError},
        404: {"description": "Not Found - Event cannot be found", "model": HTTPError},
        500: {"description": "Internal Server Error", "model": HTTPError}
    }
)
async def get_an_event_by_id(id: int, username: str):
    """
    Get details of an event by ID.

    Args:
        id (int): The ID of the event.
        username (str): The username of the requester.

    Returns:
        dict: A dictionary containing the event details if found.

    Raises:
        HTTPException: 401 if the user does not have permission to access the event.
        HTTPException: 404 if the event is not found.
        HTTPException: 500 if there is a server error or an unknown error occurs.
    """
    event, error_code = await get_event(id, username)
    if event:
        return {"event": event}
    elif error_code == 'access_denied':
        raise HTTPException(status_code=401, detail="You don't have permission to access this event.")
    elif error_code == 'event_not_found':
        raise HTTPException(status_code=404, detail="Event cannot be found.")
    elif error_code == 'server_error':
        raise HTTPException(status_code=500, detail="An error occurred while retrieving the event! Please try again later.")
    else:
        raise HTTPException(status_code=500, detail="An unknown error occurred.")

@router.get("/public",
    responses={
        200: {"description": "Public events retrieved successfully", "content": {"application/json": {"example": {"events": []}}}},
        404: {"description": "Not Found - No public events found", "model": HTTPError},
        500: {"description": "Internal Server Error", "model": HTTPError}
    }
)
async def get_public_event():
    """
    Get all public events.

    Returns:
        dict: A dictionary containing public events if found.

    Raises:
        HTTPException: 404 if no public events are found.
        HTTPException: 500 if there is a server error or an unknown error occurs.
    """
    events, error_code = await get_public()
    if error_code == "events_found":
        return {"events": events}
    elif error_code == 'events_not_found':
        raise HTTPException(status_code=404, detail="No events to show!")
    elif error_code == 'server_error':
        raise HTTPException(status_code=500, detail="An error occurred while searching for the public events! Please try again later.")
    else:
        raise HTTPException(status_code=500, detail="An unknown error occurred.")

@router.post("/participant",
    responses={
        200: {"description": "Participant added successfully", "content": {"application/json": {"example": {"message": "Participant added"}}}},
        409: {"description": "Conflict - Participant already exists", "model": HTTPError},
        500: {"description": "Internal Server Error", "model": HTTPError}
    }
)
async def add_participant_to_event(event_id: int, username: str, status: str):
    """
    Add a participant to an event.

    Args:
        event_id (int): The ID of the event.
        username (str): The username of the participant.
        status (str): The participation status of the user.

    Returns:
        dict: A dictionary containing a success message if the participant is added successfully.

    Raises:
        HTTPException: 409 if the participant already exists.
        HTTPException: 500 if there is a server error or an unknown error occurs.
    """
    added, message = await add_participant(event_id, username, status)
    if added:
        return {"message": message}
    elif message == 'participant_already_exists':
        raise HTTPException(status_code=409, detail=f"User {username} already participates!")
    elif message == 'server_error':
        raise HTTPException(status_code=500, detail=f"An error occurred while adding {username} to the event as participant! Please try again later.")
    else:
        raise HTTPException(status_code=500, detail="An unknown error occurred.")
