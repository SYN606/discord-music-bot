from __future__ import annotations
import discord
from discord.ext import commands
from config.emojis import EMOJIS
from manager.basic_check import BasicChecks
from manager.handlers.player_manager import PlayerManager
from manager.handlers.queue_manager import QueueManager
from utils.respond import Respond


class Remove(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cleanup(self, ctx: commands.Context):
        try:
            await ctx.message.delete()
        except Exception:
            pass

    @commands.hybrid_command(
        name="remove",
        aliases=["rm"],
        description="Remove a track from queue using its index.")
    async def remove(self, ctx: commands.Context, index: int):
        await self.cleanup(ctx)
        response = Respond(ctx=ctx)
        player = await BasicChecks.same_voice_channel(ctx)
        if not player:
            return
        if player.queue.is_empty:
            return await response.warning("Empty Queue",
                                          "There are no queued tracks.")
        queue_list = list(player.queue)
        if (index < 1 or index > len(queue_list)):
            return await response.warning(
                "Invalid Index", "That queue position does not exist.")
        removed = QueueManager.remove_index(player, index)
        if not removed:
            return await response.error("Removal Failed",
                                        "Failed to remove track from queue.")
        embed = discord.Embed(color=0x5865F2)
        duration = PlayerManager.format_time(removed.length)
        embed.description = (f"{EMOJIS['fail']} "
                             f"**Removed From Queue**\n\n"
                             f"`#{index}` "
                             f"{removed.title[:45]}\n\n"
                             f"{EMOJIS['waveform']} "
                             f"`{removed.author[:28]}`\n\n"
                             f"{EMOJIS['play']} "
                             f"`{duration}`")
        artwork = getattr(removed, "artwork", None)
        if artwork:
            embed.set_thumbnail(url=artwork)
        embed.set_footer(text=(f"{self.bot.user.name} • "
                               f"Bajao Queue System"))
        await response.send(embed=embed)

    @remove.error
    async def remove_error(self, ctx: commands.Context,
                           error: commands.CommandError):
        response = Respond(ctx=ctx)
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['queue']} "
                                 f"**Remove Track**\n\n"
                                 f"{EMOJIS['warning']} "
                                 f"You must provide a queue index.\n\n"
                                 f"{EMOJIS['arrow_point']} "
                                 f"`bajao remove 2`\n"
                                 f"{EMOJIS['arrow_point']} "
                                 f"`bajao rm 5`")
            return await response.send(embed=embed)
        if isinstance(error, commands.BadArgument):
            return await response.warning("Invalid Index",
                                          "Queue index must be a number.")
        return await response.error("Command Error", str(error))


async def setup(bot):
    await bot.add_cog(Remove(bot))
