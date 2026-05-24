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
        # EMBED
        if embed is not None:
            payload["embed"] = embed
        # CONTENT
        if content is not None:
            payload["content"] = content
        # EXTRA KWARGS
        payload.update(kwargs)

        try:
            # PREFIX COMMAND
            if self.ctx:
                return await self.ctx.send(**payload)

            # INTERACTION
            if self.interaction:
                if self.interaction.response.is_done():
                    return await self.interaction.followup.send(**payload)
                # INITIAL RESPONSE
                await self.interaction.response.send_message(**payload)

                try:
                    return await self.interaction.original_response()
                except Exception:
                    return None

            # CHANNEL SEND
            if self.channel:
                return await self.channel.send(**payload)

        except Exception as e:

            # LAST RESORT FALLBACK
            try:
                error_text = (f"Response Error: {e}")
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
            if (embed is None
                    and (title is not None or description is not None)):
                embed = make_embed(title=title or "Response",
                                   description=description,
                                   level=level,
                                   fields=fields,
                                   footer=footer)

        except Exception as e:
            content = (content or (f"{title or ''}\n"
                                   f"{description or ''}\n\n"
                                   f"Error: {e}"))

            embed = None
        return await self._dispatch(embed=embed, content=content, **kwargs)

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
                               level="MUSIC",
                               **kwargs)

    # RAW
    async def raw(self, content: str, **kwargs):
        return await self._dispatch(content=content, **kwargs)

    async def edit(self,
                   message: discord.Message,
                   *,
                   embed: discord.Embed | None = None,
                   content: str | None = None,
                   view=None):

        try:
            payload = {}
            if embed is not None:
                payload["embed"] = embed
            if content is not None:
                payload["content"] = content
            if view is not None:
                payload["view"] = view
            return await message.edit(**payload)

        except Exception:
            return None
