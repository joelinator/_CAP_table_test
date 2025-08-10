# app/infrastructure/cache.py (updated)

import redis
import os
import json
from typing import Optional, Any
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0, decode_responses=True)

def get_cache(key: str) -> Optional[Any]:
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
    except redis.exceptions.RedisError as e:
        logger.warning(f"Redis error in get_cache: {str(e)}. Falling back to no cache.")
    return None

def set_cache(key: str, value: Any, ttl: int = 300) -> None:
    try:
        redis_client.set(key, json.dumps(value), ex=ttl)
    except redis.exceptions.RedisError as e:
        logger.warning(f"Redis error in set_cache: {str(e)}. Skipping cache set.")

def delete_cache(key: str) -> None:
    try:
        redis_client.delete(key)
    except redis.exceptions.RedisError as e:
        logger.warning(f"Redis error in delete_cache: {str(e)}. Skipping cache deletion.")
