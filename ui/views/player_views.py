from __future__ import annotations
from typing import cast
import discord
import wavelink
from config.emojis import EMOJIS
from manager.handlers.player_manager import PlayerManager
from ui.views.queue_paginator import QueuePaginator


class PlayerControls(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # GET PLAYER
    def get_player(self,
                   interaction: discord.Interaction) -> wavelink.Player | None:
        return cast(
            wavelink.Player | None,
            interaction.guild.voice_client if interaction.guild else None)

    # VALIDATE
    async def validate(
            self, interaction: discord.Interaction) -> wavelink.Player | None:
        player = self.get_player(interaction)
        if not player:
            await interaction.response.send_message(embed=discord.Embed(
                color=0x5865F2,
                description=(f"{EMOJIS['fail']} "
                             f"No active player found.")),
                                                    ephemeral=True)
            return None
        member = cast(discord.Member, interaction.user)
        if not member.voice:
            await interaction.response.send_message(embed=discord.Embed(
                color=0x5865F2,
                description=(f"{EMOJIS['warning']} "
                             f"Join a voice channel first.")),
                                                    ephemeral=True)

            return None
        if (player.channel and member.voice.channel.id  # type: ignore
                != player.channel.id):
            await interaction.response.send_message(embed=discord.Embed(
                color=0x5865F2,
                description=(f"{EMOJIS['warning']} "
                             f"You must be in the same voice channel.")),
                                                    ephemeral=True)
            return None
        return player

    @discord.ui.button(emoji=EMOJIS["pause"],
                       style=discord.ButtonStyle.secondary,
                       row=0)
    async def pause_resume(self, interaction: discord.Interaction,
                           button: discord.ui.Button):
        player = await self.validate(interaction)

        if not player:
            return
        if player.paused:
            await player.pause(False)
            button.emoji = EMOJIS["pause"]

        else:
            await player.pause(True)
            button.emoji = EMOJIS["play"]
        current = player.current
        if not current:
            return

        embed = PlayerManager.build_now_playing(player, current)
        await interaction.response.edit_message(embed=embed, view=self)

    # SKIP
    @discord.ui.button(emoji=EMOJIS["skip"],
                       style=discord.ButtonStyle.primary,
                       row=0)
    async def skip(self, interaction: discord.Interaction,
                   button: discord.ui.Button):
        player = await self.validate(interaction)
        if not player:
            return
        await player.skip()
        current = player.current
        if not current:
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['warning']} "
                                 f"Queue ended.")
            return await interaction.response.edit_message(embed=embed,
                                                           view=None)

        embed = PlayerManager.build_now_playing(player, current)
        await interaction.response.edit_message(embed=embed, view=self)
    # QUEUE
    @discord.ui.button(emoji=EMOJIS["queue"],
                       style=discord.ButtonStyle.success,
                       row=0)
    async def queue(self, interaction: discord.Interaction,
                    button: discord.ui.Button):
        player = await self.validate(interaction)
        if not player:
            return
        view = QueuePaginator(player=player, author_id=interaction.user.id)
        await interaction.response.send_message(embed=view.build_embed(),
                                                view=view,
                                                ephemeral=True)

    # REFRESH
    @discord.ui.button(emoji="🔄", style=discord.ButtonStyle.secondary, row=0)
    async def refresh(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
        player = await self.validate(interaction)
        if not player:
            return
        current = player.current
        if not current:
            return
        embed = PlayerManager.build_now_playing(player, current)
        await interaction.response.edit_message(embed=embed, view=self)

    # LEAVE
    @discord.ui.button(emoji=EMOJIS["leave"],
                       style=discord.ButtonStyle.danger,
                       row=0)
    async def leave(self, interaction: discord.Interaction,
                    button: discord.ui.Button):

        player = await self.validate(interaction)

        if not player:
            return

        player.queue.clear()

        await player.disconnect()

        # DISABLE BUTTONS
        for item in self.children:

            item.disabled = True  # type: ignore

        embed = discord.Embed(color=0x5865F2)

        embed.description = (f"{EMOJIS['leave']} "
                             f"Disconnected from voice channel.")

        await interaction.response.edit_message(embed=embed, view=self)
