import functools
import logging
from datetime import datetime
from typing import Callable

import pytz
from fastapi import Request, Response

logger = logging.getLogger("crud")


def setup_logger(func: Callable) -> Callable:
    logger_ = logging.getLogger("setup")

    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> bool:
        retval: bool = False
        action = " ".join(
            word.capitalize() for word in func.__name__.replace("_", " ").split(" ")
        )
        logger_.info(action)
        try:
            await func(*args, **kwargs)
            retval = True
        except Exception as e:
            logger_.error(e)
        return retval

    return wrapper


def log_request(request: Request, request_id: str):
    timestamp = _timestamp()
    message = f'{timestamp}: {request_id} - "{request.method} {request.url}"'
    logger.info(message)


def log_response(response: Response, request_id: str):
    timestamp = _timestamp()
    message = f"{timestamp}: {request_id} - {response.status_code}"
    logger.info(message)


def _timestamp() -> str:
    now = datetime.utcnow().replace(tzinfo=pytz.UTC)
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    return timestamp
