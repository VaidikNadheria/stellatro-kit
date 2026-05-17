"""
Stellatro submission bot.

Draft: denial-aware greedy + 2-ply lookahead on top-4 (draft uses cached top combos).
Play: exact exhaustive 5-card search via evaluate_hand.
"""

from copy import deepcopy
from itertools import combinations
from typing import Dict, List, Tuple

from stellatro_common import GameState, PlayerTurn
from stellatro_game import Card, Suit, evaluate_hand, PLAYER_CARDS
from stellatro_game.jokers import ALL_JOKER_CLASSES, RegularJoker

DENIAL_WEIGHT = 0.35
LOOKAHEAD_TOP_K = 4
DRAFT_TOP_COMBOS = 15

_JOKER_NAME_TO_CLASS = {cls.name: cls for cls in ALL_JOKER_CLASSES}

HandKey = tuple
JokerKey = tuple
ComboKey = Tuple[HandKey, JokerKey]
ScoreCache = Dict[ComboKey, int]
ComboCache = Dict[ComboKey, tuple[tuple[int, ...], ...]]


def _to_cards(card_models) -> List[Card]:
    cards = []
    for c in card_models:
        card = Card(c.rank, Suit(c.suits[0]))
        for s in c.suits[1:]:
            card.add_suit(Suit(s))
        card.scored = c.scored
        card.num_triggers = c.num_triggers
        cards.append(card)
    return cards


def _to_jokers(joker_models):
    return [_JOKER_NAME_TO_CLASS.get(j.name, RegularJoker)() for j in joker_models]


def _hand_key(cards: List[Card]) -> HandKey:
    n = min(PLAYER_CARDS, len(cards))
    return tuple(
        (cards[i].rank, tuple(sorted(str(s) for s in cards[i].suits)))
        for i in range(n)
    )


def _joker_key(jokers) -> JokerKey:
    return tuple(type(j).__name__ for j in jokers)


def _score_combo(cards: List[Card], jokers, combo: tuple[int, ...]) -> int:
    try:
        return evaluate_hand(
            [deepcopy(cards[i]) for i in combo],
            deepcopy(jokers),
        )
    except Exception:
        return -1


def _search_combos(
    hand: List[Card],
    jokers,
    seed_combos: tuple[tuple[int, ...], ...] | None,
    *,
    full: bool = False,
) -> tuple[int, tuple[tuple[int, ...], ...]]:
    """Return best score and top combo seeds (full 252 or incremental re-score)."""
    n = min(PLAYER_CARDS, len(hand))
    if n < 5:
        return 0, ()

    scored: List[tuple[int, tuple[int, ...]]] = []

    if seed_combos and not full:
        for combo in seed_combos:
            if len(combo) != 5 or any(i >= n for i in combo):
                continue
            scored.append((_score_combo(hand, jokers, combo), combo))
    else:
        for combo in combinations(range(n), 5):
            scored.append((_score_combo(hand, jokers, combo), combo))

    if not scored:
        return 0, ()

    scored.sort(key=lambda item: item[0], reverse=True)
    best_score = scored[0][0]
    top_combos = tuple(combo for _, combo in scored[:DRAFT_TOP_COMBOS])
    return best_score, top_combos


def _draft_best_score(
    hand: List[Card],
    jokers,
    hand_key: HandKey,
    score_cache: ScoreCache,
    combo_cache: ComboCache,
) -> int:
    """Fast draft evaluation with memoization and incremental combo reuse."""
    jkey = _joker_key(jokers)
    key: ComboKey = (hand_key, jkey)
    cached_score = score_cache.get(key)
    if cached_score is not None:
        return cached_score

    parent_key: ComboKey = (hand_key, jkey[:-1]) if jkey else (hand_key, ())
    parent_combos = combo_cache.get(parent_key)
    score, top_combos = _search_combos(
        hand,
        jokers,
        parent_combos,
        full=parent_combos is None,
    )
    score_cache[key] = score
    combo_cache[key] = top_combos
    return score


def _best_hand(cards: List[Card], jokers) -> tuple[int, List[int]]:
    """Exact play-phase search over all legal 5-card subsets."""
    best_score = -1
    best_indices: List[int] = list(range(min(5, len(cards))))
    n = min(PLAYER_CARDS, len(cards))
    if n < 5:
        return 0, best_indices

    for combo in combinations(range(n), 5):
        score = _score_combo(cards, jokers, combo)
        if score > best_score:
            best_score = score
            best_indices = list(combo)
    return best_score, best_indices


def _immediate_value(
    my_hand: List[Card],
    my_jokers,
    opp_hand: List[Card],
    opp_jokers,
    candidate,
    my_baseline: int,
    opp_baseline: int,
    my_hand_key: HandKey,
    opp_hand_key: HandKey,
    score_cache: ScoreCache,
    combo_cache: ComboCache,
) -> float:
    my_gain = (
        _draft_best_score(my_hand, my_jokers + [candidate], my_hand_key, score_cache, combo_cache)
        - my_baseline
    )
    opp_gain = (
        _draft_best_score(opp_hand, opp_jokers + [candidate], opp_hand_key, score_cache, combo_cache)
        - opp_baseline
    )
    return my_gain - DENIAL_WEIGHT * opp_gain


def _opponent_denial_pick(
    remaining: List[tuple[int, object]],
    my_hand: List[Card],
    my_jokers_after,
    opp_hand: List[Card],
    opp_jokers,
    my_baseline_after: int,
    opp_baseline: int,
    my_hand_key: HandKey,
    opp_hand_key: HandKey,
    score_cache: ScoreCache,
    combo_cache: ComboCache,
) -> object | None:
    best_value = -float("inf")
    best_candidate = None
    for _, candidate in remaining:
        opp_gain = (
            _draft_best_score(opp_hand, opp_jokers + [candidate], opp_hand_key, score_cache, combo_cache)
            - opp_baseline
        )
        my_gain_if_denied = (
            _draft_best_score(
                my_hand, my_jokers_after + [candidate], my_hand_key, score_cache, combo_cache
            )
            - my_baseline_after
        )
        value = opp_gain - DENIAL_WEIGHT * my_gain_if_denied
        if value > best_value:
            best_value = value
            best_candidate = candidate
    return best_candidate


class Bot:
    def pick_joker(self, state: GameState) -> int:
        is_p1 = state.current_turn == PlayerTurn.PLAYER1
        my_hand = _to_cards(state.player1_hand if is_p1 else state.player2_hand)
        my_jokers = _to_jokers(state.player1_jokers if is_p1 else state.player2_jokers)
        opp_hand = _to_cards(state.player2_hand if is_p1 else state.player1_hand)
        opp_jokers = _to_jokers(state.player2_jokers if is_p1 else state.player1_jokers)

        score_cache: ScoreCache = {}
        combo_cache: ComboCache = {}
        my_hand_key = _hand_key(my_hand)
        opp_hand_key = _hand_key(opp_hand)

        my_baseline = _draft_best_score(my_hand, my_jokers, my_hand_key, score_cache, combo_cache)
        opp_baseline = _draft_best_score(opp_hand, opp_jokers, opp_hand_key, score_cache, combo_cache)

        pool = state.joker_pool
        ranked: List[tuple[float, int, object]] = []
        for i, joker_model in enumerate(pool):
            candidate = _JOKER_NAME_TO_CLASS.get(joker_model.name, RegularJoker)()
            immediate = _immediate_value(
                my_hand,
                my_jokers,
                opp_hand,
                opp_jokers,
                candidate,
                my_baseline,
                opp_baseline,
                my_hand_key,
                opp_hand_key,
                score_cache,
                combo_cache,
            )
            ranked.append((immediate, i, candidate))

        ranked.sort(key=lambda item: item[0], reverse=True)
        top_candidates = ranked[: min(LOOKAHEAD_TOP_K, len(ranked))]

        best_idx = top_candidates[0][1]
        best_diff = -float("inf")
        best_immediate = -float("inf")
        for immediate, i, candidate in top_candidates:
            my_jokers_after = my_jokers + [candidate]
            my_baseline_after = _draft_best_score(
                my_hand, my_jokers_after, my_hand_key, score_cache, combo_cache
            )

            remaining = [
                (j, _JOKER_NAME_TO_CLASS.get(pool[j].name, RegularJoker)())
                for j in range(len(pool))
                if j != i
            ]

            opp_jokers_after = list(opp_jokers)
            if remaining:
                opp_pick = _opponent_denial_pick(
                    remaining,
                    my_hand,
                    my_jokers_after,
                    opp_hand,
                    opp_jokers,
                    my_baseline_after,
                    opp_baseline,
                    my_hand_key,
                    opp_hand_key,
                    score_cache,
                    combo_cache,
                )
                if opp_pick is not None:
                    opp_jokers_after.append(opp_pick)

            differential = my_baseline_after - _draft_best_score(
                opp_hand, opp_jokers_after, opp_hand_key, score_cache, combo_cache
            )

            if differential > best_diff or (
                differential == best_diff and immediate > best_immediate
            ):
                best_diff = differential
                best_immediate = immediate
                best_idx = i

        return best_idx

    def pick_hand(self, state: GameState) -> List[int]:
        is_p1 = state.current_turn == PlayerTurn.PLAYER1
        my_hand = _to_cards(state.player1_hand if is_p1 else state.player2_hand)
        my_jokers = _to_jokers(state.player1_jokers if is_p1 else state.player2_jokers)
        _, indices = _best_hand(my_hand, my_jokers)
        return indices
