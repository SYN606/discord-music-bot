from __future__ import annotations
import asyncio
from typing import cast
import discord
import wavelink
from discord.ext import commands
from config.emojis import EMOJIS
from utils.respond import Respond


class Status(commands.Cog):

    def __init__(self, bot):

        self.bot = bot
        self.inactive_tasks: dict[int, asyncio.Task] = {}

    async def cleanup(self, ctx: commands.Context):
        try:
            await ctx.message.delete()
        except Exception:
            pass

    # GET PLAYER
    def get_player(self, ctx: commands.Context) -> wavelink.Player | None:
        return cast(wavelink.Player | None, ctx.voice_client)

    # JOIN VC
    @commands.hybrid_command(name="join",
                             aliases=["summon"],
                             description="Join your voice channel.")
    async def join(self, ctx: commands.Context):

        await self.cleanup(ctx)
        response = Respond(ctx=ctx)
        member = cast(discord.Member, ctx.author)
        if not member.voice:
            return await response.warning(
                "Voice Channel Required",
                "You must join a voice channel first.")

        channel = member.voice.channel
        if channel is None:
            return await response.warning(
                "Voice Channel Required",
                "You must join a voice channel first.")
        player = self.get_player(ctx)

        # ALREADY CONNECTED
        if player:
            if (player.channel and player.channel.id == channel.id):
                return await response.warning(
                    "Already Connected",
                    "I'm already connected to your voice channel.")

            await player.move_to(channel)
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['music_player']} "
                                 f"**Voice Channel Updated**\n\n"
                                 f"{EMOJIS['waveform']} "
                                 f"Moved to {channel.mention}")

            embed.set_footer(text="Bajao Music System")
            return await response.send(embed=embed)

        # CONNECT
        player = await channel.connect(cls=wavelink.Player, self_deaf=True)

        # STORE HOME CHANNEL
        player.home = ctx.channel  # type: ignore
        embed = discord.Embed(color=0x5865F2)
        embed.description = (f"{EMOJIS['music_player']} "
                             f"**Connected**\n\n"
                             f"{EMOJIS['waveform']} "
                             f"Joined {channel.mention}\n\n"
                             f"{EMOJIS['queue']} "
                             f"Ready to play music")

        embed.set_footer(text="Bajao Music System")
        await response.send(embed=embed)

    # LEAVE VC
    @commands.hybrid_command(name="leave",
                             aliases=["dc", "disconnect"],
                             description="Disconnect from voice channel.")
    async def leave(self, ctx: commands.Context):

        await self.cleanup(ctx)
        response = Respond(ctx=ctx)
        player = self.get_player(ctx)

        if not player:
            return await response.warning(
                "Not Connected", "I'm not connected to a voice channel.")
        try:

            player.queue.clear()

        except Exception:
            pass

        text_channel = (
            player.home  # type: ignore
            if hasattr(player, "home") else ctx.channel)
        await player.disconnect()

        # LEAVE EMBED
        embed = discord.Embed(color=0x5865F2)
        embed.description = (f"{EMOJIS['leave']} "
                             f"**Disconnected**\n\n"
                             f"{EMOJIS['waveform']} "
                             f"Playback session ended")

        embed.set_footer(text="Thanks for using Bajao")
        await response.send(embed=embed)

        # THANK YOU EMBED
        try:

            thank_embed = discord.Embed(color=0x5865F2)
            thank_embed.description = (f"{EMOJIS['heart']} "
                                       f"**Thanks For Listening**\n\n"
                                       f"{EMOJIS['music_player']} "
                                       f"Hope you enjoyed your session.\n\n"
                                       f"{EMOJIS['waveform']} "
                                       f"See you again soon.")

            thank_embed.set_footer(text="Bajao • Developed by SYN606")
            await text_channel.send(embed=thank_embed)

        except Exception:
            pass

    # INACTIVITY TIMER
    async def inactivity_disconnect(self, guild_id: int,
                                    player: wavelink.Player):

        await asyncio.sleep(120)
        if player.playing:
            return
        text_channel = (player.home if hasattr(player, "home") else None) # type: ignore
        try:
            await player.disconnect()

        except Exception:
            return

        # AUTO DISCONNECT EMBED
        if text_channel:
            try:
                embed = discord.Embed(color=0x5865F2)
                embed.description = (f"{EMOJIS['leave']} "
                                     f"**Session Ended**\n\n"
                                     f"{EMOJIS['warning']} "
                                     f"No music activity for `120s`\n\n"
                                     f"{EMOJIS['music_player']} "
                                     f"Bajao disconnected automatically.")
                embed.set_footer(text="Bajao Music System")
                await text_channel.send(embed=embed)
            except Exception:
                pass
        self.inactive_tasks.pop(guild_id, None)

    # TRACK END
    @commands.Cog.listener()
    async def on_wavelink_track_end(self,
                                    payload: wavelink.TrackEndEventPayload):
        player = payload.player
        if not player:
            return
        guild = player.guild
        if not guild:
            return
        if not player.queue.is_empty:
            next_track = await player.queue.get_wait()
            await player.play(next_track)
            return
        existing = self.inactive_tasks.get(guild.id)
        if existing:
            existing.cancel()
        self.inactive_tasks[guild.id] = (asyncio.create_task(
            self.inactivity_disconnect(guild.id, player)))

    @commands.Cog.listener()
    async def on_wavelink_track_start(
            self, payload: wavelink.TrackStartEventPayload):
        player = payload.player
        if not player:
            return
        guild = player.guild
        if not guild:
            return
        task = self.inactive_tasks.get(guild.id)
        if task:
            task.cancel()
            self.inactive_tasks.pop(guild.id, None)


async def setup(bot):
    await bot.add_cog(Status(bot))
