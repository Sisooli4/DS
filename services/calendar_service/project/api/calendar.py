import httpx
from fastapi import APIRouter, Request, Depends, Form
from fastapi import HTTPException
from icecream import ic
from datetime import date
from ..database.db_wrapper import add_share, add_to_calendar, get_calendar

from pydantic import BaseModel

router = APIRouter()


@router.get("/{username}")
async def get_cal(username:str, asker:str):
    events, message = await get_calendar(username, asker)
    if events:
        return {'events': events}
    elif message == "not_permitted":
        raise HTTPException(status_code=401, detail="No access rights")
    elif message == "nothing_to_show":
        raise HTTPException(status_code=404, detail="No events to show")
    elif message == "server_error":
        raise HTTPException(status_code=500, detail="Internal Server Error while getting calendar")

@router.post("")
async def add_event_to_calendar(event_id:int = Form(), title:str = Form(), date:date = Form(), organizer:str = Form(), private:str = Form(), username:str = Form(), status:str=Form()):
    ic(event_id, title, date, organizer, private, username)
    event, message = await add_to_calendar(event_id, title, date, organizer, private, username, status)
    if event:
        ic("hello1")
        return {'detail': "Event was added to calendar!"}
    elif message == "event_already_planned":
        ic("hello2")
        raise HTTPException(status_code=409, detail="Event already planned!")
    elif message == "server_error":
        ic("hello3")
        raise HTTPException(status_code=500, detail="Server error while adding event to calendar, try again later!")

@router.post("/share")
async def add_sha(owner:str, shared:str):
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

