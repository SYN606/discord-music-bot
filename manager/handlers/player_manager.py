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
        guild = ctx.guild
        if not guild:
            return None
        member = cast(discord.Member, ctx.author)
        voice = member.voice
        if not voice or not voice.channel:
            await response.warning("Voice Channel Required",
                                   "You must join a voice channel first.")
            return None
        channel = voice.channel
        player = cast(wavelink.Player | None, ctx.voice_client)
        try:
            nodes = wavelink.Pool.nodes
            if not nodes:
                await response.warning("Lavalink Offline",
                                       "No active Lavalink nodes available.")
                return None
        except Exception:
            await response.warning("Lavalink Error",
                                   "Failed to access Lavalink nodes.")
            return None
        if player is None:
            try:
                existing_vc = guild.voice_client
                if existing_vc:
                    await existing_vc.disconnect(force=True)
            except Exception:
                pass
            try:
                player = await channel.connect(cls=wavelink.Player,
                                               self_deaf=True,
                                               timeout=60)
            except Exception as e:
                await response.warning(
                    "Voice Connection Failed", f"Unable to connect to "
                    f"`{channel.name}`.\n\n"
                    f"`{str(e)[:150]}`")
                return None
            try:
                await player.set_volume(DEFAULT_VOLUME)
            except Exception:
                pass
            setattr(player, "home", ctx.channel)
        return player

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

    @staticmethod
    def build_now_playing(player: wavelink.Player,
                          track: wavelink.Playable) -> discord.Embed:
        position = getattr(player, "position", 0)
        current_time = (PlayerManager.format_time(position))
        total_time = (PlayerManager.format_time(track.length))
        requester = "Unknown"
        try:
            requester_id = (track.extras.get("requester")
                            if isinstance(track.extras, dict) else getattr(
                                track.extras, "requester", None))
            if requester_id:
                requester = f"<@{requester_id}>"
        except Exception:
            pass
        loop_status = ("ON" if player.queue.mode != wavelink.QueueMode.normal
                       else "OFF")
        queue_count = player.queue.count
        embed = discord.Embed(color=0x5865F2)
        try:
            bot_user = player.client.user
            if (bot_user and bot_user.banner):
                embed.set_image(url=bot_user.banner.url)
        except Exception:
            pass
        embed.description = (f"{EMOJIS['music_player']} "
                             f"**Bajao Cassette**\n\n"
                             f"## {track.title[:42]}\n\n"
                             f"{EMOJIS['waveform']} "
                             f"`{track.author[:26]}`\n\n"
                             f"⏱️ "
                             f"`{current_time}` "
                             f"/ `{total_time}`\n\n"
                             f"🎚️ "
                             f"`{player.volume}%` "
                             f"• "
                             f"🎵 "
                             f"`{queue_count}` queued "
                             f"• "
                             f"🔁 "
                             f"`{loop_status}`\n\n"
                             f"Requested by {requester}")

        artwork = getattr(track, "artwork", None)
        if artwork:
            embed.set_thumbnail(url=artwork)
        embed.set_footer(text="Bajao • Music Experience")
        return embed

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
                           f"{track.title[:38]}\n"
                           f"> `{duration}` "
                           f"• "
                           f"`{track.author[:18]}`")
            if index >= 10:
                break
        embed.description = (f"{EMOJIS['queue']} "
                             f"**Bajao Queue**\n\n"
                             f"{chr(10).join(entries)}")
        current = player.current
        if (current and getattr(current, "artwork", None)):
            embed.set_thumbnail(url=current.artwork)
        embed.set_footer(text=f"{player.queue.count} tracks queued")
        return embed
