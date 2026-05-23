from __future__ import annotations

import discord

from .emojis import EMOJIS


LEVELS = {
    "INFO": {
        "color": 0x2B2D31,
        "emoji": "announcement",
    },

    "SUCCESS": {
        "color": 0x1F8B4C,
        "emoji": "success",
    },

    "WARNING": {
        "color": 0xF0B232,
        "emoji": "warning",
    },

    "ERROR": {
        "color": 0xDA373C,
        "emoji": "fail",
    },

    "DEBUG": {
        "color": 0x5865F2,
        "emoji": "developer",
    },

    "SYSTEM": {
        "color": 0x8E44AD,
        "emoji": "okay",
    },

    # MUSIC SPECIFIC
    "MUSIC": {
        "color": 0x5865F2,
        "emoji": "music",
    },
}


# SAFE LIMITER
def _safe(
    text: str | None,
    limit: int,
):

    if not text:
        return None

    return (
        text
        if len(text) <= limit
        else text[: limit - 1] + "…"
    )


# FIELD FORMATTER
def _format_field(
    name,
    value,
    emoji=None,
):

    if emoji:
        return f"{emoji} {name}", value

    return name, value


# MAIN EMBED FACTORY
def make_embed(
    *,
    title: str,
    description: str | None = None,
    level: str = "INFO",
    fields=None,
    footer: str | None = None,
    show_timestamp: bool = True,
    use_emoji: bool = True,
    highlight: bool = False,
    compact: bool = False,
    thumbnail: str | None = None,
    image: str | None = None,
    author=None
):

    level = level.upper()
    config = LEVELS.get(
        level,
        LEVELS["INFO"],
    )
    color = config["color"]
    emoji = (
        EMOJIS.get(config["emoji"])
        if use_emoji
        else None
    )
    # TITLE
    title = (
        f"{emoji} {title}"
        if emoji
        else title
    )
    # DESCRIPTION HIGHLIGHT
    if description and highlight:
        description = f"```{description}```"
    embed = discord.Embed(
        title=_safe(title, 256),
        description=_safe(description, 4096),
        color=color,
    )
    # AUTHOR
    if author:
        name = author.get("name")
        icon_url = author.get("icon_url")
        embed.set_author(
            name=_safe(name, 256),
            icon_url=icon_url
        )
    # FIELDS
    if fields:

        for field in fields[:25]:

            if len(field) == 3:
                name, value, inline = field
                field_emoji = None

            elif len(field) == 4:
                name, value, inline, field_emoji = field

            else:
                continue

            name, value = _format_field(
                name,
                value,
                field_emoji,
            )

            embed.add_field(
                name=_safe(name, 256),
                value=_safe(value, 1024),
                inline=inline if not compact else True,
            )

    # THUMBNAIL
    if thumbnail:
        embed.set_thumbnail(
            url=thumbnail,
        )

    # IMAGE
    if image:
        embed.set_image(
            url=image,
        )

    # FOOTER
    if footer:
        embed.set_footer(
            text=_safe(footer, 2048),
        )

    # TIMESTAMP
    if show_timestamp:
        embed.timestamp = discord.utils.utcnow()

    return embed