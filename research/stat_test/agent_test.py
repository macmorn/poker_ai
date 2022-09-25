from typing import List, Dict, DefaultDict
from pathlib import Path
import joblib
import collections

from tqdm import trange
import yaml
import datetime
import numpy as np
from scipy import stats
import re

from poker_ai.games.full_deck.state import ShortDeckPokerState, new_game
from poker_ai.poker.card import Card
from poker_ai.ai.ai import make_default_strategy, softmax_dict

def _get_index_neighbors(I:str, step: int = 1) -> List[str]:
    """Get the index of the neighbors of the current player."""
    up_neighbour= re.sub(r'\"cards_cluster\":(\d*),',lambda m: "\"cards_cluster\":"+str(int(m.group(1)) + step)+",", I)
    down_neighbour= re.sub(r'\"cards_cluster\":(\d*),',lambda m: "\"cards_cluster\":"+str(int(m.group(1)) - step)+",", I)

    return up_neighbour, down_neighbour


def _calculate_strategy(
        state: ShortDeckPokerState,
        I: str,
        strategy: DefaultDict[str, DefaultDict[str, float]],
        count=None,
        total_count=None
) -> str:
    sigma = collections.defaultdict(
        lambda: collections.defaultdict(lambda: 1 / 3)
    )
    # If strategy is empty, go to other block
    #sigma[I] = strategy[I].copy()
    try:
        sigma[I] = strategy.get(I, {})
        if sigma[I] == {}:
            if state.betting_stage == "pre_flop":
                up_I, down_I=_get_index_neighbors(I,1)
                sigma[I] = strategy.get(up_I, {})
                if sigma[I] == {}:
                    sigma[I] = strategy.get(down_I, {})
                    if sigma[I] == {}:
                        raise KeyError
            else:
                up_I, down_I=_get_index_neighbors(I,100)
                sigma[I] = strategy.get(up_I, {})
                if sigma[I] == {}:
                    sigma[I] = strategy.get(down_I, {})
                    if sigma[I] == {}:
                        raise KeyError
        norm = sum(sigma[I].values())
        for a in sigma[I].keys():
            sigma[I][a] /= norm
        a = np.random.choice(
            list(sigma[I].keys()), 1, p=list(sigma[I].values()),
        )[0]
    except KeyError:
        #non-strategy choice
        if count is not None:
            count += 1
        sigma[I] = make_default_strategy(state.legal_actions, state)
        a=np.random.choice(
            list(sigma[I].keys()), 1, p=list(sigma[I].values()),
        )[0]
    if total_count is not None:
        total_count += 1
    return a, count, total_count


def _create_dir(folder_id: str) -> Path:
    """Create and get a unique dir path to save to using a timestamp."""
    time = str(datetime.datetime.now())
    for char in ":- .":
        time = time.replace(char, "_")
    path: Path = Path(f"./{folder_id}_results_{time}")
    path.mkdir(parents=True, exist_ok=True)
    return path


def agent_test(
    hero_strategy_path: str,
    opponent_strategy_path: str,
    real_time_est: bool = False,
    action_sequence: List[str] = None,
    public_cards: List[Card] = [],
    n_outer_iters: int = 30,
    n_inner_iters: int = 100,
    n_players: int = 3,
    hero_count=None,
    hero_total_count=None,
):
    config: Dict[str, int] = {**locals()}
    save_path: Path = _create_dir('bt')
    with open(save_path / "config.yaml", "w") as steam:
        yaml.dump(config, steam)

    # Load unnormalized strategy for hero
    hero_strategy = joblib.load(hero_strategy_path)['strategy']
    # Load unnormalized strategy for opponents
    opponent_strategy = joblib.load(opponent_strategy_path)['strategy']

    # Loading game state we used RTS on
    if real_time_est:
        state: ShortDeckPokerState = new_game(
            n_players, real_time_test=real_time_est, public_cards=public_cards
        )
        current_game_state: ShortDeckPokerState = state.load_game_state(
            opponent_strategy, action_sequence
        ) 

    # TODO: Right now, this can only be used for loading states if the two
    # strategies are averaged. Even averaging strategies is risky. Loading a
    # game state should be used with caution. It will work only if the
    # probability of reach is identical across strategies. Use the average
    # strategy.
    oc= 0
    otc= 0
    card_info_lut = {}
    EVs = np.array([])
    for _ in trange(1, n_outer_iters):
        EV = np.array([])  # Expected value for player 0 (hero)
        for t in trange(1, n_inner_iters + 1, desc="train iter"):
            for p_i in range(n_players):
                if real_time_est:
                    # Deal hole cards based on bayesian updating of hole card
                    # probabilities
                    state: ShortDeckPokerState = current_game_state.deal_bayes()
                else:
                    state: ShortDeckPokerState = new_game(
                        n_players,
                        card_info_lut,
                        use_lut=False
                    )
                    card_info_lut = state.card_info_lut
                while True:
                    player_not_in_hand = not state.players[p_i].is_active
                    if state.is_terminal or player_not_in_hand:
                        EV = np.append(EV, state.payout[p_i])
                        break
                    if state.player_i == p_i:
                        action, hero_count, hero_total_count = \
                            _calculate_strategy(
                                state,
                                state.info_set,
                                hero_strategy,
                                count=hero_count,
                                total_count=hero_total_count
                        )
                    else:
                        action, oc, otc = _calculate_strategy(
                            state,
                            state.info_set,
                            opponent_strategy,
                            count=oc,
                            total_count=otc
                        )
                    state = state.apply_action(action)
        EVs = np.append(EVs, EV.mean())
    t_stat = (EVs.mean() - 0) / (EVs.std() / np.sqrt(n_outer_iters))
    p_val = stats.t.sf(np.abs(t_stat), n_outer_iters - 1)
    results_dict = {
        'Expected Value': float(EVs.mean()),
        'T Statistic': float(t_stat),
        'P Value': float(p_val),
        'Standard Deviation': float(EVs.std()),
        'N': int(len(EVs)),
        'Random Moves Hero': hero_count,
        'Total Moves Hero': hero_total_count,
        'Random Moves Opponent': oc,
        'Total Moves Opponent': otc
    }
    with open(save_path / 'results.yaml', "w") as stream:
        yaml.safe_dump(results_dict, stream=stream, default_flow_style=False)

if __name__ == "__main__":
    agent_test(
        hero_strategy_path="./_2022_09_20_14_24_20_947002/81000/agent.joblib",
        opponent_strategy_path="./_2022_09_20_14_24_20_947002/55000/agent.joblib",
        real_time_est=False,
        public_cards=[],
        action_sequence=None,
        n_inner_iters=50,
        n_outer_iters=100,
        hero_count=0,
        hero_total_count=0,
        n_players=4
    )
