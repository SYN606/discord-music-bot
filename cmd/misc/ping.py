import time
from datetime import datetime

import psutil
from discord.ext import commands

from config.embeds import make_embed
from config.emojis import EMOJIS
from utils.respond import Respond


class Ping(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.utcnow()

    # LATENCY STATUS
    def get_ping_status(self, ping: float):

        if ping < 100:
            return EMOJIS["signal_green"]

        if ping < 200:
            return EMOJIS["signal_yellow"]

        if ping < 400:
            return EMOJIS["signal_orange"]

        return EMOJIS["signal_red"]

    # UPTIME
    def get_uptime(self):

        delta = (datetime.utcnow() - self.start_time)

        hours, remainder = divmod(delta.seconds, 3600)

        minutes, seconds = divmod(remainder, 60)

        if delta.days:

            return (f"{delta.days}d "
                    f"{hours}h")

        if hours:

            return (f"{hours}h "
                    f"{minutes}m")

        return (f"{minutes}m "
                f"{seconds}s")

    # PING
    @commands.hybrid_command(name="ping", description="Display bot latency.")
    async def ping(self, ctx: commands.Context):

        response = Respond(ctx=ctx)

        start = time.perf_counter()

        loading = await response.raw(f"{EMOJIS['rounded_loading']} "
                                     f"Checking Bajao status...")

        end = time.perf_counter()

        # LATENCIES
        api_latency = round(self.bot.latency * 1000, 2)

        message_latency = round((end - start) * 1000, 2)

        # SYSTEM
        ram_usage = round(psutil.virtual_memory().percent, 1)

        # STATUS
        signal = self.get_ping_status(api_latency)

        # EMBED
        embed = make_embed(
            title=(f"{EMOJIS['music_player']} "
                   f"Bajao"),
            description=(f"{signal} "
                         f"`{api_latency}ms` "
                         f"API Latency"),
            level="INFO",
            fields=[
                ("Message", f"{EMOJIS['message']} "
                 f"`{message_latency}ms`", True),
                ("Uptime", f"{EMOJIS['waveform']} "
                 f"`{self.get_uptime()}`", True),
                ("Memory", f"{EMOJIS['volume']} "
                 f"`{ram_usage}%`", True),
                ("Servers", f"{EMOJIS['music']} "
                 f"`{len(self.bot.guilds)}`", True),
            ],
            footer=(f"{self.bot.user.name} • "
                    f"Bajao Music System"),
        )

        if loading:

            await loading.edit(content=None, embed=embed)  # type: ignore

        else:

            await response.send(embed=embed)


async def setup(bot):

    await bot.add_cog(Ping(bot))
