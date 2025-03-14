import os
import redis.asyncio as redis
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.base import StorageKey
from typing import Union, Dict, Any, Optional

host = {os.getenv("REDIS_HOST")}

def keybuilder(chat_id:int) -> StorageKey:
    return StorageKey(bot_id=chat_id,
                      chat_id=chat_id,
                      user_id=chat_id)

async def update_data(key: int, data: Dict[str, Any], ttl: Optional[int] = None) -> Dict[str, Any]:
    connection = RedisStorage(redis=redis.Redis, data_ttl=ttl).from_url("redis://redis:6379/5")
    current_data = await get_data(key)
    current_data.update(data)
    storage_key = keybuilder(key)
    await connection.set_data(storage_key, current_data)
    await connection.close()
    return current_data


async def set_data(key: int, data: Dict[str, Any], ttl: Optional[int] = None):
    """
    thread_id to second context manager as key
    and chat_id as value
    """
    connection = RedisStorage(redis=redis.Redis, data_ttl=ttl).from_url("redis://redis:6379/5")
    storage_key = keybuilder(key)
    await connection.set_data(storage_key, data)
    await connection.close()


async def get_data(key: int) -> Dict[str, Any]:
    connection = RedisStorage(redis=redis.Redis).from_url("redis://redis:6379/5")
    storage_key = keybuilder(key)
    data = await connection.get_data(storage_key)
    await connection.close()
    return data


async def get_value(key: int, dict_key: str) -> Union[Any, None]:
    connection = RedisStorage(redis=redis.Redis).from_url("redis://redis:6379/5")
    storage_key = keybuilder(key)
    value = await connection.get_value(storage_key, dict_key)
    await connection.close()
    return value


async def keys(key: str):   # legacy
    connection = redis.Redis().from_url("redis://localhost:6379/5")
    data = await connection.keys()
    await connection.aclose()
    return data


async def del_data(key: str):   # legacy
    connection = redis.Redis().from_url("redis://localhost:6379/5")
    await connection.delete(key)
    await connection.aclose()
