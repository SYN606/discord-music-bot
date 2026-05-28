from __future__ import annotations
from typing import cast
import discord
import wavelink
from config.emojis import EMOJIS
from manager.handlers.player_manager import PlayerManager
from ui.views.queue_paginator import QueuePaginator


class PlayerControls(discord.ui.View):

    def __init__(self, player: wavelink.Player, requester_id: int):

        super().__init__(timeout=300)
        self.player = player
        self.requester_id = requester_id
        self.message: discord.Message | None = None

    # VALIDATE
    async def interaction_check(self, interaction: discord.Interaction):
        member = cast(discord.Member, interaction.user)
        # USER NOT IN VC
        if not member.voice:
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['warning']} "
                                 f"Join the voice channel first.")
            await interaction.response.send_message(embed=embed,
                                                    ephemeral=True)
            return False

        # PLAYER DEAD
        if not self.player:
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['fail']} "
                                 f"No active player found.")
            await interaction.response.send_message(embed=embed,
                                                    ephemeral=True)
            return False

        # PLAYER VC
        if not self.player.channel:
            return False

        # DIFFERENT VC
        if member.voice.channel.id != self.player.channel.id:  # type: ignore
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['warning']} "
                                 f"You must be in the same voice channel.")
            await interaction.response.send_message(embed=embed,
                                                    ephemeral=True)
            return False
        return True

    # REFRESH PLAYER
    async def refresh_player(self, interaction: discord.Interaction):
        current = self.player.current
        if not current:
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['warning']} "
                                 f"Queue ended.")
            return await interaction.response.edit_message(embed=embed,
                                                           view=None)
        embed = PlayerManager.build_now_playing(self.player, current)
        await interaction.response.edit_message(embed=embed, view=self)

    # PAUSE / RESUME
    @discord.ui.button(emoji=EMOJIS["pause"],
                       style=discord.ButtonStyle.secondary)
    async def pause_resume(self, interaction: discord.Interaction,
                           button: discord.ui.Button):
        valid = await self.interaction_check(interaction)
        if not valid:
            return

        if self.player.paused:
            await self.player.pause(False)
            button.emoji = EMOJIS["pause"]
        else:
            await self.player.pause(True)
            button.emoji = EMOJIS["play"]
        await self.refresh_player(interaction)

    # SKIP
    @discord.ui.button(emoji=EMOJIS["skip"], style=discord.ButtonStyle.primary)
    async def skip(self, interaction: discord.Interaction,
                   button: discord.ui.Button):
        valid = await self.interaction_check(interaction)
        if not valid:
            return
        await self.player.skip()
        await self.refresh_player(interaction)

    # QUEUE
    @discord.ui.button(emoji="🎵", style=discord.ButtonStyle.success)
    async def queue(self, interaction: discord.Interaction,
                    button: discord.ui.Button):
        valid = await self.interaction_check(interaction)
        if not valid:
            return
        view = QueuePaginator(player=self.player,
                              author_id=interaction.user.id)
        embed = view.build_embed()
        await interaction.response.send_message(embed=embed,
                                                view=view,
                                                ephemeral=True)

    # LOOP
    @discord.ui.button(emoji="🔁", style=discord.ButtonStyle.secondary)
    async def loop(self, interaction: discord.Interaction,
                   button: discord.ui.Button):

        valid = await self.interaction_check(interaction)

        if not valid:
            return
        if self.player.queue.mode == wavelink.QueueMode.loop:
            self.player.queue.mode = (wavelink.QueueMode.normal)
            button.style = (discord.ButtonStyle.secondary)

        else:
            self.player.queue.mode = (wavelink.QueueMode.loop)
            button.style = (discord.ButtonStyle.success)
        await interaction.response.edit_message(view=self)

    # DISCONNECT
    @discord.ui.button(emoji=EMOJIS["leave"], style=discord.ButtonStyle.danger)
    async def leave(self, interaction: discord.Interaction,
                    button: discord.ui.Button):
        valid = await self.interaction_check(interaction)
        if not valid:
            return
        self.player.queue.clear()
        await self.player.disconnect()
        # DISABLE BUTTONS
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        embed = discord.Embed(color=0x5865F2)
        embed.description = (f"{EMOJIS['leave']} "
                             f"Disconnected from voice channel.")
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    # TIMEOUT
    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        if self.message:

            try:
                await self.message.edit(view=self)
            except Exception:
                pass

        self.stop()
