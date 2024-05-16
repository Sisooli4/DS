import httpx
from fastapi import APIRouter, Form
from fastapi import HTTPException
from icecream import ic
from datetime import date

from pydantic import BaseModel

from ..database.db_wrapper import add_invite, get_invites, delete_invite

router = APIRouter()

class Invite(BaseModel):
    id: int
    event_id: int
    username: str

@router.post("")
async def add(event_id:int = Form(), title:str = Form(), date:date = Form(), organizer:str = Form(), private:str = Form(), usernames:str = Form()):
    usernamesList = usernames.split(";")
    errorString = ""
    for username in usernamesList:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"http://nginx/users/exists?username={username}")
            if resp.status_code == 200:
                invite, message = await add_invite(event_id, title, date, organizer, private, username)
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
async def get(username:str):
    invites, message = await get_invites(username)
    if message == "events_not_found":
        raise HTTPException(status_code=404, detail="No invites found for this user")
    elif message == "server_error":
        raise HTTPException(status_code=500, detail="Server error when trying to get invites, try again later!")

    else:
        return {"invites":invites}

@router.delete("")
async def delete(event_id:int, username:str):
    message = await delete_invite(event_id, username)
    if message == "invite_deleted":
        return {'detail': 'Invite deleted'}
    elif message == "invite_not_found":
        raise HTTPException(status_code=404, detail="The invite doesn't exist")
    elif message == "server_error":
        raise HTTPException(status_code=500, detail='Server error while deleting invite')
    else:
        raise HTTPException(status_code=500, detail="An unknown error has occurred while deleting invite")
