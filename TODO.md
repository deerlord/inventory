## Add atomic lock

https://docs.python.org/3/library/asyncio-sync.html

```python
import asyncio

LOCK = asyncio.Lock()

def acid(coro):
    async def wrapper(*args, **kwargs):
        async with LOCK:
            result = await coro(*args, **kwargs)
        return result
    return wrapper


```