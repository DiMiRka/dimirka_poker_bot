import pandas as pd
import matplotlib.pyplot as plt
import json

from servise import get_games_db, update_player_db, get_players_db


async def update_player_statistics():
    """Обновляем статистику игроков из всех игр базы данных.
    Оформляем таблицу статистику игроков для вывода"""
    games = await get_games_db()
    # Собираем актуальную статистику игроков из игр и обновляем данные игрока в бд
    statistic_not_sorted = dict()
    for game in games:
        for player, result in game.items():
            if result.get('Руб.') > 0:
                win, loss, draw = 1, 0, 0
            elif result.get('Руб.') < 0:
                win, loss, draw = 0, 1, 0
            else:
                win, loss, draw = 0, 0, 1
            if statistic_not_sorted and player in statistic_not_sorted.keys():
                statistic_not_sorted[player] = {
                    'games': statistic_not_sorted[player]['games'] + 1,
                    'win': statistic_not_sorted[player]['win'] + win,
                    'draw': statistic_not_sorted[player]['draw'] + draw,
                    'loss': statistic_not_sorted[player]['loss'] + loss,
                    'winrate': str,
                    'earned': statistic_not_sorted[player]['earned'] + result.get('Руб.')
                }
            else:
                statistic_not_sorted[player] = {
                    'games': 1,
                    'win': win,
                    'draw': draw,
                    'loss': loss,
                    'winrate': str,
                    'earned': result.get('Руб.')
                }
            statistic_not_sorted[player]['winrate'] = str(round((statistic_not_sorted[player]['win'] / statistic_not_sorted[player]['games'] * 100), 2)) + ' %'
    await update_player_db(statistic_not_sorted)

    # Берем актуальную статистику игроков из бд
    statistics_list = await get_players_db()
    statistics_list = sorted(statistics_list, key=lambda user: user.earned, reverse=True)
    statistics_list = [{
        'Игрок': player.login,
        'Игр': player.games,
        'Побед': player.win,
        'В ноль': player.draw,
        'Проёб': player.loss,
        'Винрейт': player.winrate,
        'Результат': str(player.earned) + ' руб.'
    } for player in statistics_list]

    # Создаем таблицу pandas для представления
    table_statistics = dict()
    for n in statistics_list:
        for k, v in n.items():
            table_statistics.setdefault(k, []).append(v)
    tb = pd.DataFrame.from_dict(table_statistics)
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.set_size_inches(8, 8)
    fig.canvas.manager.full_screen_toggle()
    fig.set_facecolor('#4f4f4f')
    ax.axis('tight')
    ax.axis('off')
    ax.table(cellText=tb.values,
             colLabels=tb.columns,
             loc='center',
             cellLoc='center',
             rowLoc='center',
             colColours=['YellowGreen'] * 7)
    plt.savefig(f'statistics_image.png', bbox_inches='tight')
    print(tb)
    return None
