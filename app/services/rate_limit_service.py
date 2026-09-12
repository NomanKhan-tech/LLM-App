import time

from app.services.redis_service import redis_client

REQUEST_LIMIT = 10
WINDOW_SECONDS = 60


def check_rate_limit(user_id: int) -> bool:
    key = f"rate_limit:user:{user_id}"

    current_count = redis_client.get(key)

    if current_count is None:
        redis_client.set(key, 1, ex=WINDOW_SECONDS)
        return True

    if int(current_count) >= REQUEST_LIMIT:
        return False

    redis_client.incr(key)
    return True
