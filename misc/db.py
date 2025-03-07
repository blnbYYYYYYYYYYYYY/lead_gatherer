import redis.asyncio as redis


async def set_data(key, value):
    """
    thread_id to second context manager as key
    and chat_id as value
    """
    connection = redis.Redis().from_url("redis://localhost:6379/5")
    await connection.set(key, value)
    await connection.aclose()


async def get_data(key):
    connection = redis.Redis().from_url("redis://localhost:6379/5")
    data = await connection.get(key)
    await connection.aclose()
    return data


async def del_data(key):
    connection = redis.Redis().from_url("redis://localhost:6379/5")
    await connection.delete(key)
    await connection.aclose()
