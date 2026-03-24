import os
import ast
import chess
from datetime import datetime
from .utils import PATHS, load_settings, replace_text_between


def update_top_moves(user):
    os.makedirs(os.path.dirname(PATHS['top_moves']), exist_ok=True)
    
    if not os.path.exists(PATHS['top_moves']):
        player_moves_count = {}
    else:
        with open(PATHS['top_moves'], 'r') as file:
            file_content = file.read()
            player_moves_count = ast.literal_eval(file_content) if file_content else {}

    if user not in player_moves_count:
        player_moves_count[user] = 1
    else:
        player_moves_count[user] += 1

    with open(PATHS['top_moves'], 'w') as file:
        file.write(str(player_moves_count))


def update_last_moves(line):
    with open(PATHS['last_moves'], 'r+') as last_moves:
        existing_content = last_moves.read()
        last_moves.seek(0, 0)
        last_moves.write(line.rstrip('\r\n') + '\n' + existing_content)


def get_last_player_and_move():
    if not os.path.exists(PATHS['last_moves']):
        return None, None
    with open(PATHS['last_moves']) as moves:
        line = moves.readline()
        if not line:
            return None, None
        last_player = line.split(':')[1].strip()
        last_move = line.split(':')[0].strip()
        return last_player, last_move


def save_game_to_file(game):
    os.makedirs(os.path.dirname(PATHS['current_game']), exist_ok=True)
    print(game, file=open(PATHS['current_game'], 'w'), end='\n\n')


def create_new_last_moves_file(initial_content):
    os.makedirs(os.path.dirname(PATHS['last_moves']), exist_ok=True)
    with open(PATHS['last_moves'], 'w') as last_moves:
        last_moves.write(initial_content)


def archive_current_game():
    if not os.path.exists(PATHS['current_game']):
        return
    timestamp = datetime.now().strftime(PATHS['archived_games'] + 'game-%Y%m%d.pgn')
    os.rename(PATHS['current_game'], timestamp)
    if os.path.exists(PATHS['last_moves']):
        os.remove(PATHS['last_moves'])


def get_game_statistics():
    import re
    
    if not os.path.exists(PATHS['last_moves']):
        return set(), 0, 0
    
    with open(PATHS['last_moves'], 'r') as last_moves_file:
        lines = last_moves_file.readlines()
        if not lines:
            return set(), 0, 0
        pattern = re.compile('.*: (@[a-z\\d](?:[a-z\\d]|-(?=[a-z\\d])){0,38})', flags=re.I)
        player_list = {re.match(pattern, line).group(1) for line in lines if ':' in line}
        
    return player_list, len(lines) - 1, len(player_list)


def read_top_moves():
    if not os.path.exists(PATHS['top_moves']):
        return {}
    with open(PATHS['top_moves'], 'r') as file:
        file_content = file.read().strip()
        return ast.literal_eval(file_content) if file_content else {}


def read_last_moves():
    if not os.path.exists(PATHS['last_moves']):
        return []
    with open(PATHS['last_moves'], 'r') as file:
        return file.readlines()


def update_readme_file(gameboard, settings, last_moves):
    from . import renderer
    
    with open(PATHS['readme'], 'r') as file:
        readme = file.read()
        readme = replace_text_between(readme, settings['markers']['board'], '{chess_board}')
        readme = replace_text_between(readme, settings['markers']['moves'], '{moves_list}')
        readme = replace_text_between(readme, settings['markers']['turn'], '{turn}')
        readme = replace_text_between(readme, settings['markers']['last_moves'], '{last_moves}')
        readme = replace_text_between(readme, settings['markers']['top_moves'], '{top_moves}')

    with open(PATHS['readme'], 'w') as file:
        file.write(readme.format(
            chess_board=renderer.render_board_to_markdown(gameboard),
            moves_list=renderer.render_moves_list(gameboard),
            turn=('WHITE' if gameboard.turn == chess.WHITE else 'BLACK'),
            last_moves=last_moves,
            top_moves=renderer.render_top_moves()))