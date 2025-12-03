from redis import Redis
from rq import Queue
import os

def get_redis() -> Redis:
    host = os.getenv("REDIS_HOST", "127.0.0.1")
    port = int(os.getenv("REDIS_PORT", "6379"))
    return Redis(host=host, port=port, decode_responses=False)

def get_queue() -> Queue:
    return Queue(connection=get_redis())
