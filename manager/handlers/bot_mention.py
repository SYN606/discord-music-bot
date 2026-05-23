import time
import discord
from discord.ext import commands
from config.embeds import make_embed
from config.emojis import EMOJIS
from config.prefix import PREFIX


class BotMention(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        # User cooldown cache
        self.cooldowns = {}
        # Cooldown duration
        self.cooldown_time = 15

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        # Ignore bots
        if message.author.bot:
            return

        # Ignore DMs
        if not message.guild:
            return

        # Trigger only on pure mention
        if message.content.strip() not in (f"<@{self.bot.user.id}>",
                                           f"<@!{self.bot.user.id}>"):
            return

        # Cooldown system
        now = time.time()
        last_used = self.cooldowns.get(message.author.id, 0)
        if now - last_used < self.cooldown_time:
            return

        self.cooldowns[message.author.id] = now
        embed = make_embed(
            title="DV-Music",
            description=(
                f"{EMOJIS['music']} "
                f"High quality Discord music experience\n\n"
                f"{EMOJIS['arrow_point']} "
                f"Prefix: `{PREFIX}`\n"
                f"{EMOJIS['message']} "
                f"Use `{PREFIX}help` "
                f"to view all commands\n\n"
                f"{EMOJIS['green_dot']} "
                f"Features:\n"
                f"> 24/7 Music Playback\n"
                f"> Fast & Stable Streaming\n"
                f"> Queue Management\n"
                f"> Playlist Support\n"
                f"> Crystal Clear Audio\n"
                f"> Multi-Server Music System\n"
                f"> Slash Command Support\n\n"
                f"{EMOJIS['music']} "
                f"Now playing the best vibes.\n\n"
                f"{EMOJIS['developer']} "
                f"Developed with ❤️ for music lovers by `You Know Who`"),
            level="INFO",
            footer=(f"Requested by {message.author}"),
        )

        await message.reply(embed=embed, mention_author=False)


async def setup(bot):
    await bot.add_cog(BotMention(bot))
