import random
import copy
from collections import deque


class LightsOutPuzzle(object):

    def __init__(self, board):
        self._board = board

    def get_board(self):
        return self._board

    def perform_move(self, row, col):
        board = self.get_board()
        numrows = len(board)
        numcols = len(board[row])
        board[row][col] = not board[row][col]
        # down
        if row != (numrows - 1):
            board[row + 1][col] = not board[row + 1][col]
        # up
        if row != 0:
            board[row - 1][col] = not board[row - 1][col]
        # left
        if col != 0:
            board[row][col - 1] = not board[row][col - 1]
        # right
        if col != (numcols - 1):
            board[row][col + 1] = not board[row][col + 1]
        

    def scramble(self):
        board = self.get_board()
        numrows = len(board)
        numcols = len(board[0])
        for i in range(numrows):
            for j in range(numcols):
                if(random.random() < 0.5):
                    self.perform_move(i, j)

    def is_solved(self):
        board = self.get_board()
        numrows = len(board)
        numcols = len(board[0])
        for i in range(numrows):
            for j in range(numcols):
                if(board[i][j]):
                    return False
        return True
                

    def copy(self):
        new = copy.deepcopy(self.get_board())
        return LightsOutPuzzle(new)

    def successors(self):
        board = self.get_board()
        numrows = len(board)
        numcols = len(board[0])
        for i in range(numrows):
            for j in range(numcols):
                new = self.copy()
                new.perform_move(i, j)
                yield ((i, j), new)

    def find_solution(self):
        start = tuple(tuple(row) for row in self.get_board())
        frontier = deque()
        visited = set()
        frontier.append((self.copy(), []))
        visited.add(start)
        while len(frontier) != 0:
            temp = frontier.popleft()
            state, path = temp
            for move, c in state.successors():
                child = tuple(tuple(row) for row in c.get_board())
                if child not in visited:
                    newpath = path.copy()
                    newpath.append(move)
                    if c.is_solved():
                        return newpath
                    visited.add(child)
                    frontier.append((c, newpath))
        return None

def make_puzzle(rows, cols):
    make = []
    for i in range(rows):
        l = []
        for j in range(cols):
            l.append(False)
        make.append(l)
    return LightsOutPuzzle(make)

'''
p = make_puzzle(3, 3)
p.perform_move(1, 1)
print(p.get_board())
p.perform_move(0, 0)
print(p.get_board())
p.perform_move(2, 2)
print(p.get_board())
p.scramble()
print(p.get_board())
print(p.is_solved())
m = make_puzzle(3, 3)
print(m.is_solved())
m.scramble()
print(m.get_board())
h = make_puzzle(3, 3)
h2 = h.copy()
print(h.get_board() == h2.get_board())
h.perform_move(1, 1)
print(h.get_board() == h2.get_board())
s = make_puzzle(3,2)
for move, new_s in s.successors():
    print(move, new_s.get_board())
v = make_puzzle(2, 3)
for row in range(2):
    for col in range(3):
        v.perform_move(row, col)
print(v.find_solution())
b = LightsOutPuzzle([[True, False, False], [False, False, False]])
print(b.find_solution())
'''