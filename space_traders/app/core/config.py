import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv
from space_traders_api import Configuration
from space_traders_api.api_client import ApiClient

load_dotenv()


@dataclass
class Config:
    api_token: str
    faction: str = "COSMIC"
    starting_system: str = "X1-TEST"

    _instance: Optional["Config"] = None

    @classmethod
    def get_instance(cls) -> "Config":
        if cls._instance is None:
            token = os.environ.get("SPACE_TRADERS_TOKEN")
            if not token:
                raise ValueError(
                    "SPACE_TRADERS_TOKEN environment variable not set. Create a .env file or set the environment variable."
                )
            cls._instance = cls(api_token=token)
        return cls._instance

    def get_api_client(self) -> ApiClient:
        config = Configuration()
        config.access_token = self.api_token
        return ApiClient(configuration=config)

    def get_configured_client(self):
        config = Configuration()
        config.access_token = self.api_token
        return config
