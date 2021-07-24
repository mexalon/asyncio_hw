import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL
from models import Base, Char


async def drop_and_create_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def put_in_db(s, data):
    async with s.begin():
        s.add(data)


async def async_main():
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
    )
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    await drop_and_create_db(engine)

    async with async_session() as session:
        await put_in_db(session, Char(name='tets'))

        res = await session.execute(select(Char))
        print(f">>>>>>>{res.all()}")

        await session.commit()

    await engine.dispose()


asyncio.run(async_main())
