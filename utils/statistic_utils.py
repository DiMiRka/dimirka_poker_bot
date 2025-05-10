import pandas as pd
import matplotlib.pyplot as plt
import json

from db_hadler.db_class import Database


async def update_player_statistics(choice):
    """Обновляем статистику игроков из всех игр базы данных.
    Оформляем таблицу статистику игроков для вывода"""
    if choice == "общая cтатистика игроков":
        games = await Database.get_all_games()
    else:
        games = await Database.get_games()
    statistic_not_sorted = dict()
    for game in games:
        game = json.loads(game)
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
            # statistic_not_sorted[player]['winrate'] = f'{int(winrate)} %'
    await Database.update_player_statistics(statistic_not_sorted)
    statistics_list_not_sorted = await Database.get_statistics()
    statistics_list_sorted = list()
    for x in statistics_list_not_sorted:
        statistics_list_sorted.append({
            'Игрок': x[1],
            'Игр': x[2],
            'Побед': x[3],
            'В ноль': x[4],
            'Проёб': x[5],
            'Винрейт': x[6],
            'Результат': str(x[7]) + ' руб.'
        })
    table_statistics = dict()
    for n in statistics_list_sorted:
        for k, v in n.items():
            table_statistics.setdefault(k, []).append(v)
    print(table_statistics)
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
