from __future__ import annotations
import asyncio
import discord
import wavelink
from discord.ext import commands
from config.emojis import EMOJIS
from manager.handlers.player_manager import PlayerManager
from manager.handlers.queue_manager import QueueManager
from ui.views.player_views import PlayerControls


class MusicEvents(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.disconnect_tasks: dict[int, asyncio.Task] = {}

    def cancel_disconnect_task(self, guild_id: int):
        old_task = self.disconnect_tasks.get(guild_id)
        if old_task:
            old_task.cancel()
            self.disconnect_tasks.pop(guild_id, None)

    def get_text_channel(self, player: wavelink.Player):
        return getattr(player, "home", None)

    async def safe_send(self, channel, embed: discord.Embed, view=None):
        if not channel:
            return None
        try:
            return await channel.send(embed=embed, view=view)
        except Exception:
            return None

    async def inactive_disconnect(self, player: wavelink.Player):
        await asyncio.sleep(120)
        if player.playing:
            return
        if player.channel:
            humans = [
                member for member in player.channel.members if not member.bot
            ]
            if humans:
                return
        text_channel = self.get_text_channel(player)
        try:
            QueueManager.clear(player)
            await player.disconnect()
        except Exception:
            return
        embed = discord.Embed(color=0x5865F2)
        embed.description = (f"{EMOJIS['leave']} "
                             f"**Session Ended**\n\n"
                             f"{EMOJIS['warning']} "
                             f"No music activity for `120s`\n\n"
                             f"{EMOJIS['music_player']} "
                             f"Bajao disconnected automatically.")
        embed.set_footer(text="Bajao Music System")
        await self.safe_send(text_channel, embed)

    @commands.Cog.listener()
    async def on_wavelink_track_start(
            self, payload: wavelink.TrackStartEventPayload):
        player = payload.player
        if not player:
            return
        guild = player.guild
        if not guild:
            return
        self.cancel_disconnect_task(guild.id)
        track = payload.track
        if not track:
            return
        text_channel = self.get_text_channel(player)
        if not text_channel:
            return
        try:
            embed = PlayerManager.build_now_playing(player, track)
            requester_id = (getattr(track.extras, "requester", 0) if hasattr(
                track, "extras") else 0)
            view = PlayerControls(player=player, requester_id=requester_id)
            message = await self.safe_send(text_channel, embed, view)
            if message:
                view.message = message
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_wavelink_track_end(self,
                                    payload: wavelink.TrackEndEventPayload):
        player = payload.player
        if not player:
            return
        next_track = await QueueManager.get_next(player)
        if next_track:
            await player.play(next_track)
            return
        guild = player.guild
        if not guild:
            return
        self.cancel_disconnect_task(guild.id)
        self.disconnect_tasks[guild.id] = (asyncio.create_task(
            self.inactive_disconnect(player)))

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member,
                                    before: discord.VoiceState,
                                    after: discord.VoiceState):
        if member.bot:
            return
        if not before.channel:
            return
        voice_client = (before.channel.guild.voice_client)
        if not isinstance(voice_client, wavelink.Player):
            return
        player = voice_client
        if (not player.channel or before.channel.id != player.channel.id):
            return
        humans = [
            member for member in before.channel.members if not member.bot
        ]
        if humans:
            return
        text_channel = self.get_text_channel(player)
        try:
            QueueManager.clear(player)
            await player.disconnect()
        except Exception:
            return
        embed = discord.Embed(color=0x5865F2)
        embed.description = (f"{EMOJIS['leave']} "
                             f"**Voice Channel Empty**\n\n"
                             f"{EMOJIS['music_player']} "
                             f"Bajao disconnected automatically.")
        embed.set_footer(text="Bajao Music System")
        await self.safe_send(text_channel, embed)


async def setup(bot):
    await bot.add_cog(MusicEvents(bot))
