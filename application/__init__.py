from fastapi import FastAPI

from application.router import generate_routers


def setup_application():
    app = FastAPI()
    for router in generate_routers():
        app.include_router(router, prefix="/api")
    return app
