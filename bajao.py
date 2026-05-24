from __future__ import annotations
import logging
import os
import traceback
import discord
import wavelink
from discord.ext import commands
from config import settings
from config.emojis import EMOJIS
from config.lavalink import connect_lavalink
from config.prefix import dynamic_prefix, normalize
from database.init import init_db

try:

    settings.validate()
    TOKEN = settings.TOKEN
    SYNC_COMMANDS = settings.SYNC_COMMANDS

except Exception as e:
    print("\n[CONFIG ERROR]")
    print(f"→ {e}")
    print("\nFix your .env file and restart.\n")
    raise SystemExit(1)

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logging.getLogger("wavelink").setLevel(logging.WARNING)
logging.getLogger("websockets").setLevel(logging.WARNING)
logging.getLogger("discord.voice_state").setLevel(logging.ERROR)
logging.getLogger("aiohttp.access").setLevel(logging.WARNING)
logger = logging.getLogger("bajao")


def log(message: str):
    logger.info(message)


def log_error(message: str):
    logger.error(message)


# INTENTS
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True


# BOT
class Bajao(commands.Bot):

    def __init__(self):

        super().__init__(command_prefix=dynamic_prefix,
                         intents=intents,
                         help_command=None)

    async def setup_hook(self):
        try:
            await init_db()  # type: ignore
            log("✓ Database initialized")

        except Exception as e:
            log_error(f"Database initialization failed → {e}")
            if settings.is_dev():
                traceback.print_exc()

        # LAVALINK
        try:
            await connect_lavalink(self)
            log("✓ Lavalink initialized")

        except Exception as e:
            log_error(f"Lavalink initialization failed → {e}")
            if settings.is_dev():
                traceback.print_exc()
        await self.load_extensions()
        if SYNC_COMMANDS:
            try:
                await self.tree.sync()
                log("✓ Slash commands synced")
            except Exception as e:
                log_error(f"Slash command sync failed → {e}")
                if settings.is_dev():
                    traceback.print_exc()

    # LOAD EXTENSIONS
    async def load_extensions(self):
        folders = ("cmd", "manager.startups")

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
                    module = (os.path.join(root,
                                           file).replace("\\", ".").replace(
                                               "/", ".").replace(".py", ""))

                    try:

                        log(f"Loading: {module}")
                        await self.load_extension(module)
                        log(f"✓ Loaded {module}")

                    except Exception as e:
                        log_error(f"✗ Failed {module} → {e}")
                        if settings.is_dev():
                            traceback.print_exc()

    # READY
    async def on_ready(self):
        print()
        log(f"Logged in as "
            f"{self.user} "
            f"({self.user.id})"  # type: ignore
            )
        log("Bajao is ready")

        # LAVALINK STATUS
        try:
            nodes = wavelink.Pool.nodes

            if nodes:
                log(f"✓ Lavalink connected "
                    f"({len(nodes)} node active)")

            else:
                log_error("✗ No Lavalink nodes connected")
        except Exception:
            pass

        # COMMANDS
        print("\n=== COMMANDS LOADED ===")
        for command in self.commands:
            print(f"- {command.name}")
        print()

    # MESSAGE HANDLER
    async def on_message(self, message: discord.Message):
        if (message.author.bot or not message.guild):
            return
        try:
            message.content = normalize(message.content)

        except Exception:
            if settings.is_dev():
                traceback.print_exc()
        await self.process_commands(message)

    # GLOBAL COMMAND ERROR
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        # IGNORE LOCAL HANDLERS
        if (ctx.command and ctx.command.has_error_handler()):
            return
        # IGNORE COG HANDLERS
        cog = ctx.cog

        if (cog and cog.has_error_handler()):
            return
        # IGNORE UNKNOWN COMMANDS
        if isinstance(error, commands.CommandNotFound):
            return
        log_error(f"[COMMAND ERROR] {error}")

        if settings.is_dev():
            traceback.print_exc()

        embed = discord.Embed(color=0x5865F2)
        embed.description = (f"{EMOJIS['warning']} "
                             f"Something went wrong.\n\n"
                             f"`{str(error)[:150]}`")

        try:
            await ctx.send(embed=embed, delete_after=10)
        except Exception:
            pass

    # NODE READY
    async def on_wavelink_node_ready(self,
                                     payload: wavelink.NodeReadyEventPayload):
        log(f"✓ Lavalink node ready → "
            f"{payload.node.identifier}")


# ENTRYPOINT
def main():
    bot = Bajao()

    try:
        log("Starting Bajao...")
        bot.run(TOKEN)  # type: ignore

    except discord.errors.PrivilegedIntentsRequired:
        print("\n[INTENTS ERROR]")
        print("Enable these in "
              "Developer Portal:")
        print("- MESSAGE CONTENT INTENT")
        print("- SERVER MEMBERS INTENT")
        print("- VOICE STATE INTENT\n")

    except KeyboardInterrupt:
        log("Shutting down gracefully...")

        try:
            if (bot.loop and not bot.loop.is_closed()):
                bot.loop.run_until_complete(bot.close())
        except Exception:
            pass

    except Exception as e:
        log_error(f"Bot crashed → {e}")
        if settings.is_dev():
            traceback.print_exc()


if __name__ == "__main__":

    main()
