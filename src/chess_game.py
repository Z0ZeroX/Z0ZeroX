import re
import os
import chess
import chess.pgn
from datetime import datetime
from .utils import Action, WIN_MESSAGES


def parse_issue(title):
    """Parse issue title and return (action, move) tuple"""
    if title.lower() == 'chess: start new game':
        return (Action.NEW_GAME, None)

    if 'chess: move' in title.lower():
        match_obj = re.match('Chess: Move ([A-H][1-8]) to ([A-H][1-8])', title, re.I)
        if match_obj:
            source = match_obj.group(1)
            dest = match_obj.group(2)
            return (Action.MOVE, (source + dest).lower())

    return (Action.UNKNOWN, None)


def create_new_game(repo_owner):
    game = chess.pgn.Game()
    game.headers['Event'] = f"@{repo_owner}'s Online Open Chess Tournament"
    game.headers['Site'] = 'https://github.com/' + os.environ['GITHUB_REPOSITORY']
    game.headers['Date'] = datetime.now().strftime('%Y.%m.%d')
    game.headers['Round'] = '1'
    game.headers['White'] = 'Collaborative Team White'
    game.headers['Black'] = 'Collaborative Team Black'
    game.headers['Result'] = '*'
    game.headers['GameType'] = 'Collaborative'
    game.headers['WhitePlayers'] = ''
    game.headers['BlackPlayers'] = ''
    return game


def load_current_game():
    from .utils import PATHS
    
    with open(PATHS['current_game']) as pgn_file:
        game = chess.pgn.read_game(pgn_file)
        gameboard = game.board()
        
        for move in game.mainline_moves():
            gameboard.push(move)
            
        return game, gameboard


def is_valid_move(gameboard, move_uci):
    """Check move validity, auto-promotes pawns to queen"""
    if chess.Move.from_uci(move_uci + 'q') in gameboard.legal_moves:
        return move_uci + 'q'
    
    move = chess.Move.from_uci(move_uci)
    if move in gameboard.legal_moves:
        return move_uci
        
    return None


def execute_move(game, gameboard, move_uci, player):
    move = chess.Move.from_uci(move_uci)
    
    is_white_turn = gameboard.turn == chess.WHITE
    team_key = 'WhitePlayers' if is_white_turn else 'BlackPlayers'
    
    current_players = game.headers.get(team_key, '')
    if player not in current_players:
        if current_players:
            game.headers[team_key] = current_players + f", {player}"
        else:
            game.headers[team_key] = player
    
    gameboard.push(move)
    
    game.end().add_main_variation(move, comment=f"Player: {player}")
    
    game.headers['Result'] = gameboard.result()
    
    return game, gameboard


def is_consecutive_move(last_player, current_player, last_move):
    if not last_player or not last_move:
        return False
    return last_player == current_player and 'Start game' not in last_move


def get_move_labels(gameboard, move):
    move_obj = chess.Move.from_uci(move)
    labels = ['⚔️ Capture!'] if gameboard.is_capture(move_obj) else []
    labels += ['White' if gameboard.turn == chess.WHITE else 'Black']
    return labels


def is_game_over_and_get_result(gameboard):
    if not gameboard.is_game_over():
        return False, None
        
    return True, WIN_MESSAGES.get(gameboard.result(), 'UNKNOWN')


def is_board_valid(gameboard):
    return gameboard.is_valid()