import os
import logging
import traceback

import discord
from discord.ext import commands

from config import settings
from config.prefix import dynamic_prefix, normalize

from database.init import init_db


# Validate settings
try:
    settings.validate()

    TOKEN = settings.TOKEN
    SYNC_COMMANDS = settings.SYNC_COMMANDS

except Exception as e:
    print("\n[CONFIG ERROR]")
    print(f"→ {e}")
    print("\nFix your .env file and restart.\n")
    raise SystemExit(1)


# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger("imposter")


def log(message: str):
    logger.info(message)


def log_error(message: str):
    logger.error(message)


# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True


# Bot
class ImposterBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=dynamic_prefix,
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self):

        # Initialize database
        try:
            await init_db()

            log("✓ Database initialized")
        except Exception as e:
            log_error(f"Database initialization failed → {e}")
            if settings.is_dev():
                traceback.print_exc()
        # Load extensions
        await self.load_extensions()
        # Sync slash commands
        if SYNC_COMMANDS:
            try:
                await self.tree.sync()
                log("✓ Slash commands synced")

            except Exception as e:
                log_error(f"Slash command sync failed → {e}")
                if settings.is_dev():
                    traceback.print_exc()

    async def load_extensions(self):
        folders = (
            "cmd",
            "manager.handlers",
            "manager.startups",
        )
        for base in folders:
            path = base.replace(".", os.sep)
            if not os.path.isdir(path):
                log(f"Missing folder: {path}")
                continue
            for root, _, files in os.walk(path):
                for file in files:
                    if not file.endswith(".py"):
                        continue
                    if file.startswith("__"):
                        continue
                    module = (
                        os.path.join(root, file)
                        .replace("\\", ".")
                        .replace("/", ".")
                        .replace(".py", "")
                    )
                    try:
                        log(f"Loading: {module}")
                        await self.load_extension(module)
                        log(f"✓ Loaded {module}")

                    except Exception as e:
                        log_error(f"✗ Failed {module} → {e}")
                        if settings.is_dev():
                            traceback.print_exc()

    async def on_ready(self):
        log(
            f"\nLogged in as {self.user} ({self.user.id})"  # type: ignore
        )
        log("Imposter is ready\n")
        print("=== COMMANDS LOADED ===")
        for command in self.commands:
            print(f"- {command.name}")

    async def on_message(self, message: discord.Message):
        # Ignore bots and DMs
        if message.author.bot or not message.guild:
            return
        # Normalize prefixes
        try:
            message.content = normalize(message.content)
        except Exception as e:
            log_error(f"[NORMALIZE ERROR] {e}")
            if settings.is_dev():
                traceback.print_exc()
        await self.process_commands(message)

    # Global command error handler
    async def on_command_error(
        self,
        ctx: commands.Context,
        error: Exception,
    ):
        log_error(f"[COMMAND ERROR] {error}")
        if settings.is_dev():
            traceback.print_exc()
        try:
            await ctx.send(f"⚠️ {error}")
        except Exception:
            pass


# Entrypoint
def main():
    bot = ImposterBot()
    try:
        log("Starting bot...\n")
        bot.run(TOKEN)  # type: ignore

    except discord.errors.PrivilegedIntentsRequired:
        print("\n[INTENTS ERROR]")
        print("Enable these in Developer Portal:")
        print("- MESSAGE CONTENT INTENT")
        print("- SERVER MEMBERS INTENT\n")

    except KeyboardInterrupt:
        log("Shutting down gracefully...")
        try:
            if bot.loop and not bot.loop.is_closed():
                bot.loop.run_until_complete(bot.close())

        except Exception:
            pass
    except Exception as e:
        log_error(f"Bot crashed → {e}")
        if settings.is_dev():
            traceback.print_exc()


if __name__ == "__main__":
    main()
