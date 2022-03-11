import asyncio

from fastapi import FastAPI, Request


def acid_transaction(app: FastAPI):
    lock = asyncio.Lock()

    @app.middleware("http")
    async def middleware(request: Request, call_next):
        async with lock:
            return await call_next(request)
