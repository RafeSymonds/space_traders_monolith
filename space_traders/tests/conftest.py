from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_space_traders_api():
    from space_traders_api import ApiClient, Configuration

    config = MagicMock(spec=Configuration)
    config.api_key = {"AgentToken": "test_token"}
    config.host = "https://api.spacetraders.io"
    config.verify_ssl = True
    config.timeout = 1000

    api_client = MagicMock(spec=ApiClient)
    api_client.configuration = config

    return {
        "config": config,
        "client": api_client,
    }
