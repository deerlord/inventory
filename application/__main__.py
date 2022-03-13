import uvicorn  # type: ignore

from application import setup_application

if __name__ == "__main__":
    app = setup_application()
    uvicorn.run(app, host="localhost", port=8000, log_level="debug")
