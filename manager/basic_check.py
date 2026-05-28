from __future__ import annotations
from typing import cast
import discord
import wavelink
from discord.ext import commands
from utils.respond import Respond


class BasicChecks:

    @staticmethod
    def get_player(ctx: commands.Context) -> wavelink.Player | None:
        return cast(wavelink.Player | None, ctx.voice_client)

    @staticmethod
    def is_privileged(ctx: commands.Context) -> bool:

        member = cast(discord.Member, ctx.author)
        if (ctx.guild and ctx.guild.owner_id == member.id):
            return True
        perms = member.guild_permissions
        return any(
            (perms.administrator, perms.manage_guild, perms.manage_channels))

    @staticmethod
    async def user_in_vc(ctx: commands.Context) -> bool:
        response = Respond(ctx=ctx)
        member = cast(discord.Member, ctx.author)
        if not member.voice:
            await response.warning("Voice Channel Required",
                                   "You must join a voice channel first.")
            return False
        return True

    @staticmethod
    async def player_exists(ctx: commands.Context) -> wavelink.Player | None:
        response = Respond(ctx=ctx)
        player = BasicChecks.get_player(ctx)
        if not player:
            await response.warning("Nothing Playing",
                                   "No active player found.")
            return None
        return player

    @staticmethod
    async def same_voice_channel(
            ctx: commands.Context) -> wavelink.Player | None:
        response = Respond(ctx=ctx)
        if not await BasicChecks.user_in_vc(ctx):
            return None
        player = await BasicChecks.player_exists(ctx)
        if not player:
            return None
        player_channel = cast(discord.VoiceChannel | None, player.channel)
        if not player_channel:
            await response.warning("Voice Channel Missing",
                                   "Bot is not connected to a voice channel.")
            return None
        if BasicChecks.is_privileged(ctx):
            return player
        member = cast(discord.Member, ctx.author)
        member_voice = member.voice
        if not member_voice or not member_voice.channel:
            await response.warning("Voice Channel Required",
                                   "You must join a voice channel first.")
            return None
        if member_voice.channel.id != player_channel.id:
            await response.warning(
                "Wrong Voice Channel",
                "You must be in the same voice channel as the bot.")
            return None
        return player

    @staticmethod
    async def player_playing(ctx: commands.Context) -> wavelink.Player | None:
        response = Respond(ctx=ctx)
        player = await BasicChecks.same_voice_channel(ctx)
        if not player:
            return None
        if not player.current:
            await response.warning("Nothing Playing",
                                   "No active track is currently playing.")
            return None
        return player

    @staticmethod
    def can_control(ctx: commands.Context, requester_id: int | None) -> bool:
        member = cast(discord.Member, ctx.author)
        if requester_id == member.id:
            return True
        return BasicChecks.is_privileged(ctx)
