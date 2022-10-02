"""Script for using multiprocessing to train agent.

CLI Use
-------

Below you can run `python runner.py --help` to get the following description of
the two commands available in the CLI, `resume` and `search`:
```
Usage: poker_ai bot [OPTIONS]

  Run bot to play windo

Options:
    --game TEXT  Game to train on.  [required]
    --bot_path TEXT  Path to bot.  [required]
    --quadrant INTEGER  Quadrant to play in.  [required]
    --help       Show this message and exit.
```
"""


import cv2
import pyautogui
import time
import numpy as np
import click
from ggpoker_client import GGPokerClient

SUPPORTED_GAMES = ["aof_sit_go_holdem", "aof_regular_holdem", "spin_3p"]

@click.command()
@click.option('--game', required=False, default="aof_sit_go", type=str)
@click.option('--bot_path', required=False, type=str)
@click.option('--quadrant', required=False, default=1, type=int)

def run_bot(
    game: str,
    bot_path: str,
    quadrant: int,
):
        pass

if __name__ == "__main__":
    run_bot()