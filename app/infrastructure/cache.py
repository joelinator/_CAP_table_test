# For scalability: Add caching with Redis
# New file: app/infrastructure/cache.py

import redis
import os
import json
from typing import Optional, Any

redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0, decode_responses=True)

def get_cache(key: str) -> Optional[Any]:
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None

def set_cache(key: str, value: Any, ttl: int = 300):  # 5 min default
    redis_client.set(key, json.dumps(value), ex=ttl)
