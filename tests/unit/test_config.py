from __future__ import annotations

from ha_mcp.config import get_settings


def test_ha_settings_read_documented_environment_variables(monkeypatch):
    monkeypatch.setenv("HA_URL", "http://homeassistant.test:8123")
    monkeypatch.setenv("HA_TOKEN", "test-token")
    monkeypatch.setenv("HA_VERIFY_SSL", "false")

    settings = get_settings()

    assert settings.ha.url == "http://homeassistant.test:8123"
    assert settings.ha.token == "test-token"
    assert settings.ha.verify_ssl is False