import random

import discord
from discord.ext import commands, tasks


class Presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.activities = [

            # Playing
            discord.Game(name="high quality audio"),
            discord.Game(name="music across servers"),
            discord.Game(name="beats 24/7"),
            discord.Game(name="your favorite tracks"),

            # Watching
            discord.Activity(
                type=discord.ActivityType.watching,
                name="active voice channels",
            ),
            discord.Activity(
                type=discord.ActivityType.watching,
                name="music queues grow",
            ),
            discord.Activity(
                type=discord.ActivityType.watching,
                name="listeners vibe together",
            ),

            # Listening
            discord.Activity(
                type=discord.ActivityType.listening,
                name="lofi & chill beats",
            ),
            discord.Activity(
                type=discord.ActivityType.listening,
                name="community playlists",
            ),
            discord.Activity(
                type=discord.ActivityType.listening,
                name="songs requested by users",
            ),

            # Custom Status
            discord.CustomActivity(name="🎵 Powered by DV-Music"),
            discord.CustomActivity(name="🎶 Streaming nonstop audio"),
            discord.CustomActivity(name="🎧 Your music companion"),
            discord.CustomActivity(name="🔊 Crystal clear playback"),
            discord.CustomActivity(name="📻 Now serving premium vibes"),
            discord.CustomActivity(name="🎼 Music without limits"),
        ]

    async def cog_load(self):

        self.rotate_presence.start()

    async def cog_unload(self):

        self.rotate_presence.cancel()

    # Rotate every hour
    @tasks.loop(hours=1)
    async def rotate_presence(self):

        if not self.bot.is_ready():
            return

        try:
            await self.bot.change_presence(
                status=discord.Status.online,
                activity=random.choice(self.activities),
            )

        except Exception:
            pass

    @rotate_presence.before_loop
    async def before_rotate_presence(self):

        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Presence(bot))