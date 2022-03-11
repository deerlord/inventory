from fastapi import FastAPI

from application.router import generate_routers, middleware


def setup_application():
    app = FastAPI()
    for router in generate_routers():
        app.include_router(router)

    middleware.acid_transaction(app)

    return app
