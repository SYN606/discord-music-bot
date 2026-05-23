from __future__ import annotations
from typing import Any
import discord
from config.embeds import make_embed


class Respond:

    def __init__(self,
                 ctx=None,
                 interaction: discord.Interaction | None = None,
                 channel: discord.abc.Messageable | None = None):
        self.ctx = ctx
        self.interaction = interaction
        self.channel = channel

    # INTERNAL DISPATCHER
    async def _dispatch(self,
                        *,
                        embed: discord.Embed | None = None,
                        content: str | None = None,
                        **kwargs):
        payload: dict[str, Any] = {}

        # ONLY PASS VALUES IF THEY EXIST
        if embed is not None:
            payload["embed"] = embed

        if content is not None:
            payload["content"] = content

        payload.update(kwargs)

        try:
            # PREFIX COMMANDS
            if self.ctx:
                return await self.ctx.send(**payload)

            # SLASH COMMANDS
            if self.interaction:
                if self.interaction.response.is_done():
                    return await self.interaction.followup.send(**payload)
                return await self.interaction.response.send_message(**payload)

            # MANUAL CHANNEL SEND
            if self.channel:
                return await self.channel.send(**payload)

        except Exception as e:
            # LAST-RESORT FALLBACK
            try:
                error_text = f"Response Error: {e}"
                if self.ctx:
                    return await self.ctx.send(error_text)
                if self.channel:
                    return await self.channel.send(error_text)

            except Exception:
                return None

    # GENERIC SEND
    async def send(self,
                   title: str | None = None,
                   description: str | None = None,
                   *,
                   level: str = "INFO",
                   fields=None,
                   footer: str | None = None,
                   content: str | None = None,
                   embed: discord.Embed | None = None,
                   **kwargs):
        try:
            # AUTO BUILD EMBED
            if embed is None and (title is not None
                                  or description is not None):
                embed = make_embed(title=title or "Response",
                                   description=description,
                                   level=level,
                                   fields=fields,
                                   footer=footer,
                                   **kwargs)

        except Exception as e:
            # EMBED FAILURE FALLBACK
            content = (content or (f"{title or ''}\n"
                                   f"{description or ''}\n\n"
                                   f"Error: {e}"))

            embed = None
        return await self._dispatch(embed=embed, content=content)

    # SUCCESS
    async def success(self,
                      title: str,
                      description: str | None = None,
                      **kwargs):
        return await self.send(title=title,
                               description=description,
                               level="SUCCESS",
                               **kwargs)

    # ERROR
    async def error(self,
                    title: str,
                    description: str | None = None,
                    **kwargs):
        return await self.send(title=title,
                               description=description,
                               level="ERROR",
                               **kwargs)

    # WARNING
    async def warning(self,
                      title: str,
                      description: str | None = None,
                      **kwargs):
        return await self.send(title=title,
                               description=description,
                               level="WARNING",
                               **kwargs)

    # INFO
    async def info(self, title: str, description: str | None = None, **kwargs):
        return await self.send(title=title,
                               description=description,
                               level="INFO",
                               **kwargs)

    # LOADING
    async def loading(self,
                      title: str = "Loading...",
                      description: str | None = None,
                      **kwargs):

        return await self.send(title=title,
                               description=description,
                               level="INFO",
                               **kwargs)

    # RAW MESSAGE
    async def raw(self, content: str, **kwargs):
        return await self._dispatch(content=content, **kwargs)
