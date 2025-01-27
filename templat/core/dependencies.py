from aiohttp import ClientSession


async def get_async_client() -> ClientSession:
    async with ClientSession() as session:
        yield session
