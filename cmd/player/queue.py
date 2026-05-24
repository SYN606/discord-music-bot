from __future__ import annotations

import discord
from discord.ext import commands

from config.emojis import EMOJIS
from manager.handlers.player_manager import PlayerManager
from ui.views.queue_paginator import QueuePaginator
from utils.respond import Respond


class Queue(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cleanup(self, ctx: commands.Context):
        try:
            await ctx.message.delete()
        except Exception:
            pass

    @commands.hybrid_command(name="queue",
                             aliases=["q"],
                             description="View the current music queue.")
    async def queue(self, ctx: commands.Context):
        await self.cleanup(ctx)
        response = Respond(ctx=ctx)
        player = await PlayerManager.validate_player(ctx)
        if not player:
            return
        if player.queue.is_empty:
            current = player.current
            if current:
                embed = PlayerManager.build_now_playing(player, current)
                embed.description = ((embed.description or "") + "\n\n" +
                                     (f"{EMOJIS['warning']} "
                                      f"No upcoming tracks queued."))

                return await response.send(embed=embed)
            return await response.warning("Empty Queue",
                                          "There are no queued tracks.")

        view = QueuePaginator(player=player, author_id=ctx.author.id)
        embed = view.build_embed()
        message = await response.send(embed=embed, view=view)
        if message:
            view.message = message  # type: ignore


async def setup(bot):
    await bot.add_cog(Queue(bot))
