"""Hermes Mission Control -- Plugin API V0 (read-only, non-intrusive)"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

from fastapi import FastAPI, HTTPException
import uvicorn

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

HERMES_PROFILES_DIR = Path(os.environ.get(
    "HERMES_PROFILES_DIR",
    Path.home() / ".hermes" / "profiles"
))

HERMES_CONFIG_FILE = Path(os.environ.get(
    "HERMES_CONFIG_FILE",
    Path.home() / ".hermes" / "config.yaml"
))

API_HOST = os.environ.get("HMC_HOST", "127.0.0.1")
API_PORT = int(os.environ.get("HMC_PORT", "7700"))

# Fields automatically redacted in all API responses
REDACTED_FIELDS: set[str] = {
    "api_key", "token", "secret", "password",
    "cookie", "auth", "credential", "private_key",
}

# ---------------------------------------------------------------------------
# Security: redact sensitive fields
# ---------------------------------------------------------------------------

_REDACT_PATTERN = re.compile(
    r"|".join(re.escape(f) for f in REDACTED_FIELDS),
    re.IGNORECASE,
)


def redact(obj: Any, _depth: int = 0) -> Any:
    """Recursively redact sensitive fields from dicts/lists."""
    if _depth > 20:
        return obj
    if isinstance(obj, dict):
        return {
            k: "[REDACTED]" if _REDACT_PATTERN.fullmatch(str(k)) else redact(v, _depth + 1)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [redact(item, _depth + 1) for item in obj]
    return obj


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_yaml_safe(path: Path) -> dict:
    """Load a YAML file safely, return empty dict on error."""
    if yaml is None:
        return {"error": "pyyaml not installed -- pip install pyyaml"}
    try:
        with path.open(encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception as exc:
        return {"error": str(exc)}


def _discover_agents() -> list[dict]:
    """Scan HERMES_PROFILES_DIR for agent profile folders."""
    agents = []
    if not HERMES_PROFILES_DIR.exists():
        return agents
    for entry in sorted(HERMES_PROFILES_DIR.iterdir()):
        if entry.is_dir():
            config_file = entry / "config.yaml"
            soul_file = entry / "SOUL.md"
            agents.append({
                "id": entry.name,
                "path": str(entry),
                "has_config": config_file.exists(),
                "has_soul": soul_file.exists(),
            })
    return agents


def _load_hermes_config() -> dict:
    """Load the global Hermes config (read-only, redacted)."""
    if not HERMES_CONFIG_FILE.exists():
        return {"warning": "Hermes config.yaml not found", "path": str(HERMES_CONFIG_FILE)}
    raw = _load_yaml_safe(HERMES_CONFIG_FILE)
    return redact(raw)


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Hermes Mission Control",
    version="0.1.0",
    description="Plugin cockpit read-only pour agents Hermes -- V0 non intrusive",
)


@app.get("/health")
def health() -> dict:
    """Statut du plugin."""
    return {
        "status": "ok",
        "version": "0.1.0",
        "phase": 0,
        "readonly": True,
        "dry_run": True,
        "hermes_profiles_dir": str(HERMES_PROFILES_DIR),
        "profiles_dir_exists": HERMES_PROFILES_DIR.exists(),
    }


@app.get("/agents")
def list_agents() -> dict:
    """Liste des profils Hermes detectes (aucun secret expose)."""
    agents = _discover_agents()
    return {
        "count": len(agents),
        "agents": agents,
        "profiles_dir": str(HERMES_PROFILES_DIR),
    }


@app.get("/agents/{agent_id}")
def get_agent(agent_id: str) -> dict:
    """Detail d'un profil agent -- config redacted."""
    # Sanitize agent_id to prevent path traversal
    if not re.match(r"^[\w\-\.]+$", agent_id):
        raise HTTPException(status_code=400, detail="Invalid agent id")

    agent_path = HERMES_PROFILES_DIR / agent_id
    if not agent_path.exists() or not agent_path.is_dir():
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    config = {}
    config_file = agent_path / "config.yaml"
    if config_file.exists():
        config = redact(_load_yaml_safe(config_file))

    soul_preview = None
    soul_file = agent_path / "SOUL.md"
    if soul_file.exists():
        try:
            text = soul_file.read_text(encoding="utf-8")
            soul_preview = text[:500] + ("..." if len(text) > 500 else "")
        except Exception:
            soul_preview = "[unreadable]"

    return {
        "id": agent_id,
        "path": str(agent_path),
        "config": config,
        "soul_preview": soul_preview,
    }


@app.get("/providers")
def list_providers() -> dict:
    """Providers configures dans Hermes -- secrets masques."""
    config = _load_hermes_config()
    providers = config.get("providers", config.get("llm", {}))
    return {
        "providers": redact(providers),
        "source": str(HERMES_CONFIG_FILE),
    }


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"[HMC] Demarrage Hermes Mission Control API sur http://{API_HOST}:{API_PORT}")
    print(f"[HMC] Profils Hermes : {HERMES_PROFILES_DIR}")
    print("[HMC] Mode : lecture seule (V0 non intrusive)")
    uvicorn.run(app, host=API_HOST, port=API_PORT)
