from sqlalchemy import Column, Integer, String
from database.base import Base


class GuildConfig(Base):
    __tablename__ = "guild_config"
    id = Column(Integer, primary_key=True)
    guild_id = Column(String, unique=True, nullable=False)
    admin_role = Column(String, default="Admin")
    def __repr__(self):
        return f"<GuildConfig guild_id={self.guild_id}>"