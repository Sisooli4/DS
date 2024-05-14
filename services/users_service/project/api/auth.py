from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from fastapi import HTTPException
from ..database.db_wrapper import add_user, verify_user
import typing
from icecream import ic

from pydantic import BaseModel

router = APIRouter()

class UserModel(BaseModel):
    id: typing.Optional[int]
    username: str
    password: str

@router.post("")
async def register(username: str = Form(...), password: str = Form(...)):

    username, error_code = await add_user(username, password)
    if username:
        return {'username': username}
    elif error_code == 'user_already_exists':
        raise HTTPException(status_code=409, detail="User already exists!\n Please choose a different username.")
    elif error_code == 'server_error':
        raise HTTPException(status_code=500, detail="An error occurred while registering the user!\n Please try again later.")
    else:
        # Handle other unspecified errors generically
        raise HTTPException(status_code=500, detail="An unknown error occurred.")

@router.post("/authenticate")
async def login(username: str = Form(...), password: str = Form(...)):
    """
    Authenticates a user and initializes their session if successful.

    Parameters:
        request (Request): The request object containing form data with username and password.

    Returns:
        RedirectResponse: Redirects to the homepage if authentication is successful.

    Raises:
        HTTPException: 400 Bad Request if authentication fails.
    """

    # Check user credentials
    username, error_code = await verify_user(username, password)
    if username:
        return {'username': username}
    elif error_code == 'invalid_credentials':
        raise HTTPException(status_code=401, detail="Invalid credentials.\n Please check username and password.")
    elif error_code == 'server_error':
        raise HTTPException(status_code=500, detail="An error occurred during authentication.\n Please try again later.")
    else:
        # Handle other unspecified errors generically
        raise HTTPException(status_code=500, detail="An unknown error occurred.")

