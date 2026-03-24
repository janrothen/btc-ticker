import tomllib
from functools import lru_cache
from pathlib import Path

# Prefer config.toml next to the current working directory (production: the
# systemd WorkingDirectory). Fall back to the repo root for development.
_CWD_CONFIG = Path.cwd() / "config.toml"
_REPO_CONFIG = Path(__file__).parents[2] / "config.toml"
_CONFIG_PATH = _CWD_CONFIG if _CWD_CONFIG.exists() else _REPO_CONFIG


@lru_cache(maxsize=None)
def config() -> dict:
    with open(_CONFIG_PATH, "rb") as f:
        return tomllib.load(f)
