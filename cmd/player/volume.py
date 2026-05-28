from __future__ import annotations
import discord
from discord.ext import commands
from config.emojis import EMOJIS
from manager.basic_check import BasicChecks
from ui.views.volume_views import VolumeControls
from utils.respond import Respond


class Volume(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cleanup(self, ctx: commands.Context):
        try:
            await ctx.message.delete()
        except Exception:
            pass

    def volume_bar(self, volume: int) -> str:
        filled = volume // 10
        return ("▬" * filled + "▭" * (10 - filled))

    @commands.hybrid_command(name="volume",
                             aliases=["vol"],
                             description="Control music volume.")
    async def volume(self, ctx: commands.Context, volume: int | None = None):
        await self.cleanup(ctx)
        response = Respond(ctx=ctx)
        player = await BasicChecks.player_playing(ctx)
        if not player:
            return
        if volume is None:
            current = player.volume
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['volume']} "
                                 f"**Bajao Audio Mixer**\n\n"
                                 f"`{self.volume_bar(current)}`\n\n"
                                 f"### `{current}%`\n\n"
                                 f"{EMOJIS['waveform']} "
                                 f"Live playback gain controller")
            embed.set_footer(text="Interactive Volume Controls")
            view = VolumeControls(player=player, author_id=ctx.author.id)
            message = await response.send(embed=embed, view=view)
            if isinstance(message, discord.Message):
                view.message = message
            return
        volume = max(0, min(volume, 100))
        await player.set_volume(volume)
        embed = discord.Embed(color=0x5865F2)
        embed.description = (f"{EMOJIS['volume']} "
                             f"**Volume Updated**\n\n"
                             f"`{self.volume_bar(volume)}`\n\n"
                             f"### `{volume}%`")
        embed.set_footer(text="Bajao Audio System")
        await response.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Volume(bot))
