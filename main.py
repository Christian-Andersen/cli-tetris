from __future__ import annotations

from random import randint
from typing import ClassVar

import numpy as np
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Center, Horizontal, Vertical
from textual.widgets import Digits, Footer, Header, Static

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
        self.next_tetro, _ = SHAPES[randint(0, 6)]  # noqa: S311
        self.held_tetro: np.ndarray | None = None
        self.can_hold = True
        self.new_shape()
        self.score = 0
        self.game_over = False

    def move_down(self) -> bool:
        """Moves tetro down. Returns True if it combined."""
        if self.game_over:
            return False
        self.y += 1
        if self.has_overlap():
            self.y -= 1
            self.combine()
            return True
        return False

    def handle_down(self) -> None:
        if self.game_over:
            return
        self.move_down()
        if (self.y + self.tetro.shape[0]) == HEIGHT:
            self.combine()
        self.move_down()
        self._check_bounds()

    def _check_bounds(self) -> None:
        if (self.y + self.tetro.shape[0]) >= HEIGHT:
            if (self.y + self.tetro.shape[0]) > HEIGHT:
                self.y = HEIGHT - self.tetro.shape[0]
            self.combine()

    def rotate(self) -> None:
        if self.game_over:
            return
        original_tetro = self.tetro.copy()
        original_x = self.x

        self.tetro = np.rot90(self.tetro, k=1)

        # Try original position, then shifts to make it fit
        for dx in [0, -1, 1, -2, 2]:
            self.x = original_x + dx
            if not self.has_overlap():
                return

        # If no position works, revert
        self.x = original_x
        self.tetro = original_tetro

    def drop(self) -> None:
        if self.game_over:
            return
        while ((self.y + self.tetro.shape[0] - 1) != HEIGHT) and (not self.has_overlap()):
            self.y += 1
        self.y -= 1
        self.combine()

    def move_left(self) -> None:
        if self.game_over:
            return
        if self.x > 0:
            self.x -= 1
            if self.has_overlap():
                self.x += 1

    def move_right(self) -> None:
        if self.game_over:
            return
        if (self.x + self.tetro.shape[1]) < WIDTH:
            self.x += 1
            if self.has_overlap():
                self.x -= 1

    def hold_piece(self) -> None:
        if self.game_over or not self.can_hold:
            return

        if self.held_tetro is None:
            self.held_tetro = self.tetro
            self.new_shape()
        else:
            self.held_tetro, self.tetro = self.tetro, self.held_tetro
            self.x = WIDTH // 2 - self.tetro.shape[1] // 2
            self.y = 0
            if self.has_overlap():
                self.game_over = True
        self.can_hold = False

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
        self.tetro = self.next_tetro
        self.x = WIDTH // 2 - self.tetro.shape[1] // 2
        self.y = 0
        self.next_tetro, _ = SHAPES[randint(0, 6)]  # noqa: S311
        self.can_hold = True
        if self.has_overlap():
            self.game_over = True

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

    def get_board_string(self) -> str:
        """Returns string representation of the board"""
        temp_y = self.y
        while ((self.y + self.tetro.shape[0]) < HEIGHT) and (not self.has_overlap()):
            self.y += 1
        if self.has_overlap():
            self.y -= 1
        shadow_print = self.tetro_board()
        self.y = temp_y
        to_print = np.logical_or(self.board, self.tetro_board())

        lines = []
        lines.append("\u2597" + 2 * WIDTH * "\u2584" + "\u2596")
        for row_idx in range(to_print.shape[0]):
            line = ["\u2590"]
            for col_idx in range(to_print.shape[1]):
                if to_print[row_idx, col_idx]:
                    line.append(2 * "\u2593")
                elif shadow_print[row_idx, col_idx]:
                    line.append(2 * "\u25af")
                else:
                    line.append(2 * " ")
            line.append("\u258c")
            lines.append("".join(line))
        lines.append("\u259d" + 2 * WIDTH * "\u2580" + "\u2598")
        if self.game_over:
            lines.append("   GAME OVER   ")
        return "\n".join(lines)


class TetrisApp(App):
    TITLE: ClassVar[str] = "Tetris"
    CSS: ClassVar[str] = """
    Screen {
        align: center middle;
    }
    #game-container {
        layout: horizontal;
        width: 60;
        height: 25;
        border: heavy $primary;
        align: center middle;
    }
    #main-panel {
        width: 40;
        height: 100%;
        align: center middle;
    }
    #side-panel {
        width: 20;
        height: 100%;
        border-left: solid $primary-muted;
        padding: 1 2;
    }
    .side-label {
        text-style: bold;
        margin-top: 1;
    }
    .piece-preview {
        height: 5;
        content-align: center middle;
        border: panel $primary-muted;
        margin-bottom: 1;
    }
    #board {
        width: auto;
        height: auto;
    }
    #score {
        margin-top: 1;
    }
    """

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("left", "move_left", "Left"),
        Binding("right", "move_right", "Right"),
        Binding("up", "rotate", "Rotate"),
        Binding("down", "move_down", "Down"),
        Binding("space", "drop", "Drop"),
        Binding("c", "hold", "Hold"),
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="game-container"):
            with Vertical(id="main-panel"), Center():
                yield Static(id="board")
            with Vertical(id="side-panel"):
                yield Static("HOLD", classes="side-label")
                yield Static(id="hold-piece", classes="piece-preview")
                yield Static("NEXT", classes="side-label")
                yield Static(id="next-piece", classes="piece-preview")
                yield Static("SCORE", classes="side-label")
                yield Digits("0", id="score")
        yield Footer()

    def on_mount(self) -> None:
        self.game = GameState()
        self.update_board()
        self.set_interval(0.5, self.tick)

    def tick(self) -> None:
        if not self.game.game_over:
            self.game.move_down()
            self.update_board()

    def _get_piece_string(self, tetro: np.ndarray | None) -> str:
        if tetro is None:
            return ""
        lines = []
        for row in tetro:
            line = [2 * "\u2593" if cell else "  " for cell in row]
            lines.append("".join(line))
        return "\n".join(lines)

    def update_board(self) -> None:
        self.query_one("#board", Static).update(self.game.get_board_string())
        self.query_one("#score", Digits).update(str(self.game.score))
        self.query_one("#next-piece", Static).update(self._get_piece_string(self.game.next_tetro))
        self.query_one("#hold-piece", Static).update(self._get_piece_string(self.game.held_tetro))

    def action_move_left(self) -> None:
        self.game.move_left()
        self.update_board()

    def action_move_right(self) -> None:
        self.game.move_right()
        self.update_board()

    def action_rotate(self) -> None:
        self.game.rotate()
        self.update_board()

    def action_move_down(self) -> None:
        self.game.handle_down()
        self.update_board()

    def action_drop(self) -> None:
        self.game.drop()
        self.update_board()

    def action_hold(self) -> None:
        self.game.hold_piece()
        self.update_board()


if __name__ == "__main__":
    app = TetrisApp()
    app.run()
