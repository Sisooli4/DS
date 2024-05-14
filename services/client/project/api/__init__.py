from fastapi import Depends
from .app import app
from . import docs

from .client import router as event_router
from ..database.database import get_async_session, create_db_and_tables
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.on_event("startup")
async def on_startup(session: AsyncSession = Depends(get_async_session)):
    await create_db_and_tables()

app.mount("/static", StaticFiles(directory="static"))
app.include_router(docs.router, prefix="/client-service", tags=["docs"])
app.include_router(event_router, prefix="/web", tags=["web"])
