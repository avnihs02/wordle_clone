import redis
import hashlib
from datetime import timedelta, date, datetime
import json

def open_session():
    """
    create a session with database
    """
    redis_client = redis.Redis(
        host="127.0.0.1",
        port=6379,
        db=0,
        decode_responses=True,
    )
    return redis_client

def write_cache(ip_add):
    client = open_session()
    keyhash = hashlib.md5(ip_add.encode()).hexdigest()
    tomorrow = (date.today() + timedelta(days=1))
    exp = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0)- datetime.now()
    val = client.setex(name=keyhash, time=exp, value="1")
    client.close()

def cache_exist(ip_add):
    client = open_session()
    keyhash = hashlib.md5(ip_add.encode()).hexdigest()
    if client.exists(keyhash):
        ttl = client.ttl(keyhash)
        client.close()
        return True, ttl
    client.close()
    return False, None

def write_stats(key, data):
    client = open_session()
    keyhash = hashlib.md5(key.encode()).hexdigest()
    val = client.set(name=f"stats:{keyhash}", value=json.dumps(data))
    client.close()

def read_stats(key):
    client = open_session()
    keyhash = hashlib.md5(key.encode()).hexdigest()
    val = client.get(name=f"stats:{keyhash}")
    client.close()
    if val:
        return json.loads(val)
    return {}
