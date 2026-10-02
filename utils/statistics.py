def calculate_statistics(games: list[dict]) -> dict:
    statistics = {}
    for game in games:
        for player, result in game.items():
            earned = result['Руб.']
            totals = statistics.setdefault(player, {
                'games': 0, 'win': 0, 'draw': 0, 'loss': 0, 'earned': 0,
            })
            totals['games'] += 1
            totals['earned'] += earned
            if earned > 0:
                totals['win'] += 1
            elif earned < 0:
                totals['loss'] += 1
            else:
                totals['draw'] += 1
    for totals in statistics.values():
        totals['winrate'] = f"{round(totals['win'] / totals['games'] * 100, 2)} %"
    return statistics
