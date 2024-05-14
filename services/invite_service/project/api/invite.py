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

router = APIRouter()

class ThingModel(BaseModel):
    id: typing.Optional[int]
    text: str
