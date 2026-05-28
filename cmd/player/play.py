from __future__ import annotations
import discord
import wavelink
from discord.ext import commands
from config.emojis import EMOJIS
from manager.basic_check import BasicChecks
from manager.handlers.player_manager import PlayerManager
from manager.handlers.queue_manager import QueueManager
from ui.views.player_views import PlayerControls
from ui.views.queue_views import QueueControls
from utils.respond import Respond


class Player(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cleanup(self, ctx: commands.Context):
        try:
            await ctx.message.delete()
        except Exception:
            pass

    # SEARCH TRACK
    async def search_track(self, query: str):
        query = " ".join(query.strip().split())
        if query.startswith(("http://", "https://")):
            return await wavelink.Playable.search(query)
        garbage = ("(lyrics)", "[lyrics]", "lyrics", "official video",
                   "official audio", "audio", "video")
        cleaned = query.lower()
        for item in garbage:
            cleaned = cleaned.replace(item, "")
        query = cleaned.strip()
        result = await wavelink.Playable.search(f"ytmsearch:{query}")
        if not result:
            result = await wavelink.Playable.search(f"ytsearch:{query}")
        return result

    @commands.hybrid_command(name="play",
                             aliases=["p"],
                             description="Play a song or playlist.")
    async def play(self, ctx: commands.Context, *, query: str):
        await self.cleanup(ctx)
        response = Respond(ctx=ctx)
        if not await BasicChecks.user_in_vc(ctx):
            return
        player = await PlayerManager.get_player(ctx)
        if not player:
            return
        setattr(player, "home", ctx.channel)
        loading_embed = discord.Embed(color=0x5865F2)
        loading_embed.description = (f"{EMOJIS['rounded_loading']} "
                                     f"Searching tracks...")
        loading_message = await ctx.send(embed=loading_embed)
        try:
            result = await self.search_track(query)
        except Exception:
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['fail']} "
                                 f"Failed to fetch search results.")
            await loading_message.edit(embed=embed)
            return

        # NO RESULTS
        if not result:
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['warning']} "
                                 f"No matching tracks found.")
            await loading_message.edit(embed=embed)
            return

        # PLAYLIST
        if isinstance(result, wavelink.Playlist):
            for track in result.tracks:
                track.extras = {"requester": ctx.author.id}
                await QueueManager.add_track(player, track)
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['playlist']} "
                                 f"**Playlist Added**\n\n"
                                 f"## {result.name[:42]}\n\n"
                                 f"{EMOJIS['queue']} "
                                 f"`{len(result.tracks)}` tracks queued\n\n"
                                 f"{EMOJIS['developer']} "
                                 f"{ctx.author.mention}")
            artwork = getattr(result, "artwork", None)
            if artwork:
                embed.set_thumbnail(url=artwork)
            embed.set_footer(text="Bajao Playlist System")
            await loading_message.edit(embed=embed)
            if not player.playing:
                next_track = await QueueManager.get_next(player)
                if next_track:
                    try:
                        await player.play(next_track)
                    except Exception as e:
                        error_embed = discord.Embed(color=0x5865F2)
                        error_embed.description = (f"{EMOJIS['fail']} "
                                                   f"Playback failed.\n\n"
                                                   f"`{str(e)[:150]}`")
                        await loading_message.edit(embed=error_embed)

            return
        track = (result[0] if isinstance(result, list) else result)
        if not track:
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['warning']} "
                                 f"No playable track found.")
            await loading_message.edit(embed=embed)
            return
        track.extras = {"requester": ctx.author.id}
        if player.playing:
            await QueueManager.add_track(player, track)
            queue_index = player.queue.count
            embed = discord.Embed(color=0x5865F2)
            embed.description = (
                f"{EMOJIS['queue']} "
                f"**Added To Queue**\n\n"
                f"## {track.title[:42]}\n\n"
                f"{EMOJIS['waveform']} "
                f"`{track.author[:24]}`\n\n"
                f"⏱️ "
                f"`{PlayerManager.format_time(track.length)}`\n\n"
                f"{EMOJIS['developer']} "
                f"{ctx.author.mention}")
            artwork = getattr(track, "artwork", None)
            if artwork:
                embed.set_thumbnail(url=artwork)
            embed.set_footer(text="Bajao Queue System")
            view = QueueControls(player=player,
                                 queue_index=queue_index,
                                 requester_id=ctx.author.id)

            await loading_message.edit(embed=embed, view=view)
            view.message = loading_message
            return
        try:
            await player.play(track)
        except Exception as e:
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['fail']} "
                                 f"Failed to start playback.\n\n"
                                 f"`{str(e)[:150]}`")
            await loading_message.edit(embed=embed)
            return
        embed = PlayerManager.build_now_playing(player, track)
        view = PlayerControls(player=player, requester_id=ctx.author.id)
        await loading_message.edit(embed=embed, view=view)
        view.message = loading_message

    # PAUSE
    @commands.hybrid_command(name="pause", description="Pause playback.")
    async def pause(self, ctx: commands.Context):
        await self.cleanup(ctx)
        response = Respond(ctx=ctx)
        player = await BasicChecks.player_playing(ctx)
        if not player:
            return
        if player.paused:
            return await response.warning("Already Paused",
                                          "Playback is already paused.")
        await player.pause(True)
        embed = discord.Embed(color=0x5865F2)
        embed.description = (f"{EMOJIS['pause']} "
                             f"Playback paused.")
        await response.send(embed=embed)

    # RESUME
    @commands.hybrid_command(name="resume", description="Resume playback.")
    async def resume(self, ctx: commands.Context):
        await self.cleanup(ctx)
        response = Respond(ctx=ctx)
        player = await BasicChecks.player_playing(ctx)
        if not player:
            return
        if not player.paused:
            return await response.warning("Not Paused",
                                          "Playback is not paused.")
        await player.pause(False)
        embed = discord.Embed(color=0x5865F2)
        embed.description = (f"{EMOJIS['play']} "
                             f"Playback resumed.")
        await response.send(embed=embed)

    # SKIP
    @commands.hybrid_command(name="skip",
                             aliases=["next"],
                             description="Skip current track.")
    async def skip(self, ctx: commands.Context):
        await self.cleanup(ctx)
        response = Respond(ctx=ctx)
        player = await BasicChecks.player_playing(ctx)
        if not player:
            return
        await player.skip()
        embed = discord.Embed(color=0x5865F2)
        embed.description = (f"{EMOJIS['skip']} "
                             f"Skipped current track.")
        await response.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Player(bot))
