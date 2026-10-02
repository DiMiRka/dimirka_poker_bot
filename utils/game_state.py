from dataclasses import dataclass, field


@dataclass
class GameState:
    game_users: list[str] = field(default_factory=list)
    start_status: bool = False
    player_list: list[str] = field(default_factory=list)
    player_out_list: list[str] = field(default_factory=list)
    text_players: str = ''
    date: str = ''
    game_id: int = 0
    count: int = 0
    game_data: dict = field(default_factory=dict)
    add_bank_player: str = ''
    out_player: str = ''


games: dict[int, GameState] = {}


def get_game(chat_id: int) -> GameState:
    if chat_id not in games:
        games[chat_id] = GameState()
    return games[chat_id]


def reset_game(chat_id: int) -> GameState:
    games[chat_id] = GameState()
    return games[chat_id]
