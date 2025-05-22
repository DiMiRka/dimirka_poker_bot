from datetime import datetime
from typing import List
from sqlalchemy import TIMESTAMP, JSON, String, Integer, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

game_player = Table(
    'game_player',
    Base.metadata,
    Column('game_id', ForeignKey('games.id'), primary_key=True),
    Column('player_id', ForeignKey('players.id'), primary_key=True)
)


class Game(Base):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, index=True)
    date: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    count: Mapped[int]
    game: Mapped[JSON] = mapped_column(JSON, default={})

    players: Mapped[List["Player"]] = relationship(
        "Player",
        secondary=game_player,
        back_populates="games_played",
        lazy="selectin"
    )


class Player(Base):
    __tablename__ = "players"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, index=True)
    login: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    games_count: Mapped[int] = mapped_column(Integer, default=0)
    win: Mapped[int] = mapped_column(Integer, default=0)
    draw: Mapped[int] = mapped_column(Integer, default=0)
    loss: Mapped[int] = mapped_column(Integer, default=0)
    winrate: Mapped[str] = mapped_column(String(20), default='0 %')
    earned: Mapped[int] = mapped_column(Integer, default=0)

    games_played: Mapped[List["Game"]] = relationship(
        "Game",
        secondary=game_player,
        back_populates="players",
        lazy="selectin"
    )
