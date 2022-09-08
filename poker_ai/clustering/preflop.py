from typing import Dict, Tuple, List
import operator
from itertools import combinations

from poker_ai.poker.card import Card

RANK_INDEX= sorted(list(combinations(range(2,15),r=2)), key = lambda x:x[0] + x[1], reverse=True)

def make_starting_hand_lossless(starting_hand, short_deck = True) -> int:
    """"""
    #TODO: (Anton)Complete with indicator if short deck is used and extend logic to those values

    if short_deck:
        ranks = []
        suits = []
        for card in starting_hand:
            ranks.append(card.rank_int)
            suits.append(card.suit)
        if len(set(suits)) == 1:
            suited = True
        else:
            suited = False

            if all(c_rank == 14 for c_rank in ranks):
                return 0
            elif all(c_rank == 13 for c_rank in ranks):
                return 1
            elif all(c_rank == 12 for c_rank in ranks):
                return 2
            elif all(c_rank == 11 for c_rank in ranks):
                return 3
            elif all(c_rank == 10 for c_rank in ranks):
                return 4
            elif 14 in ranks and 13 in ranks:
                return 5 if suited else 15
            elif 14 in ranks and 12 in ranks:
                return 6 if suited else 16
            elif 14 in ranks and 11 in ranks:
                return 7 if suited else 17
            elif 14 in ranks and 10 in ranks:
                return 8 if suited else 18
            elif 13 in ranks and 12 in ranks:
                return 9 if suited else 19
            elif 13 in ranks and 11 in ranks:
                return 10 if suited else 20
            elif 13 in ranks and 10 in ranks:
                return 11 if suited else 21
            elif 12 in ranks and 11 in ranks:
                return 12 if suited else 22
            elif 12 in ranks and 10 in ranks:
                return 13 if suited else 23
            elif 11 in ranks and 10 in ranks:
                return 14 if suited else 24

    else:
        suits=set([card.suit for card in starting_hand])
        ranks=set([card.rank_int for card in starting_hand])
    if len(suits) == 1:
        suited = True
    else:
        suited = False
    if len(ranks) == 1:
        rank = ranks.pop()
        if rank == 14:
            return 0
        elif rank == 13:
            return 1
        elif rank == 12:
            return 2
        elif rank == 11:
            return 3
        elif rank == 10:
            return 4
        elif rank == 9:
            return 5
        elif rank == 8:
            return 6
        elif rank == 7:
            return 7
        elif rank == 6:
            return 8
        elif rank == 5:
            return 9
        elif rank == 4:
            return 10
        elif rank == 3:
            return 11
        elif rank == 2:
            return 12
    elif len(ranks) == 2:
        return 13+RANK_INDEX.index(tuple(sorted(ranks))) 



        

def compute_preflop_lossless_abstraction(builder) -> Dict[Tuple[Card, Card], int]:
    """Compute the preflop abstraction dictionary.

    Only works for the short deck presently.
    """

    # Getting combos and indexing with lossless abstraction
    preflop_lossless: Dict[Tuple[Card, Card], int] = {}
    for starting_hand in builder.starting_hands:
        starting_hand = sorted(
            list(starting_hand),
            key=operator.attrgetter("eval_card"),
            reverse=True
        )
        preflop_lossless[tuple(starting_hand)] = make_starting_hand_lossless(
            starting_hand, builder, short_deck=True
        )
    return preflop_lossless
