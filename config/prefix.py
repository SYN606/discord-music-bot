from discord.ext import commands
import discord
import os

PREFIX = (os.getenv("PREFIX") or "dvm ").strip()

if not PREFIX:
    PREFIX = "sus"

PREFIX_LOWER = PREFIX.lower()


def normalize(content: str):
    """
    FORCE:
    sus ping -> susping
    SUS PING -> susping
    sus    ping -> susping
    """
    if not content:
        return content

    stripped = content.lstrip()

    if not stripped.lower().startswith(PREFIX_LOWER):
        return content

    rest = stripped[len(PREFIX):].lstrip()
    return f"{PREFIX}{rest}"


def dynamic_prefix(bot: commands.Bot, message: discord.Message):
    """
    Always use HARD prefix:
    susping
    """
    return commands.when_mentioned_or(PREFIX)(bot, message)
