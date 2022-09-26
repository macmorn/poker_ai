import collections
import copy
import random
from typing import List, Tuple, Optional

import pytest
import numpy as np
import dill as pickle

from poker_ai.games.aof.state import AOFPokerState
from poker_ai.games.aof.player import AOFPokerPlayer
from poker_ai.poker.card import Card
from poker_ai.poker.pot import Pot
from poker_ai.utils.random import seed
import logging

logger = logging.getLogger(__name__)

def _new_game(
    n_players: int,
    small_blind: int = 50,
    big_blind: int = 100,
    initial_chips: int = 800,
) -> Tuple[AOFPokerState, Pot]:
    """Create a new game."""
    pot = Pot()
    players = [
        AOFPokerPlayer(player_i=player_i, pot=pot, initial_chips=initial_chips)
        for player_i in range(n_players)
    ]
    state = AOFPokerState(
        players=players,
        use_lut=False,
        small_blind=small_blind,
        big_blind=big_blind,
    )
    return state, pot

def test_aof_2():
    """Test the aof poker game state works as expected."""
    n_players = 3
    state, _ = _new_game(n_players=3)
    player_i_order = [2, 0, 1]
    # Call for all players.
    for i in range(n_players):
        assert len(state.legal_actions) == 2
        assert state.betting_stage == "pre_flop"
        if i == 0:
            state = state.apply_action(action_str="all-in")
        else:
            state = state.apply_action(action_str="fold")
    # Only one player left, so game state should be terminal.
    assert state.is_terminal, "state was not terminal"
    assert state.betting_stage == "terminal"
    
