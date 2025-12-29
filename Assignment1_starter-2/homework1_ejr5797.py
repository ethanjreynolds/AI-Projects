############################################################
# CMPSC/DS 442: Uninformed Search
############################################################

student_name = "Ethan Reynolds"

############################################################
# Imports
############################################################

# Include your imports here, if any are used.
import math
import random
import copy
from collections import deque

############################################################
# Section 1: N-Queens
############################################################

def num_placements_entire(n):
    sq = n*n
    num = int(math.factorial(sq)/(math.factorial(sq-n) * math.factorial(n)))
    return num

def num_placements_one_in_row(n):
    num = n ** n
    return num

def n_queens_valid(board):
    for var in range(len(board)):
        left = board[var]
        middle = board[var]
        right = board[var]
        for compare in range(var + 1, len(board)):
            left -= 1
            right += 1
            if board[compare] == middle:
                return False
            if left >= 0 and board[compare] == left:
                return False
            if right < len(board) and board[compare] == right:
                return False
    return True

def n_queens_helper(n, board):
    row = len(board)
    if row == n:
        yield board.copy()
    else:
        for col in range(n):
            trunum = True
            for r in range(row):
                if col == board[r]:
                    trunum = False
                if abs(col - board[r]) == (row - r):
                    trunum = False
            if trunum == True:
                board.append(col)
                yield from n_queens_helper(n, board)
                board.pop()

def n_queens_solutions(n):
    yield from n_queens_helper(n, [])

'''
print(num_placements_entire(4))
print(num_placements_one_in_row(4))
print(n_queens_valid([0, 3]))
print(list(n_queens_solutions(6)))
'''

############################################################
# Section 2: Lights Out
############################################################

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

############################################################
# Section 3: Linear Disk Movement
############################################################

def find_children(state, length):
    disks = set(state)
    for pos in state:
        if pos + 1 < length and pos + 1 not in disks:
            new = list(state)
            new.remove(pos)
            new.append(pos + 1)
            new.sort()
            yield tuple(new), (pos, pos + 1)
        if pos - 1 >= 0 and pos - 1 not in disks:
            new = list(state)
            new.remove(pos)
            new.append(pos - 1)
            new.sort()
            yield tuple(new), (pos, pos - 1)
        if pos + 2 < length and pos + 2 not in disks and pos + 1 in disks:
            new = list(state)
            new.remove(pos)
            new.append(pos + 2)
            new.sort()
            yield tuple(new), (pos, pos + 2)
        if pos - 2 >= 0 and pos - 2 not in disks and pos - 1 in disks:
            new = list(state)
            new.remove(pos)
            new.append(pos - 2)
            new.sort()
            yield tuple(new), (pos, pos - 2)

def solve_identical_disks(length, n):
    start = tuple(range(n))
    goal = tuple(range(length - n, length))
    if start == goal:
        return []
    frontier = deque()
    visited = set()
    frontier.append((start, []))
    visited.add(start)
    while len(frontier) != 0:
        temp = frontier.popleft()
        state, path = temp
        for child, move in find_children(state, length):
            if child not in visited:
                newpath = path.copy()
                newpath.append(move)
                if child == goal:
                    return newpath
                visited.add(child)
                frontier.append((child, newpath))
    return None

#print(solve_identical_disks(6, 3))

def find_children_distinct(state, length):
    for i, disk in enumerate(state):
        if i + 1 < length and state[i + 1] == -1:
            new = list(state)
            new[i + 1] = new[i]
            new[i] = -1
            yield tuple(new), (i, i + 1)
        if i - 1 >= 0 and state[i - 1] == -1:
            new = list(state)
            new[i - 1] = new[i]
            new[i] = -1
            yield tuple(new), (i, i - 1)
        if i + 2 < length and state[i + 2] == -1 and state[i + 1] != -1:
            new = list(state)
            new[i + 2] = new[i]
            new[i] = -1
            yield tuple(new), (i, i + 2)
        if i - 2 >= 0 and state[i - 2] == -1 and state[i - 1] != -1:
            new = list(state)
            new[i - 2] = new[i]
            new[i] = -1
            yield tuple(new), (i, i - 2)

def solve_distinct_disks(length, n):
    s = list(range(n))
    for i in range(length - n):
        s.append(-1)
    start = tuple(s)
    g = []
    for i in range(length - n):
        g.append(-1)
    goal = tuple(g + list(range(n))[::-1])
    if start == goal:
        return []
    frontier = deque()
    visited = set()
    frontier.append((start, []))
    visited.add(start)
    while len(frontier) != 0:
        temp = frontier.popleft()
        state, path = temp
        for child, move in find_children_distinct(state, length):
            if child not in visited:
                newpath = path.copy()
                newpath.append(move)
                if child == goal:
                    return newpath
                visited.add(child)
                frontier.append((child, newpath))
    return None

#print(solve_distinct_disks(5, 3))