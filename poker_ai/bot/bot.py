import json
import time
import numpy as np
from ggpoker_client import AoF_Client
import click
from poker_ai.poker.card import Card
from poker_ai.clustering.preflop import make_starting_hand_lossless
from poker_ai.utils import algos, io

import joblib

import logging

"""
def play_aof_sit_go_holdem(quadrant):
    client = GGPokerClient()
    client.connect()
    client.join_table(quadrant)
    client.start_game()
    client.play_hand()
    client.leave_table()
    client.disconnect()
"""

class DecisionModel:
    """_summary_
    """
    def __init__(
        self,
        path_model: str,
        round_preflop: int =5,
        round_flop: int =100,
        use_bet_ratio: bool = True,
        ):
        """Class to query a decision model.

        Args:
            path_model (str): path to joblib file with game model.
            round_preflop (int, optional): Model parameter to which mumber card rank is roundned in the preflop. Defaults to 5.
            round_flop (int, optional): Model parameter to which mumber card rank is roundned in the preflop. Defaults to 100.
            use_bet_ratio (bool, optional): Flag if bet ratio is included in the query. Defaults to True.
        """

        self.path_model = path_model
        self._round_preflop = round_preflop
        self._round_flop = round_flop
        self.use_bet_ratio = use_bet_ratio
        self.model=self._load_agent()
        self._dealer=None

    def _load_agent(self):
        with open(self.path_model, "rb") as input_file:
            offline_strategy_dict = joblib.load(input_file)
        return offline_strategy_dict

    def _to_probability(self, strat: dict):
        norm = sum(strat.values())
        for a in strat.keys():
            strat[a] /= norm
        a = np.random.choice(
            list(strat.keys()), 1, p=list(strat.values()),
        )[0]
        logging.debug(f"Probabilities: {strat.values()}")
        return a

    def max_probability(self, strat: dict):
        norm = sum(strat.values())
        for a in strat.keys():
            strat[a] /= norm
        a = max(strat,key=strat.get)
        logging.debug(f"Probabilities: {strat.values()}")
        return a

    def query(self, 
            num_players: int,
            my_bet: float,
            max_bet:float,
            hand_cards: list,
            board_cards: list = [],
            pre_flop_history: list = [],
            flop_history: list = [],
            turn_history: list = [],
            river_history: list = [],
            ):

        history=[]
        if pre_flop_history:
            history.append({"pre_flop": pre_flop_history})
        if flop_history:
            history.append({"flop": flop_history})
        if turn_history:
            history.append({"turn": turn_history})
        if river_history:
            history.append({"river": river_history})

    
        #check if we are in flop already 
        if board_cards==[]:

            card_cluster= make_starting_hand_lossless(hand_cards, short_deck=False)
            rank=algos.round_to_nearest_n(card_cluster,self._round_preflop)

        else:
            Exception("Flop not implemented yet")
        if max_bet==0:
            portion_bet=0.0
        else:
            portion_bet=algos.round_to_nearest_element(my_bet/max_bet)


        query_dict={
            "n_players": num_players,
            "cards_cluster": rank,
            "portion_bet": portion_bet,
            "history": history,
        }
        #lifted from inof_state, where th index ist first generated
        query= json.dumps(
            query_dict, separators=(",", ":"), cls=io.NumpyJSONEncoder
        )
        logging.info(f"Query: {query}")
        #return strategy
        try:
            return self.model[query]
        except:
            logging.error("Could not find strategy for query, saving query for analysis")
            with open("debug/failed_queries.txt", "a") as f:
                f.write(query+"\n")



def start(models_path: str, scale = 1.0):
    model= DecisionModel(path_model=models_path)
    client = AoF_Client(scale= scale)
    is_game_over=client.is_game_over
    while is_game_over == False:
        play_round(client, model)
        is_game_over=client.is_game_over
    
    


#super crude playing function
def play_round(client : AoF_Client, model: DecisionModel):
            client.wait_for_round_start()
            #round switch triggered by me getting closed cards
            client.current_round+=1
            logging.info(f"Round {client.current_round} has started")
            #get player orders
            player_order=client.get_player_order()
            logging.info(f"Player order:{player_order}")
            preflop_history=[]
            bets=[]
            #watch for player actions and record them
            for i in player_order:
                if i=="0":
                    break
                action=client.watch_player_action(i)
                #if player didnt fold add the bet to the list
                if action!="fold":
                    client._update_window_screenshot()
                    bet=client.get_player_bet_amount(i)
                    if bet==0:
                        logging.error("Could not get bet amount")
                    else:
                        bets.append(bet)
                        logging.info(bet)
                    #logging.info(f"Player {i} bet {bets[-1]}")
                logging.info(action)
                
                preflop_history.append(action)
            logging.info(f"Preflop history: {preflop_history}")    
            #ideally parallelize this
            client._update_window_screenshot()
            #continue only if im not only player
            if client.get_active_players() != ["0"]:
                hand=client.get_player_cards(threshold=0.6)
                while len(hand)!=2:
                    time.sleep(1)
                    client._update_window_screenshot()
                    hand=client.get_player_cards()
                logging.info(f"My cards: {hand}")
                #get my bet and pot for the current round
                client._update_window_screenshot()
                my_bet=client.get_player_bet_amount("0")
                my_pot=client.get_player_chips_amount("0")
                logging.info(f"My bet: {my_bet}")
                logging.info(f"My pot: {my_pot}")
                #get max bet
                if bets != []:
                    max_bet=max(bets)
                else:
                    max_bet=my_pot
                logging.info(f"Bets: {bets}")    
                logging.info(f"Max bet: {max_bet}")
                #get number of players
                n_players= len(player_order)
                strat=model.query(
                    num_players=n_players,
                    my_bet=my_bet,
                    max_bet=max_bet,
                    hand_cards=hand,
                    pre_flop_history=preflop_history
                )
                logging.info(f"Strategy: {strat}")
                #get action
                if strat:
                    action= model.max_probability(strat)
                    logging.info(f"Action: {action}")
                    
                    if click.confirm(f'Do you want to {action}?', default=True):
                        #hotfix
                        if action=="all-in":
                            action="all_in"

                        client.take_action(action)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    start(models_path="poker_ai/bot/models/aof_avg_round_5_2022_10_06_09_16_11_546798.joblib", scale = 1)
    #SHOULD I MAYBE JSUT COMBINE ALL SIMILAR MODELS AND INFERENCE THEM BY n_palyers?