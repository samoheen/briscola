from .game import Game

def _autoplay(game: Game) -> tuple[int, int]:
    while not game.is_finished:
        game.play_card(game.current_player, hand_index=0)

    return game.points

def main() -> None:
    game = Game()
    print(_autoplay(game))
