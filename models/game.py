from datetime import datetime
from sqlalchemy import TIMESTAMP, JSON, String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Game(Base):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, index=True)
    date: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    count: Mapped[int]
    game: Mapped[JSON] = mapped_column(JSON)


class Player(Base):
    __tablename__ = "players"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, index=True)
    login: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    games: Mapped[int] = mapped_column(Integer, default=0)
    win: Mapped[int] = mapped_column(Integer, default=0)
    draw: Mapped[int] = mapped_column(Integer, default=0)
    loss: Mapped[int] = mapped_column(Integer, default=0)
    winrate: Mapped[str] = mapped_column(String(20))
    earned: Mapped[int] = mapped_column(Integer, default=0)
