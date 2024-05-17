import httpx
from fastapi import APIRouter, Form, HTTPException
from datetime import date
from pydantic import BaseModel
from ..database.db_wrapper import add_invite, get_invites, delete_invite

router = APIRouter()

class Invite(BaseModel):
    id: int
    event_id: int
    username: str

class HTTPError(BaseModel):
    detail: str

@router.post("",
    responses={
        200: {"description": "Invites sent successfully", "content": {"application/json": {"example": {"detail": "All invites are sent!"}}}},
        422: {"description": "Unprocessable Entity - Errors in sending invites", "model": HTTPError}
    }
)
async def add_invite_to_list(event_id: int = Form(...), title: str = Form(...), date: date = Form(...), organizer: str = Form(...), private: str = Form(...), usernames: str = Form(...)):
    """
    Add invites to a list of users for an event.

    Args:
        event_id (int): The ID of the event.
        title (str): The title of the event.
        date (date): The date of the event.
        organizer (str): The organizer of the event.
        private (str): The privacy status of the event.
        usernames (str): A semicolon-separated list of usernames to invite.

    Returns:
        dict: A success message if all invites are sent.

    Raises:
        HTTPException: 422 if there are errors in sending invites.
    """
    usernamesList = usernames.split(";")
    errorString = ""
    for username in usernamesList:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"http://nginx/users/exists?username={username}")
            if resp.status_code == 200:
                invite, message = await add_invite(event_id, title, date, organizer, private, username)
                if not invite:
                    if message == "self_invite":
                        errorString += "You can't invite yourself!\n"
                    if message == "invite_already_exists":
                        errorString += f"User {username} is already invited!\n"
                    elif message == "server_error":
                        errorString += f"Server error when trying to send invite to {username}, try again later!\n"
            elif resp.status_code in [404, 500]:
                errorString += resp.json()["detail"]

    if errorString == "":
        return {"detail": "All invites are sent!\n"}
    else:
        raise HTTPException(status_code=422, detail=errorString)

@router.get("/{username}",
    responses={
        200: {"description": "Invites retrieved successfully", "content": {"application/json": {"example": {"invites": []}}}},
        404: {"description": "Not Found - No invites found for this user", "model": HTTPError},
        500: {"description": "Internal Server Error", "model": HTTPError}
    }
)
async def get_invites_for_user(username: str):
    """
    Get invites for a specific user.

    Args:
        username (str): The username to retrieve invites for.

    Returns:
        dict: A dictionary containing the invites for the user.

    Raises:
        HTTPException: 404 if no invites are found for the user.
        HTTPException: 500 if there is a server error.
    """
    invites, message = await get_invites(username)
    if message == "events_not_found":
        raise HTTPException(status_code=404, detail="No invites found for this user")
    elif message == "server_error":
        raise HTTPException(status_code=500, detail="Server error when trying to get invites, try again later!")
    else:
        return {"invites": invites}

@router.delete("",
    responses={
        200: {"description": "Invite deleted successfully", "content": {"application/json": {"example": {"detail": "Invite deleted"}}}},
        404: {"description": "Not Found - The invite doesn't exist", "model": HTTPError},
        500: {"description": "Internal Server Error", "model": HTTPError}
    }
)
async def delete_invite_of_user(event_id: int, username: str):
    """
    Delete an invite for a specific user.

    Args:
        event_id (int): The ID of the event.
        username (str): The username to delete the invite for.

    Returns:
        dict: A success message if the invite is deleted.

    Raises:
        HTTPException: 404 if the invite doesn't exist.
        HTTPException: 500 if there is a server error or an unknown error occurs.
    """
    message = await delete_invite(event_id, username)
    if message == "invite_deleted":
        return {'detail': 'Invite deleted'}
    elif message == "invite_not_found":
        raise HTTPException(status_code=404, detail="The invite doesn't exist")
    elif message == "server_error":
        raise HTTPException(status_code=500, detail='Server error while deleting invite')
    else:
        raise HTTPException(status_code=500, detail="An unknown error has occurred while deleting invite")
