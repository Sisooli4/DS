from sqlalchemy import select
import logging
import bcrypt
from icecream import ic
from .models import User
from .database import get_async_session
from sqlalchemy.exc import SQLAlchemyError


async def add_user(username: str, password: str):
    async with get_async_session() as session:
        try:
            stmt = select(User).where(User.username == username)
            result = await session.execute(stmt)
            user = result.scalars().first()
            if user:
                logging.warning(f"Username {username} already exists.")
                return None, "user_already_exists"

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            new_user = User(username=username, password=hashed_password)
            session.add(new_user)
            return username, "User added successfully!"

        except SQLAlchemyError as e:
            await session.rollback()
            logging.error(f"Error adding user {username}: {str(e)}")
            return None, "server_error"


async def verify_user(username: str, password: str):
    async with get_async_session() as session:
        try:
            stmt = select(User).where(User.username == username)
            result = await session.execute(stmt)
            user = result.scalars().first()
            if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                logging.info(f"User {username} authenticated successfully.")
                return username, "authentication successful"
            else:
                logging.warning(f"Authentication failed for user {username}.")
                return None, "invalid_credentials"
        except SQLAlchemyError as e:
            logging.error(f"Database error during authentication for user {username}: {str(e)}")
            return None, "server_error"

async def user_exists(username: str):
    async with get_async_session() as session:
        try:
            stmt = select(User).where(User.username == username)
            result = await session.execute(stmt)
            user = result.scalars().first()
            if user:
                logging.info(f"User {username} exists.")
                return username, "user exists"
            else:
                logging.warning(f"User {username}, does not exists.")
                return None, "invalid_user"
        except SQLAlchemyError as e:
            logging.error(f"Database error during authentication for user {username}: {str(e)}")
            return None, "server_error"
