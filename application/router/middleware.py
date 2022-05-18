from fastapi import FastAPI, Request


def example(app: FastAPI):
    @app.middleware("http")
    async def middleware(request: Request, call_next):
        response = await call_next(request)
        return response
