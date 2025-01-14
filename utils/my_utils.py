player_list = []
text_players = ''


def player_input(text):
    global player_list
    global text_players
    if text == 'новая игра':
        player_list =[]
        text_players = ''
    else:
        player_list.append(text)
        text_players += f'\n{text}'


def get_players():
    return player_list


def get_players_text():
    return text_players
