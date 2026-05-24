from __future__ import annotations
import discord
from discord.ext import commands
from config.emojis import EMOJIS
from manager.handlers.player_manager import PlayerManager
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
        return ("▰" * filled + "▱" * (10 - filled))

    @commands.hybrid_command(name="volume",
                             aliases=["vol"],
                             description="Control music volume.")
    async def volume(self, ctx: commands.Context, volume: int | None = None):
        await self.cleanup(ctx)
        response = Respond(ctx=ctx)
        player = await PlayerManager.validate_player(ctx)
        if not player:
            return
        if volume is None:
            current = player.volume
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['volume']} "
                                 f"**Bajao Volume Controller**\n\n"
                                 f"## `{current}%`\n"
                                 f"`{self.volume_bar(current)}`\n\n"
                                 f"{EMOJIS['waveform']} "
                                 f"Adjust playback volume\n"
                                 f"using the controls below.")

            embed.set_footer(text="Volume changes by 2%")
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
                             f"## `{volume}%`\n"
                             f"`{self.volume_bar(volume)}`")

        embed.set_footer(text="Bajao Audio System")
        await response.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Volume(bot))
