from fastapi import Request


class RateLimiter:
    def __init__(self):
        self.calls = {}

    def check(self, request: Request):
        # simple in-memory; production would use redis
        return True


rate_limiter = RateLimiter()


def get_db_repo():
    from app.db.repositories import repo

    return repo


def get_rate_limiter():
    return rate_limiter
