"""Tests de securite -- redaction des champs sensibles (Hermes Mission Control V0)"""
import sys
from pathlib import Path

# Allow import from dashboard/ without install
sys.path.insert(0, str(Path(__file__).parent.parent / "dashboard"))

from plugin_api import redact


def test_redact_api_key():
    assert redact({"api_key": "sk-super-secret-123"})["api_key"] == "[REDACTED]"

def test_redact_token():
    assert redact({"token": "ghp_abc123"})["token"] == "[REDACTED]"

def test_redact_secret():
    assert redact({"secret": "my-secret-value"})["secret"] == "[REDACTED]"

def test_redact_password():
    assert redact({"password": "hunter2"})["password"] == "[REDACTED]"

def test_redact_cookie():
    assert redact({"cookie": "session=abc123"})["cookie"] == "[REDACTED]"

def test_redact_auth():
    assert redact({"auth": "Bearer xyz"})["auth"] == "[REDACTED]"

def test_redact_credential():
    assert redact({"credential": "some-cred"})["credential"] == "[REDACTED]"

def test_redact_private_key():
    assert redact({"private_key": "-----BEGIN RSA PRIVATE KEY-----"})["private_key"] == "[REDACTED]"

def test_preserve_non_sensitive():
    data = {"name": "elina", "model": "claude-opus-4-7", "enabled": True}
    result = redact(data)
    assert result["name"] == "elina"
    assert result["model"] == "claude-opus-4-7"
    assert result["enabled"] is True

def test_preserve_numeric_values():
    data = {"max_tokens": 4096, "temperature": 0.7}
    result = redact(data)
    assert result["max_tokens"] == 4096
    assert result["temperature"] == 0.7

def test_redact_nested_dict():
    data = {"provider": {"name": "anthropic", "api_key": "sk-ant-secret", "model": "claude-sonnet-4-6"}}
    result = redact(data)
    assert result["provider"]["api_key"] == "[REDACTED]"
    assert result["provider"]["name"] == "anthropic"
    assert result["provider"]["model"] == "claude-sonnet-4-6"

def test_redact_list_of_dicts():
    data = [{"name": "agent1", "token": "tok-aaa"}, {"name": "agent2", "token": "tok-bbb"}]
    result = redact(data)
    assert result[0]["token"] == "[REDACTED]"
    assert result[1]["token"] == "[REDACTED]"
    assert result[0]["name"] == "agent1"

def test_redact_deeply_nested():
    data = {"config": {"llm": {"providers": [
        {"id": "openai", "api_key": "sk-openai"},
        {"id": "mistral", "api_key": "ms-key"},
    ]}}}
    result = redact(data)
    providers = result["config"]["llm"]["providers"]
    assert providers[0]["api_key"] == "[REDACTED]"
    assert providers[1]["api_key"] == "[REDACTED]"
    assert providers[0]["id"] == "openai"

def test_redact_case_insensitive_uppercase():
    assert redact({"API_KEY": "sk-upper"})["API_KEY"] == "[REDACTED]"

def test_redact_case_insensitive_mixed():
    assert redact({"Api_Key": "sk-mixed"})["Api_Key"] == "[REDACTED]"

def test_redact_none_value():
    assert redact({"api_key": None})["api_key"] == "[REDACTED]"

def test_redact_empty_dict():
    assert redact({}) == {}

def test_redact_empty_list():
    assert redact([]) == []

def test_redact_scalar_passthrough():
    assert redact("hello") == "hello"
    assert redact(42) == 42
    assert redact(True) is True

def test_redact_multiple_sensitive_in_one_dict():
    data = {"api_key": "key", "token": "tok", "name": "safe", "password": "pw"}
    result = redact(data)
    assert result["api_key"] == "[REDACTED]"
    assert result["token"] == "[REDACTED]"
    assert result["password"] == "[REDACTED]"
    assert result["name"] == "safe"
