import httpx
from fastapi import APIRouter, Form, HTTPException
from datetime import date
from pydantic import BaseModel
from ..database.db_wrapper import add_share, add_to_calendar, get_calendar

router = APIRouter()

class HTTPError(BaseModel):
    detail: str

@router.get("/{username}",
    responses={
        200: {"description": "Events retrieved successfully", "content": {"application/json": {"example": {"events": []}}}},
        401: {"description": "Unauthorized - No access rights", "model": HTTPError},
        404: {"description": "Not Found - No events to show", "model": HTTPError},
        500: {"description": "Internal Server Error", "model": HTTPError}
    }
)
async def get_event_in_calendar(username: str, asker: str):
    """
    Get events from a user's calendar.

    Args:
        username (str): The username of the calendar owner.
        asker (str): The username of the person requesting the calendar.

    Returns:
        dict: A dictionary containing events if found.

    Raises:
        HTTPException: 401 if access rights are not permitted.
        HTTPException: 404 if no events are found.
        HTTPException: 500 if there is an internal server error.
    """
    events, message = await get_calendar(username, asker)
    if events:
        return {'events': events}
    elif message == "not_permitted":
        raise HTTPException(status_code=401, detail="No access rights")
    elif message == "nothing_to_show":
        raise HTTPException(status_code=404, detail="No events to show")
    elif message == "server_error":
        raise HTTPException(status_code=500, detail="Internal Server Error while getting calendar")

@router.post("",
    responses={
        200: {"description": "Event successfully added to your calendar!", "content": {"application/json": {"example": {"detail": "Event was added to calendar!"}}}},
        409: {"description": "Conflict - Event already planned", "model": HTTPError},
        500: {"description": "Internal Server Error", "model": HTTPError}
    }
)
async def add_event_to_calendar(event_id: int = Form(...), title: str = Form(...), date: date = Form(...),
                                organizer: str = Form(...), private: str = Form(...), username: str = Form(...),
                                status: str = Form(...)):
    """
    Add an event to a user's calendar.

    Args:
        event_id (int): The ID of the event.
        title (str): The title of the event.
        date (date): The date of the event.
        organizer (str): The organizer of the event.
        private (str): Whether the event is private.
        username (str): The username of the calendar owner.
        status (str): The status of the event.

    Returns:
        dict: A dictionary with a detail message if the event was added successfully.

    Raises:
        HTTPException: 409 if the event is already planned.
        HTTPException: 500 if there is a server error.
    """
    event, message = await add_to_calendar(event_id, title, date, organizer, private, username, status)
    if event:
        return {'detail': "Event successfully added to your calendar!"}
    elif message == "event_already_planned":
        raise HTTPException(status_code=409, detail="Event already planned!")
    elif message == "server_error":
        raise HTTPException(status_code=500, detail="Server error while adding event to calendar, try again later!")

@router.post("/share",
    responses={
        200: {"description": "Calendar shared successfully", "content": {"application/json": {"example": {"detail": "Calendar shared with user!"}}}},
        409: {"description": "Conflict - Calendar already shared or sharing with self", "model": HTTPError},
        500: {"description": "Internal Server Error", "model": HTTPError}
    }
)
async def share_calendar(owner: str, shared: str):
    """
    Share a user's calendar with another user.

    Args:
        owner (str): The username of the calendar owner.
        shared (str): The username of the user to share the calendar with.

    Returns:
        dict: A dictionary with a detail message if the calendar was shared successfully.

    Raises:
        HTTPException: 409 if the calendar is being shared with the owner themselves or if the share already exists.
        HTTPException: 500 if there is a server error.
    """
    if owner == shared:
        raise HTTPException(status_code=409, detail="You can't share a calendar with yourself!")
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"http://nginx/users/exists?username={shared}")
        if resp.status_code == 200:
            shared, message = await add_share(owner, shared)
            if shared:
                return {'detail': f"Calendar shared with {shared}!"}
            elif message == "share_already_exists":
                raise HTTPException(status_code=409, detail="You already shared your calendar with this user!")
            elif message == "server_error":
                raise HTTPException(status_code=500, detail="Internal Server Error while sharing agenda, try again later!")
        else:
            raise HTTPException(status_code=resp.status_code, detail=resp.json().get("detail"))
