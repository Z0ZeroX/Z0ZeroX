import os
import chess
from .utils import Action, load_settings, PATHS
from .chess_game import (
    parse_issue, create_new_game, load_current_game, is_valid_move, 
    execute_move, is_consecutive_move, get_move_labels, 
    is_game_over_and_get_result, is_board_valid
)
from .data_store import (
    update_top_moves, update_last_moves, save_game_to_file, 
    archive_current_game, create_new_last_moves_file, 
    get_last_player_and_move, get_game_statistics, update_readme_file
)
from .renderer import render_last_moves


def handle_new_game(issue, issue_author, repo_owner, settings):
    if os.path.exists(PATHS['current_game']) and issue_author != repo_owner:
        issue.create_comment(settings['comments']['invalid_new_game'].format(author=issue_author))
        issue.edit(state='closed')
        return False, 'ERROR: A current game is in progress. Only the repo owner can start a new game'

    issue.create_comment(settings['comments']['successful_new_game'].format(author=issue_author))
    issue.edit(state='closed')

    create_new_last_moves_file('Start game: ' + issue_author)
    game = create_new_game(repo_owner)
    gameboard = chess.Board()
    
    return True, (game, gameboard)


def handle_move(issue, issue_author, action, settings):
    if not os.path.exists(PATHS['current_game']):
        issue.create_comment(f"{issue_author} Sorry, there is no game in progress! [Click here](https://github.com/{os.environ['GITHUB_REPOSITORY']}/issues/new?body=Please+do+not+change+the+title.+Just+click+%22Submit+new+issue%22.+You+don%27t+need+to+do+anything+else+%3AD&title=Chess%3A+Start+new+game) to start a new game.")
        issue.edit(state='closed', labels=['Invalid'])
        return False, 'ERROR: There is no game in progress! Start a new game first'

    game, gameboard = load_current_game()
    last_player, last_move = get_last_player_and_move()

    if is_consecutive_move(last_player, issue_author, last_move):
        issue.create_comment(settings['comments']['consecutive_moves'].format(author=issue_author))
        issue.edit(state='closed', labels=['Invalid'])
        return False, 'ERROR: Two moves in a row!'

    valid_move = is_valid_move(gameboard, action[1])
    if not valid_move:
        issue.create_comment(settings['comments']['invalid_move'].format(author=issue_author, move=action[1]))
        issue.edit(state='closed', labels=['Invalid'])
        return False, 'ERROR: Move is invalid!'

    if not is_board_valid(gameboard):
        issue.create_comment(settings['comments']['invalid_board'].format(author=issue_author))
        issue.edit(state='closed', labels=['Invalid'])
        return False, 'ERROR: Board is invalid!'

    issue_labels = get_move_labels(gameboard, valid_move)
    issue.create_comment(settings['comments']['successful_move'].format(author=issue_author, move=valid_move))
    issue.edit(state='closed', labels=issue_labels)

    color_code = 'W' if gameboard.turn == chess.WHITE else 'B'
    update_last_moves(f"{valid_move}:{issue_author}:{color_code}")
    update_top_moves(issue_author)

    game, gameboard = execute_move(game, gameboard, valid_move, issue_author)
    
    return True, (game, gameboard)


def handle_unknown_action(issue, issue_author, settings):
    issue.create_comment(settings['comments']['unknown_command'].format(author=issue_author))
    issue.edit(state='closed', labels=['Invalid'])
    return False, 'ERROR: Unknown action'


def handle_game_over(issue, gameboard, settings):
    game_over, outcome = is_game_over_and_get_result(gameboard)
    
    if not game_over:
        return
    
    player_list, num_moves, num_players = get_game_statistics()

    if gameboard.result() == '1/2-1/2':
        issue.add_to_labels('👑 Draw!')
    else:
        issue.add_to_labels('👑 Winner!')

    issue.create_comment(settings['comments']['game_over'].format(
        outcome=outcome,
        players=', '.join(player_list),
        num_moves=num_moves,
        num_players=num_players))

    archive_current_game()


def process_game_action(issue, issue_author, repo_owner):
    action = parse_issue(issue.title)
    settings = load_settings()
    
    if action[0] == Action.NEW_GAME:
        result, data = handle_new_game(issue, issue_author, repo_owner, settings)
        if not result:
            return False, data
        game, gameboard = data
        
    elif action[0] == Action.MOVE:
        result, data = handle_move(issue, issue_author, action, settings)
        if not result:
            return False, data
        game, gameboard = data
        
    elif action[0] == Action.UNKNOWN:
        return handle_unknown_action(issue, issue_author, settings)
    
    save_game_to_file(game)
    last_moves = render_last_moves()
    handle_game_over(issue, gameboard, settings)
    update_readme_file(gameboard, settings, last_moves)
    
    return True, ''