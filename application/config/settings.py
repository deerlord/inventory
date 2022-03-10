import os

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    database_protocol: str = Field(env="DATABASE_PROTOCOL", default="sqlite")
    database_name: str = Field(env="DATABASE_NAME", default="/data.sqlite")

    class Config:
        env_file = "" if bool(os.environ.get("DEBUG", "false")) else ""
