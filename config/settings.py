import os
from dotenv import load_dotenv

load_dotenv()


# BASE ENV GETTERS
def _get(key, default=None):
    value = os.getenv(key)
    if value is None:
        return default
    
    return value.strip()


def _get_bool(key, default="false"):
    value = _get(
        key,
        default,
    )
    return str(value).lower() in ("1", "true", "yes", "on")


def _get_int(key, default=0):
    value = _get(key, default)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# DISCORD
TOKEN = _get("TOKEN")

PREFIX = (_get("PREFIX", "!") or "!")

SYNC_COMMANDS = _get_bool("SYNC_COMMANDS", "false")

ENV = (_get("ENV", "prod") or "prod").lower()

# LAVALINK
LAVALINK_HOST = _get("LAVALINK_HOST", "127.0.0.1")
LAVALINK_PORT = _get_int("LAVALINK_PORT", 2333)
LAVALINK_PASSWORD = _get("LAVALINK_PASSWORD", "youshallnotpass")
LAVALINK_SECURE = _get_bool("LAVALINK_SECURE", "false")

# MUSIC
DEFAULT_VOLUME = _get_int("DEFAULT_VOLUME", 80)
AUTO_RECONNECT = _get_bool("AUTO_RECONNECT", "true")


# HELPERS
def is_dev():
    return ENV == "dev"


def lavalink_uri():
    protocol = ("https" if LAVALINK_SECURE else "http")
    return (f"{protocol}://"
            f"{LAVALINK_HOST}:"
            f"{LAVALINK_PORT}")


# VALIDATION
def validate():
    missing = []

    if not TOKEN:
        missing.append("TOKEN")

    if not LAVALINK_PASSWORD:
        missing.append("LAVALINK_PASSWORD")

    if missing:
        raise RuntimeError("Missing env variables: "
                           f"{', '.join(missing)}")
