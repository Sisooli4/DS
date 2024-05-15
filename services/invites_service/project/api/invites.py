import httpx
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from fastapi import HTTPException
import requests
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import typing
from icecream import ic

from pydantic import BaseModel

from ..database.db_wrapper import add_invite, get_invites

router = APIRouter()

class Invite(BaseModel):
    id: int
    event_id: int
    username: str

@router.post("")
async def add(event_id:int, usernames:str):
    usernamesList = usernames.split(";")
    errorString = ""
    for username in usernamesList:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"http://nginx/users/exists?username={username}")
            if resp.status_code == 200:
                invite, message = await add_invite(event_id, username)
                if not invite:
                    if message == "invite_already_exists":
                        errorString += f"User {username} is already invited!\n"
                    elif message == "server_error":
                        errorString += f"Server error when trying to send invite to {username}, try again later!\n"
            elif resp.status_code == 404 or resp.status_code == 500:
                errorString += resp.json()["detail"]

    if errorString == "":
        return {"detail": "All invites are send!\n"}

    else:
        raise HTTPException(status_code=422, detail=errorString)

@router.get("/{username}")
async def add(username:str):
    event_ids, message = await get_invites(username)
    if message == "events_not_found":
        raise HTTPException(status_code=404, detail="No invites found for this user")
    elif message == "server_error":
        raise HTTPException(status_code=500, detail="Server error when trying to get invites, try again later!")

    else:
        invites = []
        for event_id in event_ids:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"http://nginx/events/event/{event_id}?username={username}&invite={True}")
                if resp.status_code == 200:
                    event = resp.json().get("event")
                    invites.append((event_id, event[0], event[1], event[2], event[3]))

        return {"invites":invites}
