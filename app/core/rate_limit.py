import os
from datetime import UTC, datetime

from fastapi import HTTPException, Request, status
from redis import Redis
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.auth.dependencies import get_api_key_value
from app.db.models import User
from app.db.session import SessionLocal


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
FREE_TIER_PER_MINUTE_LIMIT = "5/minute"
FREE_TIER_PER_MONTH_LIMIT = 100

redis_client = Redis.from_url(REDIS_URL, decode_responses=True)


def get_api_key_rate_limit_key(request: Request) -> str:
    return get_api_key_value(request) or get_remote_address(request)


def is_free_tier_request(request: Request) -> bool:
    api_key = get_api_key_value(request)
    if not api_key:
        return False

    with SessionLocal() as db:
        user = db.query(User).filter(User.api_key == api_key).first()
        return bool(user and user.plan_tier == "free")


limiter = Limiter(key_func=get_api_key_rate_limit_key, default_limits=[])


def _monthly_usage_key(api_key: str, now: datetime | None = None) -> str:
    current_time = now or datetime.now(UTC)
    return f"rate_limit:flash:monthly:{current_time:%Y-%m}:{api_key}"


def _seconds_until_next_month(now: datetime | None = None) -> int:
    current_time = now or datetime.now(UTC)
    if current_time.month == 12:
        next_month = datetime(current_time.year + 1, 1, 1, tzinfo=UTC)
    else:
        next_month = datetime(current_time.year, current_time.month + 1, 1, tzinfo=UTC)
    return max(1, int((next_month - current_time).total_seconds()))


def check_monthly_flash_limit(user: User) -> None:
    if user.plan_tier != "free":
        return

    usage = redis_client.get(_monthly_usage_key(user.api_key))
    current_usage = int(usage or 0)
    if current_usage >= FREE_TIER_PER_MONTH_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Free-tier monthly limit exceeded for the Flash API.",
        )


def increment_monthly_flash_usage(user: User, amount: int = 1) -> None:
    if user.plan_tier != "free":
        return

    key = _monthly_usage_key(user.api_key)
    pipeline = redis_client.pipeline()
    pipeline.incrby(key, amount)
    pipeline.expire(key, _seconds_until_next_month())
    pipeline.execute()
