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


async def get_param(url_list):
    result_str = ''
    if url_list:
        tasks = [asyncio.create_task(make_request(url)) for url in url_list]
        res = await asyncio.gather(*tasks)
        for r in res:
            name = r.get('name')
            if name:
                result_str += name+', '
    return result_str


async def one_char_processing(j):
    char_obj = Char(name=j.get('name'))
    char_obj.birth_year = j.get('birth_year')
    char_obj.eye_color = j.get('eye_color')
    char_obj.films = await get_param(j.get('films'))
    char_obj.gender = j.get('gender')
    char_obj.hair_color = j.get('hair_color')
    char_obj.height = j.get('height')
    hw = await make_request(j.get('homeworld'))
    char_obj.homeworld = hw.get('name')
    char_obj.mass = j.get('mass')
    char_obj.skin_color = j.get('skin_color')
    char_obj.species = await get_param(j.get('species'))
    char_obj.starships = await get_param(j.get('starships'))
    char_obj.vehicles = await get_param(j.get('vehicles'))
    print(char_obj)
    return char_obj


async def people_on_page_processing(page):
    tasks = [asyncio.create_task(one_char_processing(item)) for item in page.get('results')]
    char_objects = await asyncio.gather(*tasks)
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


async def db_output(data):
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
    )
    # для тестов
    await drop_and_create_db(engine)

    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        async with session.begin():
            session.add_all(data)
        await session.commit()

    await engine.dispose()


async def async_main():
    data = await collect_people()
    await db_output(data)


asyncio.run(async_main())
