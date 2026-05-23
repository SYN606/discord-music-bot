import wavelink
from config import settings


async def connect_lavalink(bot):

    node = wavelink.Node(
        uri=settings.lavalink_uri(),
        password=settings.LAVALINK_PASSWORD,
    )

    await wavelink.Pool.connect(
        nodes=[node],
        client=bot,
    )

    print("✓ Lavalink connected")
