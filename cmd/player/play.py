from __future__ import annotations
from typing import cast
import discord
import wavelink
from discord.ext import commands
from config.embeds import make_embed
from config.emojis import EMOJIS
from config.settings import DEFAULT_VOLUME
from utils.respond import Respond


class Player(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # GET / CREATE PLAYER
    async def get_player(self,
                         ctx: commands.Context) -> wavelink.Player | None:

        response = Respond(ctx=ctx)
        member = cast(discord.Member, ctx.author)

        # USER MUST BE IN VC
        if not member.voice:
            await response.warning("Voice Channel Required",
                                   "You must join a voice channel first.")
            return None

        channel = member.voice.channel
        if channel is None:
            await response.warning("Voice Channel Required",
                                   "You must join a voice channel first.")
            return None

        # EXISTING PLAYER
        player = cast(wavelink.Player | None, ctx.voice_client)
        # CONNECT
        if player is None:
            player = await channel.connect(
                cls=wavelink.Player,
                self_deaf=True,
            )
            await player.set_volume(DEFAULT_VOLUME, )
        return player

    # FORMAT TIME
    def format_time(self, milliseconds: int) -> str:
        seconds = milliseconds // 1000
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return (f"{hours}:"
                    f"{minutes:02}:"
                    f"{seconds:02}")

        return (f"{minutes}:"
                f"{seconds:02}")

    # PLAY
    @commands.hybrid_command(name="play",
                             aliases=["p"],
                             description="Play a song or playlist.")
    async def play(self, ctx: commands.Context, *, query: str):
        response = Respond(ctx=ctx)
        player = await self.get_player(ctx, )
        if not player:
            return

        loading = await response.raw(f"{EMOJIS['rounded_loading']} "
                                     f"Searching for tracks...")

        tracks = await wavelink.Playable.search(query, )

        # NO RESULTS
        if not tracks:

            return await response.error("No Results", "No tracks were found.")

        # PLAYLIST
        if isinstance(tracks, wavelink.Playlist):
            added = 0
            for track in tracks.tracks:
                player.queue.put(track)
                added += 1

            embed = make_embed(title="Playlist Added",
                               description=(f"{EMOJIS['playlist']} "
                                            f"Added **{added}** tracks "
                                            f"from `{tracks.name}`"),
                               level="MUSIC")
            if isinstance(loading, discord.Message):
                await loading.edit(content=None, embed=embed)
            else:
                await response.send(embed=embed)

            # AUTOPLAY IF IDLE
            if not player.playing:
                next_track = await player.queue.get_wait()
                await player.play(next_track)

            return

        # SINGLE TRACK
        track = tracks[0]

        # QUEUE TRACK
        if player.playing:
            player.queue.put(track)
            embed = make_embed(
                title="Added To Queue",
                description=(f"{EMOJIS['queue']} "
                             f"Queued "
                             f"**{track.title}**"),
                level="MUSIC",
                thumbnail=track.artwork,
                fields=[
                    ("Author", f"`{track.author}`", True),
                    ("Duration", f"`{self.format_time(track.length)}`", True),
                ],
            )

            if isinstance(loading, discord.Message):
                await loading.edit(content=None, embed=embed)

            else:
                await response.send(embed=embed, )

            return

        # PLAY IMMEDIATELY
        await player.play(track, )

        embed = make_embed(
            title="Now Playing",
            description=(f"{EMOJIS['music']} "
                         f"Now playing "
                         f"**{track.title}**"),
            level="MUSIC",
            thumbnail=track.artwork,
            fields=[
                ("Author", f"`{track.author}`", True),
                ("Duration", f"`{self.format_time(track.length)}`", True),
                ("Volume", f"`{player.volume}%`", True),
            ],
        )

        if isinstance(loading, discord.Message):
            await loading.edit(content=None, embed=embed)
        else:
            await response.send(embed=embed)

    # PAUSE
    @commands.hybrid_command(name="pause", description="Pause current track.")
    async def pause(self, ctx: commands.Context):
        response = Respond(ctx=ctx)
        player = cast(wavelink.Player | None, ctx.voice_client)
        if not player or not player.playing:

            return await response.warning("Nothing Playing",
                                          "There is no active track.")

        if player.paused:
            return await response.warning("Already Paused",
                                          "Playback is already paused.")

        await player.pause(True, )
        await response.success("Playback Paused",
                               "Music playback has been paused.")

    # RESUME
    @commands.hybrid_command(name="resume", description="Resume playback.")
    async def resume(self, ctx: commands.Context):
        response = Respond(ctx=ctx)
        player = cast(wavelink.Player | None, ctx.voice_client)
        if not player:
            return await response.warning("Nothing Playing",
                                          "No active player found.")

        if not player.paused:
            return await response.warning("Not Paused",
                                          "Playback is not paused.")

        await player.pause(False)
        await response.success("Playback Resumed",
                               "Music playback has resumed.")

    # SKIP
    @commands.hybrid_command(name="skip",
                             aliases=["next"],
                             description="Skip current track.")
    async def skip(self, ctx: commands.Context):
        response = Respond(ctx=ctx)
        player = cast(wavelink.Player | None, ctx.voice_client)
        if not player or not player.playing:
            return await response.warning("Nothing Playing",
                                          "There is no track to skip.")

        current = player.current
        if current is None:
            return await response.warning("Nothing Playing",
                                          "No active track found.")
        await player.skip()
        await response.success("Track Skipped", f"Skipped **{current.title}**")

    # STOP
    @commands.hybrid_command(name="stop",
                             description="Stop playback and clear queue.")
    async def stop(self, ctx: commands.Context):
        response = Respond(ctx=ctx)
        player = cast(wavelink.Player | None, ctx.voice_client)
        if not player:
            return await response.warning("Nothing Playing",
                                          "No active player found.")

        player.queue.clear()
        await player.disconnect()
        await response.success("Playback Stopped",
                               "Disconnected from voice channel.")

    # QUEUE
    @commands.hybrid_command(name="queue",
                             aliases=["q"],
                             description="Show current queue.")
    async def queue(self, ctx: commands.Context):
        response = Respond(ctx=ctx)
        player = cast(wavelink.Player | None, ctx.voice_client)
        if not player:
            return await response.warning("Queue Empty",
                                          "No active player found.")

        if player.queue.is_empty:
            return await response.warning("Queue Empty",
                                          "There are no queued tracks.")
        entries = []
        for index, track in enumerate(player.queue, start=1):
            entries.append(f"`{index}.` "
                           f"**{track.title}** "
                           f"(`{self.format_time(track.length)}`)")

            if index >= 10:
                break

        embed = make_embed(title="Music Queue",
                           description="\n".join(entries),
                           level="MUSIC",
                           footer=(f"{len(player.queue)} "
                                   f"tracks queued"))

        await response.send(embed=embed)

    # DISCONNECT
    @commands.hybrid_command(name="disconnect",
                             aliases=["dc", "leave"],
                             description="Disconnect from VC.")
    async def disconnect(self, ctx: commands.Context):
        response = Respond(ctx=ctx)
        player = cast(wavelink.Player | None, ctx.voice_client)
        if not player:
            return await response.warning("Not Connected",
                                          "I'm not in a voice channel.")

        await player.disconnect()
        await response.success("Disconnected", "Left the voice channel.")

    # TRACK END
    @commands.Cog.listener()
    async def on_wavelink_track_end(self,
                                    payload: wavelink.TrackEndEventPayload):

        player = payload.player
        if not player:
            return

        if not player.queue.is_empty:
            next_track = await player.queue.get_wait()
            await player.play(next_track, )


async def setup(bot):
    await bot.add_cog(Player(bot))
