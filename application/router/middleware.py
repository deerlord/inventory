import logging
import re

from fastapi import FastAPI, HTTPException, Request


def example(app: FastAPI):
    @app.middleware("http")
    async def middleware(request: Request, call_next):
        response = await call_next(request)
        return response


def testing(app: FastAPI):
    @app.middleware("http")
    async def middleware(request: Request, call_next):
        print("middleware")
        response = await call_next(request)
        if response.status_code == 200:
            print("success")
            async for x in response.body_iterator:
                print("x", x)
        return response


def log(app: FastAPI):
    logger = logging.getLogger("requests")

    @app.middleware("http")
    async def middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID")
        logger.info(
            "%(request_id)s - %(method)s %(url)",
            request_id=request_id,
            method=request.method,
            url=request.url,
        )
        try:
            result = await call_next(request)
            logger.info("%(request_id)s - COMPLETED", request_id=request_id)
            return result
        except Exception:
            logger.exception("%(request_id)s - FAILED", request_id=request_id)
        raise HTTPException(500)


def ensure_request_id(app: FastAPI):
    @app.middleware("http")
    async def middleware(request: Request, call_next):
        # header_name = Settings().request_id_header
        # request_id = "" if header_name is None else request.headers.get(header_name)
        # TODO: add request id
        return await call_next(request)
