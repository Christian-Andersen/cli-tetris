import torch
from curtsies import Input
from random import randint

WIDTH = 10
HEIGHT = 20
SHAPES = [(torch.tensor([[1, 1, 1, 1]], dtype=bool), 3),
          (torch.tensor([[1, 0, 0], [1, 1, 1]], dtype=bool), 3),
          (torch.tensor([[0, 0, 1], [1, 1, 1]], dtype=bool), 3),
          (torch.tensor([[1, 1], [1, 1]], dtype=bool), 4),
          (torch.tensor([[0, 1, 0], [1, 1, 1]], dtype=bool), 3),
          (torch.tensor([[1, 1, 0], [0, 1, 1]], dtype=bool), 3),
          (torch.tensor([[0, 1, 1], [1, 1, 0]], dtype=bool), 3)]


class GameState:
    def __init__(self):
        self.board = torch.zeros(HEIGHT, WIDTH, dtype=bool)
        self.tetro, self.x = SHAPES[randint(0, 6)]
        self.y = 0
        self.score = 0
        self.game_over = False

    def progress_game(self, input: str):
        if self.game_over:
            print('GAME OVER')
            return
        match input:
            case None:
                self.y += 1
                if self.has_overlap():
                    self.y -= 1
                    self.combine()
            case '<DOWN>':
                self.y += 1
                if self.has_overlap():
                    self.y -= 1
                    self.combine()
                if (self.y + self.tetro.shape[0]) == HEIGHT:
                    self.combine()
                self.y += 1
                if self.has_overlap():
                    self.y -= 1
                    self.combine()
            case '<UP>':
                self.tetro = self.tetro.rot90(k=1)
                if self.has_overlap():
                    self.tetro = self.tetro.rot90(k=3)
            case '<SPACE>':
                while ((self.y + self.tetro.shape[0] - 1) != HEIGHT) and (not self.has_overlap()):
                    self.y += 1
                self.y -= 1
                self.combine()
            case '<LEFT>':
                if self.x > 0:
                    self.x -= 1
                    if self.has_overlap():
                        self.x -= 1
                        self.combine()
            case '<RIGHT>':
                if (self.x + self.tetro.shape[1]) < WIDTH:
                    self.x += 1
                    if self.has_overlap():
                        self.x -= 1
                        self.combine()
        print(self.y + self.tetro.shape[0])
        if (self.y + self.tetro.shape[0]) == HEIGHT:
            self.combine()
        self.print_board()

    def combine(self):
        self.board = torch.logical_or(self.board, self.tetro_board())
        for row in reversed(range(HEIGHT)):
            if self.board[row].all():
                self.score += 1
                self.board[1:(row + 1),] = self.board.clone()[0:row,]
                self.board[1,] = torch.zeros(1, WIDTH, dtype=bool)
        self.new_shape()

    def has_overlap(self):
        return torch.logical_and(self.board, self.tetro_board()).any()

    def new_shape(self):
        """Creates new shape, also sets game_over flag to true if needed"""
        self.tetro, self.x = SHAPES[randint(0, 6)]
        self.y = 0
        self.game_over = torch.logical_and(self.board, self.tetro_board()).any()

    def tetro_board(self):
        """Returns a board with tetro on it"""
        shape_board = torch.zeros(HEIGHT, WIDTH, dtype=bool)
        shape_board[self.y:(self.y + self.tetro.shape[0]),
                    self.x:(self.x + self.tetro.shape[1])] = self.tetro
        return shape_board

    def print_board(self):
        """print board and shape onto console"""
        temp_y = self.y
        while ((self.y + self.tetro.shape[0] - 1) != HEIGHT) and (not self.has_overlap()):
            self.y += 1
        self.y -= 1
        shadow_print = self.tetro_board()
        self.y = temp_y
        to_print = torch.logical_or(self.board, self.tetro_board())
        print('\u2597' + 2 * WIDTH * '\u2584' + '\u2596')
        for row_idx in range(to_print.shape[0]):
            print('\u2590', end='')
            for col_idx in range(to_print.shape[1]):
                if to_print[row_idx, col_idx]:
                    print(2 * '\u2593', end='')
                else:
                    if shadow_print[row_idx, col_idx]:
                        print(2 * '\u25AF', end='')
                    else:
                        print(2 * ' ', end='')
            print('\u258C\n', end='')
        print('\u259D' + 2 * WIDTH * '\u2580' + '\u2598')
        print(f'SCORE: {self.score}')


def main():
    with Input() as input_generator:
        game = GameState()
        while True:
            if out := input_generator.send(0.2):
                game.progress_game(out)
            else:
                game.progress_game(None)


if __name__ == "__main__":
    main()
