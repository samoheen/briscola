from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class Card:
    rank: str
    suit: str

    def __repr__(self) -> str:
        return f"Card(rank={self.rank!r},suit={self.suit!r})"

    def __str__(self) -> str:
        return f"{self.rank!s}{self.suit!s}"

    def is_trump(self, trump_card: Card | None) -> bool:
        return trump_card is not None and self.suit == trump_card.suit


@dataclass(frozen=True, slots=True)
class PlayedCard:
    player: int
    card: Card


class Trick:
    def __init__(
            self,
            cards: tuple[PlayedCard, PlayedCard],
            points_for: Callable[[Card], int],
    ) -> None:
        self._cards = cards
        self._points = sum(points_for(played.card) for played in cards)

    @property
    def cards(self) -> tuple[PlayedCard, PlayedCard]:
        return self._cards

    @property
    def points(self) -> int:
        return self._points
