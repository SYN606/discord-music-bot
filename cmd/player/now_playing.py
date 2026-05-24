from __future__ import annotations
import discord
from discord.ext import commands
from config.emojis import EMOJIS
from manager.handlers.player_manager import PlayerManager
from ui.views.player_views import PlayerControls
from utils.respond import Respond


class NowPlaying(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # CLEANUP
    async def cleanup(self, ctx: commands.Context):

        try:
            await ctx.message.delete()
        except Exception:
            pass

    # NOW PLAYING
    @commands.hybrid_command(name="nowplaying",
                             aliases=["np", "current"],
                             description="Show the current playing track.")
    async def nowplaying(self, ctx: commands.Context):
        await self.cleanup(ctx)

        response = Respond(ctx=ctx)
        # VALIDATE PLAYER
        player = await PlayerManager.validate_player(ctx)
        if not player:
            return

        # CURRENT TRACK
        track = player.current

        if not track:
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['warning']} "
                                 f"No active track is currently playing.")
            return await response.send(embed=embed)

        # BUILD PLAYER EMBED
        embed = PlayerManager.build_now_playing(player, track)

        # EXTRA NOW PLAYING INFO
        queue_count = player.queue.count
        requester = (
            f"<@{track.extras.requester}>" if hasattr(track, "extras")
            and getattr(track.extras, "requester", None) else "Unknown")

        embed.description = ((embed.description or "") + "\n\n" +
                             (f"{EMOJIS['queue']} "
                              f"`{queue_count}` queued "
                              f"• "
                              f"{EMOJIS['volume']} "
                              f"`{player.volume}%`\n\n"
                              f"{EMOJIS['developer']} "
                              f"{requester}"))

        # CONTROLS
        view = PlayerControls()
        await response.send(embed=embed, view=view)

    # ERROR HANDLER
    @nowplaying.error
    async def nowplaying_error(self, ctx: commands.Context,
                               error: commands.CommandError):

        response = Respond(ctx=ctx)
        embed = discord.Embed(color=0x5865F2)
        embed.description = (f"{EMOJIS['warning']} "
                             f"Failed to fetch player information.\n\n"
                             f"`{str(error)[:120]}`")

        await response.send(embed=embed)


async def setup(bot):

    await bot.add_cog(NowPlaying(bot))
