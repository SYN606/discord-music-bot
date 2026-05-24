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

    @commands.Cog.listener()
    async def on_wavelink_track_start(
            self, payload: wavelink.TrackStartEventPayload):

        player = payload.player
        if not player:
            return
        guild = player.guild

        if not guild:
            return
        old_task = self.disconnect_tasks.get(guild.id)
        if old_task:
            old_task.cancel()
            self.disconnect_tasks.pop(guild.id, None)

        track = payload.track
        if not track:
            return
        text_channel = getattr(player, "home", None)
        if not text_channel:
            return

        try:
            embed = (PlayerManager.build_now_playing(player, track))
            requester_id = (getattr(track.extras, "requester", 0) if hasattr(
                track, "extras") else 0)
            view = PlayerControls(player=player, requester_id=requester_id)
            message = await text_channel.send(embed=embed, view=view)
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
        old_task = self.disconnect_tasks.get(guild.id)
        if old_task:
            old_task.cancel()
        self.disconnect_tasks[guild.id] = (asyncio.create_task(
            self.inactive_disconnect(player))) # type: ignore

    # EMPTY VC CHECK
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member,
                                    before: discord.VoiceState,
                                    after: discord.VoiceState):

        # IGNORE BOTS
        if member.bot:
            return

        # USER LEFT VC
        if not before.channel:
            return

        voice_client = (before.channel.guild.voice_client)
        if not isinstance(voice_client, wavelink.Player):
            return
        player = voice_client

        if (not player.channel or before.channel.id != player.channel.id):
            return

        humans = [m for m in before.channel.members if not m.bot]
        if humans:
            return
        text_channel = getattr(player, "home", None)

        try:
            QueueManager.clear(player)
            await player.disconnect()

        except Exception:
            return

        if text_channel:
            try:
                embed = discord.Embed(color=0x5865F2)
                embed.description = (f"{EMOJIS['leave']} "
                                     f"**Voice Channel Empty**\n\n"
                                     f"{EMOJIS['music_player']} "
                                     f"Bajao disconnected automatically.")

                embed.set_footer(text="Bajao Music System")
                await text_channel.send(embed=embed)
            except Exception:
                pass

        await asyncio.sleep(120)
        if player.playing:
            return

        if player.channel:
            humans = [
                member for member in player.channel.members if not member.bot
            ]
            if humans:
                return
        text_channel = getattr(player, "home", None)

        try:
            QueueManager.clear(player)
            await player.disconnect()
        except Exception:

            return
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


async def setup(bot):
    await bot.add_cog(MusicEvents(bot))
