from __future__ import annotations
import discord
from discord.ext import commands
from config.emojis import EMOJIS
from config.prefix import PREFIX
from utils.respond import Respond


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # CLEANUP
    async def cleanup(self, ctx: commands.Context):

        try:
            await ctx.message.delete()
        except Exception:
            pass

    # HELP
    @commands.hybrid_command(name="help",
                             aliases=["h"],
                             description="Show bot commands.")
    async def help(self, ctx: commands.Context):

        await self.cleanup(ctx)
        response = Respond(ctx=ctx)
        embed = discord.Embed(color=0x5865F2)

        embed.description = (f"{EMOJIS['music_player']} "
                             f"**Bajao Help Menu**\n\n"
                             f"{EMOJIS['waveform']} "
                             f"Modern Discord Music Experience\n\n"
                             f"## {EMOJIS['queue']} Playback\n\n"
                             f"{EMOJIS['play']} "
                             f"`{PREFIX} play <song>`\n"
                             f"> Play music or playlists\n\n"
                             f"{EMOJIS['pause']} "
                             f"`{PREFIX} pause`\n"
                             f"> Pause current playback\n\n"
                             f"{EMOJIS['play']} "
                             f"`{PREFIX} resume`\n"
                             f"> Resume paused playback\n\n"
                             f"{EMOJIS['skip']} "
                             f"`{PREFIX} skip`\n"
                             f"> Skip current track\n\n"
                             f"{EMOJIS['stop']} "
                             f"`{PREFIX} stop`\n"
                             f"> Stop playback completely\n\n"
                             f"{EMOJIS['queue']} "
                             f"`{PREFIX} queue`\n"
                             f"> View queued tracks\n\n"
                             f"{EMOJIS['fail']} "
                             f"`{PREFIX} remove <index>`\n"
                             f"> Remove track from queue\n\n"
                             f"{EMOJIS['volume']} "
                             f"`{PREFIX} volume`\n"
                             f"> Open volume controller\n\n"
                             f"{EMOJIS['volume']} "
                             f"`{PREFIX} volume <1-100>`\n"
                             f"> Set player volume\n\n"
                             f"## {EMOJIS['music_player']} Voice\n\n"
                             f"{EMOJIS['music']} "
                             f"`{PREFIX} join`\n"
                             f"> Connect bot to your VC\n\n"
                             f"{EMOJIS['leave']} "
                             f"`{PREFIX} leave`\n"
                             f"> Disconnect the bot\n\n"
                             f"## {EMOJIS['developer']} Examples\n\n"
                             f"{EMOJIS['arrow_point']} "
                             f"`{PREFIX} play perfect ed sheeran`\n\n"
                             f"{EMOJIS['arrow_point']} "
                             f"`{PREFIX} play industry baby`\n\n"
                             f"{EMOJIS['arrow_point']} "
                             f"`{PREFIX} play https://youtu.be/...`\n\n"
                             f"{EMOJIS['arrow_point']} "
                             f"`{PREFIX} volume 70`\n\n"
                             f"{EMOJIS['arrow_point']} "
                             f"`{PREFIX} remove 3`")

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed.set_footer(text=(f"{self.bot.user.name} • "
                               f"Bajao Music System"))

        await response.send(embed=embed)


async def setup(bot):

    await bot.add_cog(Help(bot))
