from __future__ import annotations
import wavelink


class QueueManager:

    @staticmethod
    async def add_track(player: wavelink.Player, track: wavelink.Playable):
        player.queue.put(track)

    @staticmethod
    async def add_playlist(player: wavelink.Player,
                           playlist: wavelink.Playlist):
        for track in playlist.tracks:
            player.queue.put(track)

    @staticmethod
    async def get_next(player: wavelink.Player) -> wavelink.Playable | None:
        if player.queue.is_empty:
            return None
        return await player.queue.get_wait()

    @staticmethod
    def clear(player: wavelink.Player):
        player.queue.clear()

    @staticmethod
    def count(player: wavelink.Player) -> int:
        return player.queue.count

    @staticmethod
    def get_queue(player: wavelink.Player) -> list[wavelink.Playable]:
        return list(player.queue)

    @staticmethod
    def rebuild_queue(player: wavelink.Player,
                      tracks: list[wavelink.Playable]):
        player.queue.clear()
        for track in tracks:
            player.queue.put(track)

    @staticmethod
    def remove_index(player: wavelink.Player,
                     index: int) -> wavelink.Playable | None:
        queue = QueueManager.get_queue(player)
        if (index < 1 or index > len(queue)):
            return None
        removed = queue.pop(index - 1)
        QueueManager.rebuild_queue(player, queue)
        return removed

    @staticmethod
    def mass_remove(player: wavelink.Player,
                    indexes: list[int]) -> list[wavelink.Playable]:
        queue = QueueManager.get_queue(player)
        removed_tracks: list[wavelink.Playable] = []
        for index in sorted(set(indexes), reverse=True):
            if (index < 1 or index > len(queue)):
                continue
            removed_tracks.append(queue.pop(index - 1))
        QueueManager.rebuild_queue(player, queue)
        return removed_tracks

    @staticmethod
    def get_page(player: wavelink.Player,
                 page: int,
                 per_page: int = 10) -> list[wavelink.Playable]:
        queue = QueueManager.get_queue(player)
        start = page * per_page
        end = start + per_page
        return queue[start:end]

    @staticmethod
    def total_pages(player: wavelink.Player, per_page: int = 10) -> int:
        queue_count = QueueManager.count(player)
        if queue_count <= 0:
            return 1

        return ((queue_count - 1) // per_page) + 1

    # SHUFFLE QUEUE
    @staticmethod
    def shuffle(player: wavelink.Player):
        queue = QueueManager.get_queue(player)
        if len(queue) <= 1:
            return
        import random
        random.shuffle(queue)
        QueueManager.rebuild_queue(player, queue)

    @staticmethod
    def move_track(player: wavelink.Player, source_index: int,
                   target_index: int) -> bool:
        queue = QueueManager.get_queue(player)
        queue_length = len(queue)
        if (source_index < 1 or source_index > queue_length):
            return False
        if (target_index < 1 or target_index > queue_length):
            return False
        track = queue.pop(source_index - 1)
        queue.insert(target_index - 1, track)
        QueueManager.rebuild_queue(player, queue)
        return True

    @staticmethod
    def swap_tracks(player: wavelink.Player, first_index: int,
                    second_index: int) -> bool:
        queue = QueueManager.get_queue(player)
        queue_length = len(queue)
        if (first_index < 1 or first_index > queue_length):
            return False
        if (second_index < 1 or second_index > queue_length):
            return False
        first = first_index - 1
        second = second_index - 1
        queue[first], queue[second] = (queue[second], queue[first])
        QueueManager.rebuild_queue(player, queue)
        return True

    @staticmethod
    def remove_duplicates(player: wavelink.Player) -> int:
        queue = QueueManager.get_queue(player)
        seen: set[str] = set()
        unique_tracks: list[wavelink.Playable] = []
        removed_count = 0
        for track in queue:
            identifier = getattr(track, "identifier", track.title)
            if identifier in seen:
                removed_count += 1
                continue
            seen.add(identifier)
            unique_tracks.append(track)
        QueueManager.rebuild_queue(player, unique_tracks)
        return removed_count
