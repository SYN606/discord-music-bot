from __future__ import annotations
import discord
import wavelink
from config.emojis import EMOJIS
from manager.handlers.player_manager import PlayerManager
from manager.handlers.queue_manager import QueueManager


class QueueControls(discord.ui.View):

    def __init__(self, player: wavelink.Player, queue_index: int,
                 requester_id: int):

        super().__init__(timeout=120)
        self.player = player
        self.queue_index = queue_index
        self.requester_id = requester_id
        self.message: discord.Message | None = None

    # VALIDATE USER
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.requester_id:
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['warning']} "
                                 f"Only the requester can manage this track.")
            await interaction.response.send_message(embed=embed,
                                                    ephemeral=True)
            return False
        return True

    # REMOVE TRACK
    @discord.ui.button(emoji=EMOJIS["fail"],
                       label="Remove",
                       style=discord.ButtonStyle.danger)
    async def remove_track(self, interaction: discord.Interaction,
                           button: discord.ui.Button):
        removed = QueueManager.remove_index(self.player, self.queue_index)
        if not removed:
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['warning']} "
                                 f"Track no longer exists in queue.")
            return await interaction.response.send_message(embed=embed,
                                                           ephemeral=True)
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        duration = (PlayerManager.format_time(removed.length))
        embed = discord.Embed(color=0x5865F2)
        embed.description = (f"{EMOJIS['success']} "
                             f"**Removed From Queue**\n\n"
                             f"## {removed.title[:45]}\n\n"
                             f"{EMOJIS['waveform']} "
                             f"`{removed.author[:28]}`\n\n"
                             f"{EMOJIS['play']} "
                             f"`{duration}`")
        artwork = getattr(removed, "artwork", None)
        if artwork:
            embed.set_thumbnail(url=artwork)
        embed.set_footer(text="Bajao Queue System")
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

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
