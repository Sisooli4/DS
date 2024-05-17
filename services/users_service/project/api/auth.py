from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import typing
from ..database.db_wrapper import add_user, verify_user, user_exists

router = APIRouter()

class UserModel(BaseModel):
    id: typing.Optional[int]
    username: str
    password: str

class HTTPError(BaseModel):
    detail: str

@router.post("",
    responses={
        200: {"description": "User registered successfully", "content": {"application/json": {"example": {"username": "john_doe"}}}},
        409: {"description": "Conflict - User already exists", "model": HTTPError},
        500: {"description": "Internal Server Error", "model": HTTPError}
    }
)
async def register_user(username: str = Form(...), password: str = Form(...)):
    """
    Register a new user.

    Args:
        username (str): The username of the new user.
        password (str): The password of the new user.

    Returns:
        dict: A dictionary containing the registered username.

    Raises:
        HTTPException: 409 if the user already exists.
        HTTPException: 500 if there is a server error or an unknown error occurs.
    """
    username, error_code = await add_user(username, password)
    if username:
        return {'username': username}
    elif error_code == 'user_already_exists':
        raise HTTPException(status_code=409, detail="User already exists! Please choose a different username.")
    elif error_code == 'server_error':
        raise HTTPException(status_code=500, detail="An error occurred while registering the user! Please try again later.")
    else:
        raise HTTPException(status_code=500, detail="An unknown error occurred.")

@router.post("/authenticate",
    responses={
        200: {"description": "Authentication successful", "content": {"application/json": {"example": {"username": "john_doe"}}}},
        401: {"description": "Unauthorized - Invalid credentials", "model": HTTPError},
        500: {"description": "Internal Server Error", "model": HTTPError}
    }
)
async def login_user(username: str = Form(...), password: str = Form(...)):
    """
    Authenticate a user and return their username if successful.

    Args:
        username (str): The username of the user.
        password (str): The password of the user.

    Returns:
        dict: A dictionary containing the authenticated username.

    Raises:
        HTTPException: 401 if the credentials are invalid.
        HTTPException: 500 if there is a server error or an unknown error occurs.
    """
    username, error_code = await verify_user(username, password)
    if username:
        return {'username': username}
    elif error_code == 'invalid_credentials':
        raise HTTPException(status_code=401, detail="Invalid credentials. Please check username and password.")
    elif error_code == 'server_error':
        raise HTTPException(status_code=500, detail="An error occurred during authentication. Please try again later.")
    else:
        raise HTTPException(status_code=500, detail="An unknown error occurred.")

@router.get("/exists",
    responses={
        200: {"description": "User exists", "content": {"application/json": {"example": True}}},
        404: {"description": "Not Found - User does not exist", "model": HTTPError},
        500: {"description": "Internal Server Error", "model": HTTPError}
    }
)
async def check_if_username_exists(username: str):
    """
    Check if a username exists.

    Args:
        username (str): The username to check.

    Returns:
        bool: True if the username exists.

    Raises:
        HTTPException: 404 if the user does not exist.
        HTTPException: 500 if there is a server error or an unknown error occurs.
    """
    usernameEx, error_code = await user_exists(username)
    if usernameEx:
        return True
    elif error_code == 'invalid_user':
        raise HTTPException(status_code=404, detail=f"User {username} does not exist.")
    elif error_code == 'server_error':
        raise HTTPException(status_code=500, detail=f"An error occurred during verification of {username}. Please try again later.")
    else:
        raise HTTPException(status_code=500, detail=f"An unknown error occurred when verifying {username}.")
