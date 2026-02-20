from random import randint
from typing import TYPE_CHECKING

import numpy as np
from curtsies import Input

if TYPE_CHECKING:
    from curtsies.events import Event

WIDTH = 10
HEIGHT = 20
SHAPES = [
    (np.array([[1, 1, 1, 1]], dtype=bool), 3),
    (np.array([[1, 0, 0], [1, 1, 1]], dtype=bool), 3),
    (np.array([[0, 0, 1], [1, 1, 1]], dtype=bool), 3),
    (np.array([[1, 1], [1, 1]], dtype=bool), 4),
    (np.array([[0, 1, 0], [1, 1, 1]], dtype=bool), 3),
    (np.array([[1, 1, 0], [0, 1, 1]], dtype=bool), 3),
    (np.array([[0, 1, 1], [1, 1, 0]], dtype=bool), 3),
]


class GameState:
    def __init__(self) -> None:
        self.board = np.zeros((HEIGHT, WIDTH), dtype=bool)
        self.tetro, self.x = SHAPES[randint(0, 6)]  # noqa: S311
        self.y = 0
        self.score = 0
        self.game_over = False

    def progress_game(self, user_input: str | Event | None) -> None:
        if self.game_over:
            print("GAME OVER")
            return
        match user_input:
            case None:
                self._move_down()
            case "<DOWN>":
                self._handle_down()
            case "<UP>":
                self._rotate()
            case "<SPACE>":
                self._drop()
            case "<LEFT>":
                self._move_left()
            case "<RIGHT>":
                self._move_right()

        self._check_bounds()
        self.print_board()

    def _handle_down(self) -> None:
        self._move_down()
        if (self.y + self.tetro.shape[0]) == HEIGHT:
            self.combine()
        self._move_down()

    def _check_bounds(self) -> None:
        if (self.y + self.tetro.shape[0]) >= HEIGHT:
            if (self.y + self.tetro.shape[0]) > HEIGHT:
                self.y = HEIGHT - self.tetro.shape[0]
            self.combine()

    def _move_down(self) -> None:
        self.y += 1
        if self.has_overlap():
            self.y -= 1
            self.combine()

    def _rotate(self) -> None:
        self.tetro = np.rot90(self.tetro, k=1)
        if self.has_overlap():
            self.tetro = np.rot90(self.tetro, k=3)

    def _drop(self) -> None:
        while ((self.y + self.tetro.shape[0] - 1) != HEIGHT) and (not self.has_overlap()):
            self.y += 1
        self.y -= 1
        self.combine()

    def _move_left(self) -> None:
        if self.x > 0:
            self.x -= 1
            if self.has_overlap():
                self.x += 1

    def _move_right(self) -> None:
        if (self.x + self.tetro.shape[1]) < WIDTH:
            self.x += 1
            if self.has_overlap():
                self.x -= 1

    def combine(self) -> None:
        self.board = np.logical_or(self.board, self.tetro_board())
        for row in reversed(range(HEIGHT)):
            if self.board[row].all():
                self.score += 1
                self.board[1 : (row + 1), :] = self.board[0:row, :].copy()
                self.board[0, :] = False
        self.new_shape()

    def has_overlap(self) -> bool:
        if self.y + self.tetro.shape[0] > HEIGHT or self.y < 0:
            return True
        if self.x + self.tetro.shape[1] > WIDTH or self.x < 0:
            return True
        return np.logical_and(self.board, self.tetro_board()).any()

    def new_shape(self) -> None:
        """Creates new shape, also sets game_over flag to true if needed"""
        self.tetro, self.x = SHAPES[randint(0, 6)]  # noqa: S311
        self.y = 0
        self.game_over = self.has_overlap()

    def tetro_board(self) -> np.ndarray:
        """Returns a board with tetro on it, handling out of bounds safely"""
        shape_board = np.zeros((HEIGHT, WIDTH), dtype=bool)

        y_start = max(0, self.y)
        y_end = min(HEIGHT, self.y + self.tetro.shape[0])
        x_start = max(0, self.x)
        x_end = min(WIDTH, self.x + self.tetro.shape[1])

        tetro_y_start = max(0, -self.y)
        tetro_y_end = tetro_y_start + (y_end - y_start)
        tetro_x_start = max(0, -self.x)
        tetro_x_end = tetro_x_start + (x_end - x_start)

        if y_start < y_end and x_start < x_end:
            shape_board[y_start:y_end, x_start:x_end] = self.tetro[tetro_y_start:tetro_y_end, tetro_x_start:tetro_x_end]
        return shape_board

    def print_board(self) -> None:
        """print board and shape onto console"""
        temp_y = self.y
        while ((self.y + self.tetro.shape[0]) < HEIGHT) and (not self.has_overlap()):
            self.y += 1
        if self.has_overlap():
            self.y -= 1
        shadow_print = self.tetro_board()
        self.y = temp_y
        to_print = np.logical_or(self.board, self.tetro_board())
        print("\u2597" + 2 * WIDTH * "\u2584" + "\u2596")
        for row_idx in range(to_print.shape[0]):
            print("\u2590", end="")
            for col_idx in range(to_print.shape[1]):
                if to_print[row_idx, col_idx]:
                    print(2 * "\u2593", end="")
                elif shadow_print[row_idx, col_idx]:
                    print(2 * "\u25af", end="")
                else:
                    print(2 * " ", end="")
            print("\u258c\n", end="")
        print("\u259d" + 2 * WIDTH * "\u2580" + "\u2598")
        print(f"SCORE: {self.score}")


def main() -> None:
    with Input() as input_generator:
        game = GameState()
        while True:
            if out := input_generator.send(0.2):
                game.progress_game(out)
            else:
                game.progress_game(None)


if __name__ == "__main__":
    main()
