import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv


# Keep server settings at the project root; this package lives below integrations/.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_CONFIG_PATH = _PROJECT_ROOT / "mcp_servers.json"
_ENV_PLACEHOLDER = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def _resolve_env_vars(value: object) -> object:
    """Resolve ${NAME} placeholders in nested MCP configuration values."""
    if isinstance(value, dict):
        return {key: _resolve_env_vars(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_resolve_env_vars(item) for item in value]
    if isinstance(value, str):
        def replace(match: re.Match[str]) -> str:
            name = match.group(1)
            resolved = os.environ.get(name)
            if resolved is None:
                raise ValueError(f"Required environment variable {name} is not set")
            return resolved

        return _ENV_PLACEHOLDER.sub(replace, value)
    return value


def load_mcp_configs() -> dict[str, dict]:
    """Load MCP server definitions and resolve their environment variables."""
    load_dotenv(_PROJECT_ROOT / ".env")
    os.environ.setdefault("CWD", str(Path.cwd().resolve()))
    try:
        config = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"MCP configuration file not found: {_CONFIG_PATH}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid MCP configuration JSON in {_CONFIG_PATH}: {exc}") from exc

    if not isinstance(config, dict) or not isinstance(config.get("mcp_servers"), dict):
        raise ValueError(f"MCP configuration must contain an 'mcp_servers' object: {_CONFIG_PATH}")

    # Resolve credentials before connecting so missing variables fail during startup.
    servers = _resolve_env_vars(config["mcp_servers"])
    if not servers:
        raise ValueError(f"No MCP servers are configured in {_CONFIG_PATH}")
    return servers
