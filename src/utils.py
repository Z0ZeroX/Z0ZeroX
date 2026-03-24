import os
from enum import Enum
import yaml


class Action(Enum):
    UNKNOWN = 0
    MOVE = 1
    NEW_GAME = 2


PATHS = {
    'settings': 'data/config/settings.yaml',
    'top_moves': 'data/moves/top_moves.txt',
    'last_moves': 'data/moves/last_moves.txt',
    'current_game': 'games/current.pgn',
    'archived_games': 'games/history/',
    'readme': 'README.md'
}

PIECE_IMAGES = {
    "r": "assets/chess/r.png",
    "n": "assets/chess/n.png", 
    "b": "assets/chess/b.png",
    "q": "assets/chess/q.png",
    "k": "assets/chess/k.png",
    "p": "assets/chess/p.png",
    "R": "assets/chess/R.png",
    "N": "assets/chess/N.png",
    "B": "assets/chess/B.png", 
    "Q": "assets/chess/Q.png",
    "K": "assets/chess/K.png",
    "P": "assets/chess/P.png",
    ".": "assets/chess/blank.png"
}

WIN_MESSAGES = {
    '1/2-1/2': 'It\'s a draw',
    '1-0': 'White wins', 
    '0-1': 'Black wins'
}


def load_settings():
    with open(PATHS['settings'], 'r') as settings_file:
        return yaml.load(settings_file, Loader=yaml.FullLoader)


def replace_text_between(original_text, marker, replacement_text):
    delimiter_a = marker['begin']
    delimiter_b = marker['end']

    if original_text.find(delimiter_a) == -1 or original_text.find(delimiter_b) == -1:
        return original_text

    leading_text = original_text.split(delimiter_a)[0]
    trailing_text = original_text.split(delimiter_b)[1]

    return leading_text + delimiter_a + replacement_text + delimiter_b + trailing_text


def create_markdown_link(text, url):
    return f"[{text}]({url})"