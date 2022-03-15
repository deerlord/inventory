import os
from distutils.util import strtobool
from typing import Optional

from pydantic import BaseSettings, Field, PositiveInt


class Settings(BaseSettings):
    database_protocol: str = Field(env="DATABASE_PROTOCOL", default="sqlite")
    database_name: str = Field(env="DATABASE_NAME", default="/data.sqlite")
    database_username: Optional[str] = Field(env="DATABASE_USERNAME", default=None)
    database_password: Optional[str] = Field(env="DATABASE_PASSWORD", default=None)
    database_hostname: Optional[str] = Field(env="DATABASE_HOSTNAME", default=None)
    database_port: Optional[PositiveInt] = Field(env="DATABASE_PORT", default=None)
    request_id_header: Optional[str] = Field(
        env="REQUEST_ID_HEADER", default="MISSING_REQUEST_ID"
    )
    debug: bool = Field(env="DEBUG", default=False)

    class Config:
        env_file = f"./settings.{'prd' if strtobool(os.environ.get('DEBUG', 'false')) else 'dbg'}"
