from __future__ import annotations
import discord
from discord.ext import commands
from config.emojis import EMOJIS
from manager.handlers.player_manager import PlayerManager
from manager.handlers.queue_manager import QueueManager
from utils.respond import Respond


class Remove(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    # REMOVE TRACK
    @commands.hybrid_command(
        name="remove",
        aliases=["rm"],
        description="Remove a track from queue using its index.")
    async def remove(self, ctx: commands.Context, index: int):
        response = Respond(ctx=ctx)

        # VALIDATE PLAYER
        player = await PlayerManager.validate_player(ctx)
        if not player:
            return

        # EMPTY QUEUE
        if player.queue.is_empty:
            return await response.warning("Empty Queue",
                                          "There are no queued tracks.")
        queue_list = list(player.queue)

        # INVALID INDEX
        if index < 1 or index > len(queue_list):
            return await response.warning(
                "Invalid Index", "That queue position does not exist.")

        # TARGET TRACK
        track = queue_list[index - 1]
        removed = QueueManager.remove_track(player, track) # type: ignore

        if not removed:

            return await response.error("Removal Failed",
                                        "Failed to remove track from queue.")
        embed = discord.Embed(color=0x5865F2)
        embed.description = (f"{EMOJIS['fail']} "
                             f"**Track Removed**\n\n"
                             f"`#{index}` "
                             f"{track.title}\n\n"
                             f"{EMOJIS['waveform']} "
                             f"`{track.author}`")

        artwork = getattr(track, "artwork", None)
        if artwork:
            embed.set_thumbnail(url=artwork)

        embed.set_footer(text="DV-Music Queue Manager")
        await response.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Remove(bot))
