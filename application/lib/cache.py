import functools
from typing import Callable


def singleton(func: Callable) -> Callable:
    """
    Cache result the first time this function is called
    """
    result = None

    @functools.wraps(func)
    def cached(*args, **kwargs):
        nonlocal result
        return func(*args, **kwargs) if result is None else result

    return cached
