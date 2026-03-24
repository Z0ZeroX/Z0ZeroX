import os
import re
from collections import defaultdict
from urllib.parse import urlencode
import chess
from .utils import PIECE_IMAGES, create_markdown_link, load_settings
from .data_store import read_top_moves, read_last_moves


def render_board_to_markdown(board):
    board_list = [[item for item in line.split(' ')] for line in str(board).split('\n')]
    markdown = ""

    if board.turn == chess.BLACK:
        markdown += "|   | H | G | F | E | D | C | B | A |   |\n"
    else:
        markdown += "|   | A | B | C | D | E | F | G | H |   |\n"
    markdown += "|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|\n"

    rows = range(1, 9)
    if board.turn == chess.BLACK:
        rows = reversed(rows)

    for row in rows:
        markdown += "| **" + str(9 - row) + "** | "
        columns = board_list[row - 1]
        if board.turn == chess.BLACK:
            columns = reversed(columns)

        for piece in columns:
            markdown += "<img src=\"{}\" width=50px> | ".format(PIECE_IMAGES.get(piece, "???"))

        markdown += "**" + str(9 - row) + "** |\n"

    if board.turn == chess.BLACK:
        markdown += "|   | **H** | **G** | **F** | **E** | **D** | **C** | **B** | **A** |   |\n"
    else:
        markdown += "|   | **A** | **B** | **C** | **D** | **E** | **F** | **G** | **H** |   |\n"

    return markdown


def render_moves_list(board):
    settings = load_settings()
    
    moves_dict = defaultdict(set)
    for move in board.legal_moves:
        source = chess.SQUARE_NAMES[move.from_square].upper()
        dest = chess.SQUARE_NAMES[move.to_square].upper()
        moves_dict[source].add(dest)

    markdown = ""

    if board.is_game_over():
        issue_link = settings['issues']['link'].format(
            repo=os.environ["GITHUB_REPOSITORY"],
            params=urlencode(settings['issues']['new_game']))

        new_game_image = "[![Start New Game](assets/new_game.png)]({})".format(issue_link)
        return "**GAME IS OVER!**\n\n" + new_game_image + "\n"

    if board.is_check():
        markdown += "**CHECK!** Choose your move wisely!\n"

    color_icon, color_name = (":white_circle:", "WHITE (solid)") if board.turn == chess.WHITE else (":black_circle:", "BLACK (hollow)")
    markdown += f"{color_icon} {color_name}: It's your turn to move! Choose one from the following table:\n\n"

    markdown += "|  FROM  | TO (Just click a link!) |\n"
    markdown += "| :----: | :---------------------- |\n"

    for source, dest in sorted(moves_dict.items()):
        markdown += "| **" + source + "** | " + _create_issue_link(source, dest) + " |\n"

    return markdown


def render_last_moves():
    settings = load_settings()
    markdown = "\n"
    markdown += "| Move | Author |\n"
    markdown += "| :--: | :----- |\n"

    counter = 0

    for line in read_last_moves():
        parts = line.rstrip().split(':')

        if ":" not in line:
            continue

        if counter >= settings['misc']['max_last_moves']:
            break

        counter += 1

        move_match = re.search('([A-H][1-8])([A-H][1-8])', line, re.I)
        if move_match is not None:
            source = move_match.group(1).upper()
            dest = move_match.group(2).upper()
            
            color_icon = ''
            if len(parts) >= 3:
                color_code = parts[2].strip()
                color_icon = ' ⚪' if color_code == 'W' else ' ⚫'
            
            markdown += "| `" + source + "` to `" + dest + "` | " + create_markdown_link(parts[1].strip(), "https://github.com/" + parts[1].strip()[1:]) + color_icon + "|\n"
        else:
            markdown += "| `" + parts[0] + "` | " + create_markdown_link(parts[1].strip(), "https://github.com/" + parts[1].strip()[1:]) + " |\n"

    return markdown + "\n"


def render_top_moves():
    settings = load_settings()
    player_moves_count = read_top_moves()

    markdown = "\n"
    markdown += "| Total moves |  User  |\n"
    markdown += "| :---------: | :----- |\n"

    max_entries = settings['misc']['max_top_moves']
    for username, move_count in sorted(player_moves_count.items(), key=lambda x: x[1], reverse=True)[:max_entries]:
        markdown += "| {} | {} |\n".format(move_count, create_markdown_link(username, "https://github.com/" + username[1:]))

    return markdown + "\n"


def _create_issue_link(source, dest_list):
    settings = load_settings()
    
    issue_link = settings['issues']['link'].format(
        repo=os.environ["GITHUB_REPOSITORY"],
        params=urlencode(settings['issues']['move'], safe="{}"))

    move_links = [create_markdown_link(dest, issue_link.format(source=source, dest=dest)) for dest in sorted(dest_list)]
    return ", ".join(move_links)