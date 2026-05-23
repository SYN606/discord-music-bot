from database.crud.base import BaseCRUD
from database.models import GuildConfig


class GuildCRUD(BaseCRUD):
    model = GuildConfig

    # GET OR CREATE GUILD
    @classmethod
    async def get_or_create(cls, guild_id: int | str):

        guild = await cls.get(
            guild_id=str(guild_id),
        )

        if guild:
            return guild

        return await cls.create(
            guild_id=str(guild_id),
        )

    # GET PREFIX
    @classmethod
    async def get_prefix(cls, guild_id: int | str):

        guild = await cls.get_or_create(
            guild_id,
        )

        return guild.prefix  # type: ignore

    # SET PREFIX
    @classmethod
    async def set_prefix(
        cls,
        guild_id: int | str,
        prefix: str,
    ):

        return await cls.update(
            {"guild_id": str(guild_id)},
            {"prefix": prefix},
        )

    # GET DJ ROLE
    @classmethod
    async def get_dj_role(
        cls,
        guild_id: int | str,
    ):

        guild = await cls.get_or_create(
            guild_id,
        )

        return guild.dj_role  # type: ignore

    # SET DJ ROLE
    @classmethod
    async def set_dj_role(
        cls,
        guild_id: int | str,
        role_id: int | str,
    ):

        return await cls.update(
            {"guild_id": str(guild_id)},
            {"dj_role": str(role_id)},
        )

    # GET DEFAULT VOLUME
    @classmethod
    async def get_volume(
        cls,
        guild_id: int | str,
    ):

        guild = await cls.get_or_create(
            guild_id,
        )

        return guild.default_volume  # type: ignore

    # SET DEFAULT VOLUME
    @classmethod
    async def set_volume(
        cls,
        guild_id: int | str,
        volume: int,
    ):

        return await cls.update(
            {"guild_id": str(guild_id)},
            {"default_volume": volume},
        )

    # GET 24/7 MODE
    @classmethod
    async def is_247_enabled(
        cls,
        guild_id: int | str,
    ):

        guild = await cls.get_or_create(
            guild_id,
        )

        return guild.twenty_four_seven  # type: ignore

    # TOGGLE 24/7 MODE
    @classmethod
    async def set_247(
        cls,
        guild_id: int | str,
        state: bool,
    ):

        return await cls.update(
            {"guild_id": str(guild_id)},
            {"twenty_four_seven": state},
        )