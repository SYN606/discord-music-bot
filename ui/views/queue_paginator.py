from __future__ import annotations
import discord
import wavelink
from config.emojis import EMOJIS
from manager.handlers.player_manager import PlayerManager
from manager.handlers.queue_manager import QueueManager


class QueuePaginator(discord.ui.View):

    def __init__(self, player: wavelink.Player, author_id: int):

        super().__init__(timeout=120)

        self.player = player
        self.author_id = author_id
        self.page = 0
        self.per_page = 10

    # VALIDATE USER
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            embed = discord.Embed(color=0x5865F2)
            embed.description = (f"{EMOJIS['warning']} "
                                 f"You cannot control this queue.")
            await interaction.response.send_message(embed=embed,
                                                    ephemeral=True)
            return False
        return True

    # BUILD EMBED
    def build_embed(self):

        queue = QueueManager.get_queue(self.player)
        tracks = QueueManager.get_page(self.player, self.page, self.per_page)
        current = self.player.current
        embed = discord.Embed(color=0x5865F2)
        description = (f"{EMOJIS['queue']} "
                       f"**DV-Music Queue**\n\n")

        # CURRENT TRACK
        if current:
            current_duration = (PlayerManager.format_time(current.length))
            description += (f"{EMOJIS['play']} "
                            f"**Now Playing**\n"
                            f"> {current.title[:40]}\n"
                            f"> `{current_duration}` "
                            f"• "
                            f"`{current.author[:20]}`\n\n")

        # EMPTY QUEUE
        if not tracks:

            description += (f"{EMOJIS['warning']} "
                            f"Queue is empty.")
        else:
            for index, track in enumerate(tracks,
                                          start=(self.page * self.per_page) +
                                          1):
                duration = (PlayerManager.format_time(track.length))
                description += (f"`{index}.` "
                                f"{track.title[:45]}\n"
                                f"> `{duration}` "
                                f"• "
                                f"`{track.author[:24]}`\n\n")

        embed.description = description
        if current and getattr(current, "artwork", None):
            embed.set_thumbnail(url=current.artwork)
        total_pages = QueueManager.total_pages(self.player, self.per_page)
        embed.set_footer(text=(f"Page "
                               f"{self.page + 1}/{total_pages} "
                               f"• "
                               f"{len(queue)} queued"))
        self.previous.disabled = (self.page <= 0)
        self.next.disabled = (self.page >= total_pages - 1)
        return embed

    # PREVIOUS
    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction,
                       button: discord.ui.Button):
        self.page -= 1
        await interaction.response.edit_message(embed=self.build_embed(),
                                                view=self)

    # REFRESH
    @discord.ui.button(emoji="🔄", style=discord.ButtonStyle.primary)
    async def refresh(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.build_embed(),
                                                view=self)

    # NEXT
    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction,
                   button: discord.ui.Button):
        self.page += 1
        await interaction.response.edit_message(embed=self.build_embed(),
                                                view=self)

    # CLOSE
    @discord.ui.button(emoji=EMOJIS["leave"], style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction,
                    button: discord.ui.Button):

        for child in self.children:
            child.disabled = True # type: ignore
        embed = discord.Embed(color=0x5865F2)
        embed.description = (f"{EMOJIS['leave']} "
                             f"Queue viewer closed.")
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
