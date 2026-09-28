from enum import Enum, auto
from random import Random
from types import MappingProxyType
from .card import Card, PlayedCard, Trick
from .deck import Deck

class GamePhase(Enum):
    FIRST_PLAY = auto()
    SECOND_PLAY = auto()
    GAME_OVER = auto()

class InvalidActionError(RuntimeError):
    """Action is not allowed in the current phase"""

class Game:
    # 2 4 5 6 7 Fante Cavallo Re 3 Asso
    _ranks = "2 4 5 6 7 F C R 3 A".split()
    _strength = {rank: strength for strength, rank in enumerate(_ranks)}
    _points = MappingProxyType({
        "2": 0, "4": 0, "5": 0, "6": 0, "7": 0,
        "F": 2, "C": 3, "R": 4, "3": 10, "A": 11,
    })
    # Spade Coppe Denari Bastoni
    _suits = "S C D B".split()

    def __init__(
        self,
        *,
        rng: Random | None = None,
        first_player: int = 0,
    ) -> None:
        self._require_player(first_player)
        
        self._deck = self._create_deck(rng)
        self._current_player = first_player

        self._hands: tuple[list[Card], list[Card]] = ([], [])
        self._current_trick: list[PlayedCard] = []
        self._tricks: tuple[list[Trick], list[Trick]] = ([], [])

        self._trump_card: Card | None = None

        self._setup()

    @property
    def phase(self) -> GamePhase:
        return self._phase

    @property
    def current_player(self) -> int:
        return self._current_player

    @property
    def trump_card(self) -> Card | None:
        return self._trump_card

    @property
    def points(self) -> tuple[int, int]:
        first, second = (
            sum(trick.points for trick in tricks)
            for tricks in self._tricks
        )
        return first, second

    @property
    def remaining_cards(self) -> int:
        return len(self._deck)

    @property
    def is_finished(self) -> bool:
        return self._phase is GamePhase.GAME_OVER

    def hand(self, player: int) -> tuple[Card, ...]:
        self._require_player(player)
        return tuple(self._hands[player])

    def _setup(self) -> None:
        order = (self._current_player, 1 - self._current_player)

        for _ in range(3):
            for player in order:
                self._hands[player].append(self._deck.draw())

        self._trump_card = self._deck.move(0, -1)

        self._phase = GamePhase.FIRST_PLAY

    def play_card(self, player: int, hand_index: int) -> None:
        self._require_phase(GamePhase.FIRST_PLAY, GamePhase.SECOND_PLAY)
        self._require_player(player)

        if (player != self._current_player):
            raise InvalidActionError()

        card = self._hands[player].pop(hand_index)
        self._current_trick.append(PlayedCard(player=player, card=card))

        if self._phase is GamePhase.FIRST_PLAY:
            self._current_player = 1 - player
            self._phase = GamePhase.SECOND_PLAY
        else:
            self._resolve_trick()

    def _resolve_trick(self) -> None:
        first, second = self._current_trick

        if first.card.suit == second.card.suit:
            second_wins = self._strength[first.card.rank] < self._strength[second.card.rank]
        else:
            second_wins = second.card.is_trump(self._trump_card)

        winner = second.player if second_wins else first.player

        trick = self._create_trick(cards=(first, second))
        self._tricks[winner].append(trick)
        self._current_trick.clear()
        self._current_player = winner

        for player in (winner, 1 - winner):
            if self._deck:
                self._hands[player].append(self._deck.draw())

        if (any(self._hands)):
            self._phase = GamePhase.FIRST_PLAY
        else:
            self._phase = GamePhase.GAME_OVER

    @classmethod
    def _create_deck(cls, rng: Random | None = None) -> Deck:
        cards = [Card(rank, suit) for suit in cls._suits for rank in cls._ranks]
        random = rng if rng is not None else Random()
        random.shuffle(cards)
        return Deck(cards)

    @classmethod
    def _create_trick(cls, cards: tuple[PlayedCard, PlayedCard]):
        return Trick(
            cards,
            lambda card: cls._points[card.rank]
        )

    @staticmethod
    def _require_player(player: int) -> None:
        if (player not in (0, 1)):
            raise ValueError("The player must have an index of 0 or 1")

    def _require_phase(self, *allowed: GamePhase) -> None:
        if self._phase not in allowed:
            raise InvalidActionError()
