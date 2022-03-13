import logging
from dataclasses import dataclass
import functools


def logger(func: Callable):
    wrapper = functools.wraps(func)
    return wrapper(_async if asyncio.iscoroutinefunction(func) else _sync)


async def _async(*args, **kwargs):
    _logging(args, kwargs)
    return await self.func(*args, **kwargs)
    

def _sync(*args, **kwargs):
    _logging(args, kwargs)
    return self.func(*args, **kwargs)


def _logging(args, kwargs):
    with_ = ""
    log_name = " ".join(
        word.capitalize() for word in self.func.__name__.replace("_", "").split(" ")
    )
    if args or kwargs:
        with_ = f" with "
        if args:
            with_ += f"{args}"
            if kwargs:
                with_ += "; "
        if kwargs:
            with_ += f"{kwargs}"
    message = f"{log_name}{with_}"
    logging.info(message)
