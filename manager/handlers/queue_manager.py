from __future__ import annotations

import wavelink


class QueueManager:

    # ADD TRACK
    @staticmethod
    async def add_track(player: wavelink.Player, track: wavelink.Playable):

        player.queue.put(track)

    # ADD PLAYLIST
    @staticmethod
    async def add_playlist(player: wavelink.Player,
                           playlist: wavelink.Playlist):

        for track in playlist.tracks:

            player.queue.put(track)

    # GET NEXT TRACK
    @staticmethod
    async def get_next(player: wavelink.Player):

        if player.queue.is_empty:
            return None

        return await player.queue.get_wait()

    # CLEAR QUEUE
    @staticmethod
    def clear(player: wavelink.Player):

        player.queue.clear()

    # QUEUE COUNT
    @staticmethod
    def count(player: wavelink.Player) -> int:

        return player.queue.count

    # GET QUEUE LIST
    @staticmethod
    def get_queue(player: wavelink.Player) -> list[wavelink.Playable]:

        return list(player.queue)

    # REBUILD QUEUE
    @staticmethod
    def rebuild_queue(player: wavelink.Player,
                      tracks: list[wavelink.Playable]):

        player.queue.clear()

        for track in tracks:

            player.queue.put(track)

    # REMOVE BY INDEX
    @staticmethod
    def remove_index(player: wavelink.Player,
                     index: int) -> wavelink.Playable | None:

        queue = QueueManager.get_queue(player)

        if index < 1 or index > len(queue):
            return None

        removed = queue.pop(index - 1)

        QueueManager.rebuild_queue(player, queue)

        return removed

    # MASS REMOVE
    @staticmethod
    def mass_remove(player: wavelink.Player,
                    indexes: list[int]) -> list[wavelink.Playable]:

        queue = QueueManager.get_queue(player)

        removed_tracks = []

        # REMOVE FROM END
        for index in sorted(set(indexes), reverse=True):

            if (index < 1 or index > len(queue)):
                continue

            removed_tracks.append(queue.pop(index - 1))

        QueueManager.rebuild_queue(player, queue)

        return removed_tracks

    # GET PAGE
    @staticmethod
    def get_page(player: wavelink.Player,
                 page: int,
                 per_page: int = 10) -> list[wavelink.Playable]:

        queue = QueueManager.get_queue(player)

        start = page * per_page

        end = start + per_page

        return queue[start:end]

    # TOTAL PAGES
    @staticmethod
    def total_pages(player: wavelink.Player, per_page: int = 10) -> int:

        queue = QueueManager.get_queue(player)

        if not queue:
            return 1

        return ((len(queue) - 1) // per_page) + 1
