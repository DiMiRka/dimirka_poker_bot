from datetime import date
from typing import List
from sqlalchemy import text, JSON, String, Integer, Table, Column, ForeignKey, Date
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
    date: Mapped[date] = mapped_column(
        Date,
        server_default=text("CURRENT_DATE"),
        nullable=False
    )
    count: Mapped[int]
    game: Mapped[JSON] = mapped_column(JSON, default={})

    players: Mapped[List["Player"]] = relationship(
        "Player",
        secondary=game_player,
        back_populates="games_played",
        lazy="selectin"
    )

    @property
    def formatted_date(self) -> str:
        """Возвращает дату в формате '23 мая 2025 г.'"""
        month_names = [
            "января", "февраля", "марта", "апреля", "мая", "июня",
            "июля", "августа", "сентября", "октября", "ноября", "декабря"
        ]
        return f"{self.date.day} {month_names[self.date.month - 1]} {self.date.year} г."

    @property
    def to_dict(self) -> dict:
        """Возвращает словарь python"""
        return {
            "id": self.id,
            "date": self.formatted_date,
            "count": self.count,
            "game": self.game
        }


class Player(Base):
    __tablename__ = "players"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, index=True)
    login: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    games: Mapped[int] = mapped_column(Integer, default=0)
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
