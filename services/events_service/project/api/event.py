from datetime import date

from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from fastapi import HTTPException
import requests
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import typing
import typing
from icecream import ic

from pydantic import BaseModel

from ..database.db_wrapper import add_event, get_event, get_public

router = APIRouter()


class Event(BaseModel):
    id: int
    title: str
    organizer: str
    date: date
    private: str
    text: str
    participants: typing.List[typing.List[str]]


@router.post("")
async def add(title:str = Form(), organizer: str = Form(), date: date = Form(), private:str = Form(), text: str = Form()):

    event_id, error_code = await add_event(title, organizer, date, private, text)
    if event_id:
        return {"event_id": event_id}
    elif error_code == 'event_already_exists':
        raise HTTPException(status_code=409, detail="Event already exists!\n Please choose a different title or date.")
    elif error_code == 'server_error':
        raise HTTPException(status_code=500, detail="An error occurred while adding the event!\n Please try again later.")
    else:
        # Handle other unspecified errors generically
        raise HTTPException(status_code=500, detail="An unknown error occurred.")

@router.get("/event/{id}")
async def get(id: int, username:str):
    event, error_code = await get_event(id, username)
    if event:
        return {"event": event}
    elif error_code == 'access_denied':
        raise HTTPException(status_code=401, detail="You don't have permission to access this event.")
    elif error_code == 'event_not_found':
        raise HTTPException(status_code=404, detail="Event cannot be found.")
    elif error_code == 'server_error':
        raise HTTPException(status_code=500, detail="An error occurred while adding the event!\n Please try again later.")
    else:
        # Handle other unspecified errors generically
        raise HTTPException(status_code=500, detail="An unknown error occurred.")

@router.get("/public")
async def public():

    events, error_code = await get_public()
    ic("hello")
    if error_code == "events_found":
        return {"events": events}
    elif error_code == 'events_not_found':
        ic("hello2")
        raise HTTPException(status_code=404, detail="No events to show!")
    elif error_code == 'server_error':
        ic("hello3")
        raise HTTPException(status_code=500,
                            detail="An error occurred while searching for the public events!\nPlease try again later.")
    else:
        raise HTTPException(status_code=500, detail="An unknown error occurred.")

