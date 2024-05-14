from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Import your models here
from .models import User

class Database:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: int):
        async with self.session as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
            return user

    async def add_user(self, user_data):
        async with self.session as session:
            new_user = User(**user_data)
            session.add(new_user)
            await session.commit()
            return new_user

    # More database operations can be defined here
