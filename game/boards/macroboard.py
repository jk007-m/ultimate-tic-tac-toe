from .microboard import Microboard
from .boarditems import State, Square, IllegalMoveError


class Macroboard:
    def __init__(self, size=3, first=Square.X):
        self.SIZE = size
        self.boards = [[Microboard(size) for _ in range(size)]
                       for _ in range(size)]
        self.__on_turn = first
        self.__last_move = None

    @property
    def dead_boards(self):
        return [(i, j) for i in range(self.SIZE) for j in range(self.SIZE)
                if self.boards[i][j].state != State.IN_PROGRESS]

    @property
    def active_boards(self):
        return [(i, j) for i in range(self.SIZE) for j in range(self.SIZE)
                if self.boards[i][j].state == State.IN_PROGRESS]

    def to_coords(self, px, py):
        if px not in range(self.SIZE**2) or py not in range(self.SIZE**2):
            raise IndexError
        return (px // self.SIZE, py // self.SIZE,
                px % self.SIZE, py % self.SIZE)

    def to_position(self, x, y, i, j):
        return (x * self.SIZE + i, y * self.SIZE + j)

    def coords_to_positions(self, coords):
        return [self.to_position(x, y, i, j) for (x, y, i, j) in coords]

    def positions_to_coords(self, positions):
        return [self.to_coords(px, py) for (px, py) in positions]

    def board_empty_positions(self, x, y):
        board = self.boards[x][y]
        coords = [(x, y, i, j) for (i, j) in board.empty_squares]
        return self.coords_to_positions(coords)

    @property
    def available_boards(self):
        if self.__last_move is None:
            return self.active_boards
        x, y = self.__last_move[-2:]
        if self.boards[x][y].state == State.IN_PROGRESS:
            return [(x, y)]
        return self.active_boards

    @property
    def available_moves(self):
        moves = []
        for x, y in self.available_boards:
            moves.extend([self.to_position(x, y, i, j) for (i, j)
                         in self.boards[x][y].empty_squares])
        return moves

    @property
    def state(self):
        lines = [[board.state for board in row] for row in self.boards]
        columns = zip(*lines)
        diagonals = [[lines[i][i] for i in range(self.SIZE)],
                     [lines[i][self.SIZE - i - 1] for i in range(self.SIZE)]]
        lines.extend(columns)
        lines.extend(diagonals)
        for line in lines:
            if set(line) == {State.X_WON}:
                return State.X_WON
            if set(line) == {State.O_WON}:
                return State.O_WON
        if not any(map(lambda line: State.IN_PROGRESS in line, lines)):
            return State.DRAW
        return State.IN_PROGRESS

    def make_move(self, px, py):
        x, y, i, j = self.to_coords(px, py)
        board = self.boards[x][y]
        if (x, y) not in self.available_boards:
            raise IllegalMoveError('Illegal move. Board is unavailable.')
        board.set_square(i, j, self.__on_turn)
        self.__on_turn = Square.X if self.__on_turn == Square.O else Square.O
        self.__last_move = (x, y, i, j)

    def __str__(self):
        str = '-' * (self.SIZE ** 2 + self.SIZE + 1) + '\n'
        for row in self.boards:
            for i in range(self.SIZE):
                str += '|'
                for board in row:
                    for square in board.export_grid()[i]:
                        str += square.value
                    str += '|'
                str += '\n'
            str += '-' * (self.SIZE ** 2 + self.SIZE + 1) + '\n'
        return str

    def macro_str(self):
        str = '-' * (2 * self.SIZE + 1) + '\n'
        for row in self.boards:
            str += ' '
            for board in row:
                str += board.state.value + ' '
            str += '\n' + '-' * (2 * self.SIZE + 1) + '\n'
        return str
