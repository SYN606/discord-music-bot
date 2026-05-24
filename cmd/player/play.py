from __future__ import annotations
import discord
import wavelink
from discord.ext import commands
from config.emojis import EMOJIS
from manager.handlers.player_manager import PlayerManager
from manager.handlers.queue_manager import QueueManager
from ui.views.player_views import PlayerControls
from ui.views.queue_views import QueueControls
from utils.respond import Respond


class Player(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # DELETE USER COMMAND
    async def cleanup(self, ctx: commands.Context):

        try:
            await ctx.message.delete()
        except Exception:
            pass

    # SEARCH TRACK
    async def search_track(self, query: str):
        query = " ".join(query.strip().split())
        garbage = ("(lyrics)", "[lyrics]", "lyrics", "official video",
                   "official audio", "audio", "video")

        cleaned = query.lower()

        for item in garbage:
            cleaned = cleaned.replace(item, "")
        query = cleaned.strip()

        # URL SEARCH
        if query.startswith(("http://", "https://")):
            return await wavelink.Playable.search(query)
        result = await wavelink.Playable.search(f"ytmsearch:{query}")
        if not result:
            result = await wavelink.Playable.search(f"ytsearch:{query}")
        return result

    # PLAY
    @commands.hybrid_command(name="play",
                             aliases=["p"],
                             description="Play a song or playlist.")
    async def play(self, ctx: commands.Context, *, query: str):

        response = Respond(ctx=ctx)
        # CLEANUP
        await self.cleanup(ctx)
        # PLAYER
        player = await PlayerManager.get_player(ctx)
        if not player:
            return

        # LOADING EMBED
        loading_embed = discord.Embed(color=0x5865F2)
        loading_embed.description = (f"{EMOJIS['rounded_loading']} "
                                     f"Searching for tracks...")
        loading = await response.send(embed=loading_embed)

        # SEARCH
        try:
            result = await self.search_track(query)

        except Exception:
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['fail']} "
                                 f"Failed to fetch search results.")
            return await loading.edit(embed=embed)  # type: ignore

        # NO RESULTS
        if not result:
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['warning']} "
                                 f"No matching tracks found.")
            return await loading.edit(embed=embed)  # type: ignore

        # PLAYLIST
        if isinstance(result, wavelink.Playlist):
            for track in result.tracks:
                track.extras = {"requester": ctx.author.id}
                await QueueManager.add_track(player, track)
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['playlist']} "
                                 f"**Playlist Added**\n\n"
                                 f"## {result.name[:45]}\n\n"
                                 f"{EMOJIS['queue']} "
                                 f"`{len(result.tracks)}` tracks queued\n\n"
                                 f"{EMOJIS['developer']} "
                                 f"{ctx.author.mention}")
            artwork = getattr(result, "artwork", None)
            if artwork:
                embed.set_thumbnail(url=artwork)
            await loading.edit(embed=embed)  # type: ignore

            # START PLAYER
            if not player.playing:
                next_track = await QueueManager.get_next(player)
                if next_track:
                    await player.play(next_track)
            return

        # TRACK
        track = (result[0] if isinstance(result, list) else result)
        if not track:
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['warning']} "
                                 f"No playable track found.")
            return await loading.edit(embed=embed)  # type: ignore
        # REQUESTER
        track.extras = {"requester": ctx.author.id}

        # ADD TO QUEUE
        if player.playing:
            await QueueManager.add_track(player, track)
            queue_index = player.queue.count
            embed = discord.Embed(color=0x5865F2)
            embed.description = (
                f"{EMOJIS['queue']} "
                f"**Added To Queue**\n\n"
                f"## {track.title[:45]}\n"
                f"{EMOJIS['waveform']} "
                f"`{track.author[:28]}`\n\n"
                f"{EMOJIS['play']} "
                f"`{PlayerManager.format_time(track.length)}`\n\n"
                f"{EMOJIS['developer']} "
                f"{ctx.author.mention}")

            artwork = getattr(track, "artwork", None)

            if artwork:

                embed.set_thumbnail(url=artwork)
            view = QueueControls(player=player,
                                 queue_index=queue_index,
                                 requester_id=ctx.author.id)
            return await loading.edit(embed=embed, view=view)  # type: ignore

        # PLAY TRACK
        await player.play(track)
        embed = PlayerManager.build_now_playing(player, track)
        view = PlayerControls()
        await loading.edit(embed=embed, view=view)  # type: ignore

    # PLAY ERROR
    @play.error
    async def play_error(self, ctx: commands.Context,
                         error: commands.CommandError):

        response = Respond(ctx=ctx)
        await self.cleanup(ctx)

        # MISSING QUERY
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['music_player']} "
                                 f"**Play Music**\n\n"
                                 f"{EMOJIS['warning']} "
                                 f"You forgot to provide a song.\n\n"
                                 f"{EMOJIS['queue']} "
                                 f"**Examples**\n\n"
                                 f"`dvm play perfect`\n"
                                 f"`dvm play industry baby`\n"
                                 f"`dvm play https://youtu.be/...`")

            embed.set_footer(text="DV-Music Search System")
            return await response.send(embed=embed)

        # BAD ARGUMENT
        if isinstance(error, commands.BadArgument):
            return await response.warning(
                "Invalid Query", "Could not understand your search query.")
        return await response.error("Command Error", str(error))

    # PAUSE
    @commands.hybrid_command(name="pause", description="Pause playback.")
    async def pause(self, ctx: commands.Context):

        await self.cleanup(ctx)
        response = Respond(ctx=ctx)
        player = await PlayerManager.validate_player(ctx)

        if not player:
            return

        if player.paused:
            return await response.warning("Already Paused",
                                          "Playback is already paused.")

        await player.pause(True)
        await response.success("Playback Paused",
                               "Music playback has been paused.")

    # RESUME
    @commands.hybrid_command(name="resume", description="Resume playback.")
    async def resume(self, ctx: commands.Context):

        await self.cleanup(ctx)
        response = Respond(ctx=ctx)
        player = await PlayerManager.validate_player(ctx)
        if not player:
            return

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

        await self.cleanup(ctx)
        response = Respond(ctx=ctx)
        player = await PlayerManager.validate_player(ctx)
        if not player:
            return
        current = player.current
        if not current:
            return await response.warning("Nothing Playing",
                                          "No active track found.")
        await player.skip()
        await response.success("Track Skipped",
                               f"Skipped **{current.title[:45]}**")

    # STOP
    @commands.hybrid_command(name="stop", description="Stop playback.")
    async def stop(self, ctx: commands.Context):
        await self.cleanup(ctx)
        response = Respond(ctx=ctx)
        player = await PlayerManager.validate_player(ctx)
        if not player:
            return

        QueueManager.clear(player)
        await player.disconnect()
        await response.success("Playback Stopped",
                               "Disconnected from voice channel.")


async def setup(bot):
    await bot.add_cog(Player(bot))
