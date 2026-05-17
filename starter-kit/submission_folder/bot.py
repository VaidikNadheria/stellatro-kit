from stellatro_common import GameState, PlayerTurn
from typing import List


class Bot:
    def pick_joker(self, state: GameState) -> int:
        # jokers available to pick from (shared pool)
        joker_pool = state.joker_pool

        # drafted jokers belonging to the active player
        if state.current_turn == PlayerTurn.PLAYER1:
            player_jokers = state.player1_jokers
        else:
            player_jokers = state.player2_jokers

        return 0

    def pick_hand(self, state: GameState) -> List[int]:
        if state.current_turn == PlayerTurn.PLAYER1:
            hand = state.player1_hand
        else:
            hand = state.player2_hand

        # play the first 5 playable cards
        return [0, 1, 2, 3, 4]