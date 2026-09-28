from collections.abc import Iterable
from .card import Card

class EmptyDeckError(LookupError):
    """There is no cards in a deck"""

class Deck:
    def __init__(
        self,
        cards: Iterable[Card],
    ) -> None:
        self._cards = list(cards)

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, index: int):
        return self._cards[index]

    def draw(self) -> Card:
        if not self._cards:
            raise EmptyDeckError()

        return self._cards.pop(0)

    def move(self, src: int, dst: int) -> Card:
        if not self._cards:
            raise EmptyDeckError()

        positions = range(len(self._cards))
        src = positions[src]
        dst = positions[dst]

        card = self._cards.pop(src)
        self._cards.insert(dst, card)
        return card
