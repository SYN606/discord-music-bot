from __future__ import annotations
import time
from typing import cast
import discord
import wavelink
from config.emojis import EMOJIS


class VolumeControls(discord.ui.View):

    def __init__(self, player: wavelink.Player, author_id: int):
        super().__init__(timeout=180)
        self.player = player
        self.author_id = author_id
        self.message: discord.Message | None = None
        self.cooldowns: dict[int, float] = {}

    def is_rate_limited(self, user_id: int) -> bool:
        now = time.time()
        last = self.cooldowns.get(user_id, 0)
        if now - last < 1.5:
            return True
        self.cooldowns[user_id] = now
        return False

    async def validate(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['warning']} "
                                 f"Only the command author "
                                 f"can use these controls.")
            await interaction.response.send_message(embed=embed,
                                                    ephemeral=True)
            return False
        member = cast(discord.Member, interaction.user)

        # USER NOT IN VC
        if not member.voice:
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['warning']} "
                                 f"Join a voice channel first.")
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

            return False

        if member.voice.channel.id != self.player.channel.id:  # type: ignore
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['warning']} "
                                 f"You must be in the same "
                                 f"voice channel.")
            await interaction.response.send_message(embed=embed,
                                                    ephemeral=True)
            return False
        return True

    # BUILD EMBED
    def build_embed(self, volume: int):

        filled = volume // 10
        bars = ("▰" * filled + "▱" * (10 - filled))
        embed = discord.Embed(color=0x5865F2)
        embed.description = (f"{EMOJIS['volume']} "
                             f"**Bajao Volume**\n\n"
                             f"## `{volume}%`\n"
                             f"`{bars}`")
        embed.set_footer(text="Bajao Audio System")
        return embed

    # DOWN
    @discord.ui.button(emoji="➖", style=discord.ButtonStyle.secondary)
    async def volume_down(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        if self.is_rate_limited(interaction.user.id):
            return
        valid = await self.validate(interaction)
        if not valid:
            return
        new_volume = max(0, self.player.volume - 10)
        await self.player.set_volume(new_volume)
        embed = self.build_embed(new_volume)
        await interaction.response.edit_message(embed=embed, view=self)

    # UP
    @discord.ui.button(emoji="➕", style=discord.ButtonStyle.primary)
    async def volume_up(self, interaction: discord.Interaction,
                        button: discord.ui.Button):
        if self.is_rate_limited(interaction.user.id):
            return
        valid = await self.validate(interaction)
        if not valid:
            return
        new_volume = min(100, self.player.volume + 10)
        await self.player.set_volume(new_volume)
        embed = self.build_embed(new_volume)
        await interaction.response.edit_message(embed=embed, view=self)

    # MUTE
    @discord.ui.button(emoji="🔇", style=discord.ButtonStyle.danger)
    async def mute(self, interaction: discord.Interaction,
                   button: discord.ui.Button):
        valid = await self.validate(interaction)
        if not valid:
            return
        await self.player.set_volume(0)
        embed = self.build_embed(0)
        await interaction.response.edit_message(embed=embed, view=self)

    # MAX
    @discord.ui.button(emoji="🔊", style=discord.ButtonStyle.success)
    async def max_volume(self, interaction: discord.Interaction,
                         button: discord.ui.Button):
        valid = await self.validate(interaction)
        if not valid:
            return

        await self.player.set_volume(100)
        embed = self.build_embed(100)
        await interaction.response.edit_message(embed=embed, view=self)

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
