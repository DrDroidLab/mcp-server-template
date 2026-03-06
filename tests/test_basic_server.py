import pytest

from mcp_template import config


def test_load_config_defaults():
    app_config = config.load_config()

    assert app_config.server.name == "MCP Template Server"
    assert app_config.server.transport in {"stdio", "streamable-http", "http"}
    assert app_config.server.port == 8000


def test_load_config_port_invalid_falls_back(monkeypatch):
    monkeypatch.setenv("MCP_PORT", "not-a-number")
    app_config = config.load_config()
    assert app_config.server.port == 8000

