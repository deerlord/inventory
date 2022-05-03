import logging
import re

from fastapi import FastAPI, HTTPException, Request


def example(app: FastAPI):
    @app.middleware("http")
    async def middleware(request: Request, call_next):
        response = await call_next(request)
        return response

