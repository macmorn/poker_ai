from typing import Dict, Tuple, List
import operator

from poker_ai.poker.card import Card

RANK_INDEX= {'Pair 14': 1,
 'Pair 13': 2,
 'Pair 12': 3,
 'Pair 11': 4,
 'Suited 1413': 5,
 'Pair 10': 6,
 'Suited 1412': 7,
 'Suited 1312': 8,
 'Suited 1411': 9,
 'Offsuit 1413': 10,
 'Suited 1311': 11,
 'Suited 1410': 12,
 'Suited 1211': 13,
 'Suited 1310': 14,
 'Offsuit 1412': 15,
 'Pair 9': 16,
 'Suited 1210': 17,
 'Offsuit 1312': 18,
 'Suited 1110': 19,
 'Offsuit 1411': 20,
 'Suited 149': 21,
 'Suited 148': 22,
 'Suited 139': 23,
 'Offsuit 1311': 24,
 'Pair 8': 25,
 'Offsuit 1410': 26,
 'Suited 147': 27,
 'Offsuit 1211': 28,
 'Suited 129': 29,
 'Suited 145': 30,
 'Suited 109': 31,
 'Suited 119': 32,
 'Suited 146': 33,
 'Suited 144': 34,
 'Offsuit 1310': 35,
 'Offsuit 1210': 36,
 'Suited 143': 37,
 'Offsuit 1110': 38,
 'Suited 138': 39,
 'Suited 137': 40,
 'Suited 142': 41,
 'Pair 7': 42,
 'Suited 128': 43,
 'Suited 108': 44,
 'Offsuit 149': 45,
 'Suited 135': 46,
 'Suited 98': 47,
 'Suited 118': 48,
 'Suited 136': 49,
 'Offsuit 139': 50,
 'Suited 134': 51,
 'Suited 127': 52,
 'Offsuit 148': 53,
 'Pair 6': 54,
 'Offsuit 109': 55,
 'Suited 87': 56,
 'Suited 107': 57,
 'Offsuit 129': 58,
 'Offsuit 119': 59,
 'Suited 117': 60,
 'Suited 97': 61,
 'Offsuit 145': 62,
 'Offsuit 147': 63,
 'Suited 126': 64,
 'Suited 125': 65,
 'Suited 133': 66,
 'Suited 132': 67,
 'Suited 124': 68,
 'Suited 76': 69,
 'Offsuit 144': 70,
 'Offsuit 146': 71,
 'Suited 86': 72,
 'Suited 123': 73,
 'Suited 96': 74,
 'Offsuit 138': 75,
 'Pair 5': 76,
 'Offsuit 143': 77,
 'Suited 106': 78,
 'Suited 122': 79,
 'Suited 115': 80,
 'Offsuit 108': 81,
 'Offsuit 128': 82,
 'Suited 65': 83,
 'Offsuit 137': 84,
 'Suited 116': 85,
 'Offsuit 118': 86,
 'Suited 75': 87,
 'Offsuit 142': 88,
 'Pair 4': 89,
 'Offsuit 98': 90,
 'Suited 114': 91,
 'Offsuit 136': 92,
 'Suited 85': 93,
 'Suited 105': 94,
 'Suited 54': 95,
 'Suited 113': 96,
 'Suited 64': 97,
 'Suited 95': 98,
 'Suited 112': 99,
 'Suited 104': 100,
 'Offsuit 135': 101,
 'Offsuit 127': 102,
 'Pair 3': 103,
 'Offsuit 87': 104,
 'Suited 103': 105,
 'Offsuit 107': 106,
 'Offsuit 134': 107,
 'Suited 74': 108,
 'Offsuit 97': 109,
 'Suited 53': 110,
 'Suited 102': 111,
 'Offsuit 117': 112,
 'Offsuit 126': 113,
 'Offsuit 133': 114,
 'Suited 84': 115,
 'Suited 94': 116,
 'Suited 63': 117,
 'Pair 2': 118,
 'Suited 93': 119,
 'Offsuit 76': 120,
 'Offsuit 125': 121,
 'Offsuit 132': 122,
 'Suited 43': 123,
 'Offsuit 106': 124,
 'Suited 92': 125,
 'Suited 73': 126,
 'Suited 52': 127,
 'Offsuit 116': 128,
 'Offsuit 86': 129,
 'Offsuit 96': 130,
 'Offsuit 124': 131,
 'Suited 83': 132,
 'Offsuit 65': 133,
 'Suited 62': 134,
 'Suited 42': 135,
 'Offsuit 123': 136,
 'Offsuit 75': 137,
 'Offsuit 115': 138,
 'Suited 82': 139,
 'Suited 72': 140,
 'Suited 32': 141,
 'Offsuit 54': 142,
 'Offsuit 114': 143,
 'Offsuit 122': 144,
 'Offsuit 85': 145,
 'Offsuit 105': 146,
 'Offsuit 95': 147,
 'Offsuit 113': 148,
 'Offsuit 64': 149,
 'Offsuit 104': 150,
 'Offsuit 112': 151,
 'Offsuit 53': 152,
 'Offsuit 74': 153,
 'Offsuit 103': 154,
 'Offsuit 84': 155,
 'Offsuit 102': 156,
 'Offsuit 43': 157,
 'Offsuit 94': 158,
 'Offsuit 63': 159,
 'Offsuit 93': 160,
 'Offsuit 52': 161,
 'Offsuit 73': 162,
 'Offsuit 92': 163,
 'Offsuit 83': 164,
 'Offsuit 42': 165,
 'Offsuit 82': 166,
 'Offsuit 62': 167,
 'Offsuit 32': 168,
 'Offsuit 72': 169}

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
    if len(ranks) == 1:
        index_key ="Pair " + str(max(ranks))
    else:
        if len(suits) == 1:
            index_key= "Suited"
        else:
            index_key= "Offsuit"
        rank_tuple=tuple(sorted(ranks))
        index_key += " " +str(rank_tuple[1])+str(rank_tuple[0])

    return RANK_INDEX[index_key]-1

        

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
