import asyncio
import aiohttp

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL, API_ROOT
from models import Base, Char


async def drop_and_create_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def make_request(url):
    s = aiohttp.ClientSession()
    resp = await s.get(url)
    json = await resp.json()
    await s.close()
    return json


async def one_char_processing(j):
    char_obj = Char(name=j.get('name'))
    # будет ходить по ссылкам
    return char_obj


async def people_on_page_processing(page):
    char_objects = await asyncio.gather(*[one_char_processing(item) for item in page.get('results')])
    return char_objects


async def collect_people():
    all_chars = []
    has_next = API_ROOT + 'people'
    while has_next:
        first = await make_request(has_next)
        chunk = await people_on_page_processing(first)
        all_chars += chunk
        has_next = first.get('next')

    return all_chars


async def async_main():
    data = await collect_people()
    print(data)

    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
    )
    await drop_and_create_db(engine)

    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        async with session.begin():
            session.add_all(data)
        await session.commit()

    await engine.dispose()


asyncio.run(async_main())
