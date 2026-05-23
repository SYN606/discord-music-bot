from discord.ext import commands
import discord
import os

PREFIX = (os.getenv("PREFIX") or "dvm ").strip()

if not PREFIX:
    PREFIX = "dvm"

PREFIX_LOWER = PREFIX.lower()


def normalize(content: str):
    if not content:
        return content
    stripped = content.lstrip()
    if not stripped.lower().startswith(PREFIX_LOWER):
        return content

    rest = stripped[len(PREFIX):].lstrip()
    return f"{PREFIX}{rest}"


def dynamic_prefix(bot: commands.Bot, message: discord.Message):
    return commands.when_mentioned_or(PREFIX)(bot, message)
