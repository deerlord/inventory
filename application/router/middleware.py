from fastapi import FastAPI, Request

from application.config.settings import Settings
from application.lib import logger


def example(app: FastAPI):
    @app.middleware("http")
    async def middleware(request: Request, call_next):
        response = await call_next(request)
        return response


# TODO: understand middleware and order of ops better
def log_request(app: FastAPI):
    @app.middleware("http")
    async def middleware(request: Request, call_next):
        request_id = request.headers.get(str(Settings().request_id_header))
        logger.log_request(request, request_id)
        response = await call_next(request)
        logger.log_response(response, request_id)
        return response


def ensure_request_id(app: FastAPI):
    @app.middleware("http")
    async def middleware(request: Request, call_next):
        # header_name = Settings().request_id_header
        # request_id = "" if header_name is None else request.headers.get(header_name)
        # TODO: add request id
        return await call_next(request)
