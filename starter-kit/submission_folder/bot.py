from itertools import combinations
from typing import List, Sequence

from stellatro_common import CardModel, GameState, JokerModel, PlayerTurn
from stellatro_game import Card, Game, Joker, PLAYER_CARDS, Suit
from stellatro_game.jokers import ALL_JOKER_CLASSES, RegularJoker


_JOKER_NAME_TO_CLASS = {joker_cls.name: joker_cls for joker_cls in ALL_JOKER_CLASSES}
_LEGAL_5_CARD_COMBOS = tuple(combinations(range(PLAYER_CARDS), 5))
_SCORER = Game(verbose=False)
DEFAULT_DENIAL_WEIGHT = 0.25


def _card_from_model(card_model: CardModel) -> Card:
    suits = [Suit(suit) for suit in card_model.suits]
    if not suits:
        raise ValueError("CardModel must include at least one suit.")

    card = Card(card_model.rank, suits[0])
    for suit in suits[1:]:
        card.add_suit(suit)
    card.scored = card_model.scored
    card.num_triggers = card_model.num_triggers
    card.stella = getattr(card_model, "stella", 0)
    return card


def _copy_card(card: Card) -> Card:
    suits = list(card.suits)
    copied = Card(card.rank, suits[0])
    for suit in suits[1:]:
        copied.add_suit(suit)
    copied.scored = card.scored
    copied.num_triggers = card.num_triggers
    copied.stella = card.stella
    return copied


def _joker_from_model(joker_model: JokerModel) -> Joker:
    joker_cls = _JOKER_NAME_TO_CLASS.get(joker_model.name, RegularJoker)
    return joker_cls()


def _active_player(state: GameState) -> PlayerTurn:
    return state.current_turn or PlayerTurn.PLAYER1


def _opponent(player_turn: PlayerTurn) -> PlayerTurn:
    if player_turn == PlayerTurn.PLAYER1:
        return PlayerTurn.PLAYER2
    return PlayerTurn.PLAYER1


def _hand_for_player(state: GameState, player_turn: PlayerTurn) -> List[Card]:
    if player_turn == PlayerTurn.PLAYER1:
        return [_card_from_model(card) for card in state.player1_hand]
    return [_card_from_model(card) for card in state.player2_hand]


def _jokers_for_player(state: GameState, player_turn: PlayerTurn) -> List[Joker]:
    if player_turn == PlayerTurn.PLAYER1:
        return [_joker_from_model(joker) for joker in state.player1_jokers]
    return [_joker_from_model(joker) for joker in state.player2_jokers]


def _hand_for_active_player(state: GameState) -> List[Card]:
    return _hand_for_player(state, _active_player(state))


def _jokers_for_active_player(state: GameState) -> List[Joker]:
    return _jokers_for_player(state, _active_player(state))


def _legal_5_card_indices(hand: Sequence[Card]):
    playable_cards = min(PLAYER_CARDS, len(hand))
    if playable_cards < 5:
        return
    if playable_cards == PLAYER_CARDS:
        yield from _LEGAL_5_CARD_COMBOS
        return
    yield from combinations(range(playable_cards), 5)


def _score_indices(
    hand: Sequence[Card],
    jokers: Sequence[Joker],
    indices: Sequence[int],
) -> int:
    chosen_cards = [_copy_card(hand[index]) for index in indices]
    return int(_SCORER.evaluate_hand(chosen_cards, list(jokers)))


def _best_hand(hand: Sequence[Card], jokers: Sequence[Joker]) -> tuple[int, List[int]]:
    best_score = -1
    best_indices: List[int] = []

    for indices in _legal_5_card_indices(hand):
        try:
            score = _score_indices(hand, jokers, indices)
        except Exception:
            continue
        if score > best_score:
            best_score = score
            best_indices = list(indices)

    if not best_indices:
        playable_cards = min(PLAYER_CARDS, len(hand))
        best_indices = list(range(min(5, playable_cards)))
        best_score = 0

    return best_score, best_indices


class Bot:
    def __init__(self, denial_weight: float = DEFAULT_DENIAL_WEIGHT) -> None:
        self.denial_weight = denial_weight

    def pick_joker(self, state: GameState) -> int:
        if not state.joker_pool:
            return 0

        player_turn = _active_player(state)
        opponent_turn = _opponent(player_turn)

        hand = _hand_for_player(state, player_turn)
        current_jokers = _jokers_for_player(state, player_turn)
        opponent_hand = _hand_for_player(state, opponent_turn)
        opponent_jokers = _jokers_for_player(state, opponent_turn)

        current_best_score, _ = _best_hand(hand, current_jokers)
        opponent_current_score, _ = _best_hand(opponent_hand, opponent_jokers)

        best_value = float("-inf")
        best_index = 0

        for index, joker_model in enumerate(state.joker_pool):
            candidate_joker = _joker_from_model(joker_model)
            my_score, _ = _best_hand(hand, current_jokers + [candidate_joker])
            opponent_score, _ = _best_hand(opponent_hand, opponent_jokers + [candidate_joker])

            my_gain = my_score - current_best_score
            opponent_gain = opponent_score - opponent_current_score
            value = my_gain + current_best_score - (self.denial_weight * opponent_gain)

            if value > best_value:
                best_value = value
                best_index = index

        return best_index

    def pick_hand(self, state: GameState) -> List[int]:
        hand = _hand_for_active_player(state)
        jokers = _jokers_for_active_player(state)
        _, indices = _best_hand(hand, jokers)
        return indices
