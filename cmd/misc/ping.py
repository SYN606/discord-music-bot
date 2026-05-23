import platform
import time
from datetime import datetime
import psutil
from discord.ext import commands
from config.emojis import EMOJIS
from config.embeds import make_embed
from utils.respond import Respond


class Ping(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.utcnow()

    # LATENCY STATUS
    def get_ping_status(self, ping: float):

        if ping < 100:
            return (EMOJIS["signal_green"], "Excellent")

        if ping < 200:
            return (EMOJIS["signal_yellow"], "Good")

        if ping < 400:
            return (EMOJIS["signal_orange"], "Average")

        return (EMOJIS["signal_red"], "Poor")

    # FORMAT UPTIME
    def get_uptime(self):
        delta = datetime.utcnow() - self.start_time
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)

        minutes, seconds = divmod(remainder, 60)
        parts = []
        if days:
            parts.append(f"{days}d")

        if hours:
            parts.append(f"{hours}h")

        if minutes:
            parts.append(f"{minutes}m")

        parts.append(f"{seconds}s")
        return " ".join(parts)

    @commands.hybrid_command(
        name="ping", description="Display bot latency and system statistics.")
    async def ping(self, ctx: commands.Context):

        response = Respond(ctx=ctx)
        start = time.perf_counter()
        loading = await response.raw(f"{EMOJIS['rounded_loading']} "
                                     f"Checking DV-Music status...")

        end = time.perf_counter()

        # LATENCIES
        api_latency = round(self.bot.latency * 1000, 2)
        message_latency = round((end - start) * 1000, 2)

        # SYSTEM
        cpu_usage = round(psutil.cpu_percent(), 1)
        ram_usage = round(psutil.virtual_memory().percent, 1)

        # STATUS
        status_emoji, status_text = self.get_ping_status(api_latency)

        # GUILD DATA
        guild_count = len(self.bot.guilds)
        user_count = sum(guild.member_count or 0 for guild in self.bot.guilds)
        shard_id = (ctx.guild.shard_id if ctx.guild else 0)

        # BUILD EMBED
        embed = make_embed(
            title="DV-Music Status",
            description=(f"{status_emoji} "
                         f"Current network quality: "
                         f"**{status_text}**"),
            level="INFO",
            fields=[
                ("API Latency", f"`{api_latency}ms`", True),
                ("Message Latency", f"`{message_latency}ms`", True),
                ("CPU Usage", f"`{cpu_usage}%`", True),
                ("RAM Usage", f"`{ram_usage}%`", True),
                ("Uptime", f"`{self.get_uptime()}`", True),
                ("Python", f"`{platform.python_version()}`", True),
                ("Servers", f"`{guild_count}`", True),
                ("Users", f"`{user_count}`", True),
                ("Shard", f"`{shard_id}`", True),
            ],
            footer=(f"{self.bot.user.name} • "
                    f"Music System Operational"),
        )

        # EDIT LOADING MESSAGE
        if loading:
            await loading.edit(content=None, embed=embed)  # type: ignore

        # FALLBACK
        else:
            await response.send(embed=embed, )


async def setup(bot):
    await bot.add_cog(Ping(bot))
