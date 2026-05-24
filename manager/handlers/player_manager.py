from __future__ import annotations
from typing import cast
import discord
import wavelink
from config.emojis import EMOJIS
from config.settings import DEFAULT_VOLUME
from utils.respond import Respond


class PlayerManager:

    @staticmethod
    async def get_player(ctx) -> wavelink.Player | None:
        response = Respond(ctx=ctx)
        member = cast(discord.Member, ctx.author)
        if not member.voice:
            await response.warning("Voice Channel Required",
                                   "You must join a voice channel first.")
            return None
        channel = member.voice.channel
        if channel is None:
            return None
        player = cast(wavelink.Player | None, ctx.voice_client)
        if player is None:
            player = await channel.connect(cls=wavelink.Player, self_deaf=True)
            await player.set_volume(DEFAULT_VOLUME)
            player.home = ctx.channel  # type: ignore
        return player

    # VALIDATE ACTIVE PLAYER
    @staticmethod
    async def validate_player(ctx) -> wavelink.Player | None:
        response = Respond(ctx=ctx)
        player = cast(wavelink.Player | None, ctx.voice_client)
        if not player:
            await response.warning("Nothing Playing",
                                   "No active player found.")
            return None
        member = cast(discord.Member, ctx.author)
        if not member.voice:
            await response.warning("Voice Channel Required",
                                   "You must join a voice channel first.")
            return None

        if not player.channel:
            await response.warning("Voice Channel Missing",
                                   "Bot is not connected to a voice channel.")
            return None
        if member.voice.channel.id != player.channel.id:  # type: ignore
            await response.warning(
                "Wrong Voice Channel",
                "You must be in the same voice channel as the bot.")
            return None
        return player

    # FORMAT TIME
    @staticmethod
    def format_time(milliseconds: int) -> str:
        seconds = milliseconds // 1000
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return (f"{hours}:"
                    f"{minutes:02}:"
                    f"{seconds:02}")

        return (f"{minutes}:"
                f"{seconds:02}")

    # PROGRESS BAR
    @staticmethod
    def progress_bar(position: int, length: int, size: int = 14) -> str:

        if length <= 0:
            return "▬" * size
        filled = int((position / length) * size)
        filled = min(filled, size - 1)
        bar = ""

        for index in range(size):
            if index == filled:
                bar += "🔘"
            else:

                bar += "▬"

        return bar

    # NOW PLAYING EMBED
    @staticmethod
    def build_now_playing(player: wavelink.Player,
                          track: wavelink.Playable) -> discord.Embed:

        position = getattr(player, "position", 0)
        progress = PlayerManager.progress_bar(position, track.length, 16)
        requester = (
            f"<@{track.extras.requester}>" if hasattr(track, "extras")
            and getattr(track.extras, "requester", None) else "Unknown")

        queue_count = player.queue.count
        current_time = (PlayerManager.format_time(position))
        total_time = (PlayerManager.format_time(track.length))
        embed = discord.Embed(color=0x5865F2)

        # BOT BANNER
        try:
            banner = (player.client.user.banner)  # type: ignore
            if banner:
                embed.set_image(url=banner.url)

        except Exception:
            pass

        # MAIN DESCRIPTION
        embed.description = (f"{EMOJIS['music_player']} "
                             f"**Bajao Cassette**\n\n"
                             f"## {track.title[:45]}\n"
                             f"{EMOJIS['waveform']} "
                             f"`{track.author[:28]}`\n\n"
                             f"`{current_time}`\n"
                             f"{progress}\n"
                             f"`{total_time}`\n\n"
                             f"{EMOJIS['volume']} "
                             f"`{player.volume}%`\n"
                             f"{EMOJIS['queue']} "
                             f"`{queue_count}` queued\n\n"
                             f"{EMOJIS['developer']} "
                             f"{requester}")

        # TRACK ARTWORK
        artwork = getattr(track, "artwork", None)
        if artwork:
            embed.set_thumbnail(url=artwork)
        embed.set_footer(text="Bajao • Cassette Experience")
        return embed

    # QUEUE EMBED
    @staticmethod
    def build_queue_embed(player: wavelink.Player) -> discord.Embed:
        embed = discord.Embed(color=0x5865F2)
        if player.queue.is_empty:
            embed.description = (f"{EMOJIS['warning']} "
                                 f"Queue is empty.")
            return embed
        entries: list[str] = []
        for index, track in enumerate(player.queue, start=1):
            duration = (PlayerManager.format_time(track.length))
            entries.append(f"`{index}.` "
                           f"{track.title[:40]}\n"
                           f"> `{duration}` "
                           f"• "
                           f"`{track.author[:20]}`")
            if index >= 10:
                break
        embed.description = (f"{EMOJIS['queue']} "
                             f"**Bajao Queue**\n\n"
                             f"{chr(10).join(entries)}")
        current = player.current
        if (current and getattr(current, "artwork", None)):
            embed.set_thumbnail(url=current.artwork)
        embed.set_footer(text=(f"{player.queue.count} tracks queued"))
        return embed
